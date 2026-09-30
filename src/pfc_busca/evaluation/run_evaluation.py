"""Roda o dataset inteiro sobre UM modelo e grava execuções + métricas (fase F6).

    pfc-avaliar --modelo qwen3:4b                    # 310 consultas, 1 repetição
    pfc-avaliar --modelo qwen3:4b --repeticoes 3     # protocolo completo
    pfc-avaliar --modelo qwen3:4b --ids P01,N04,GT001
    pfc-avaliar --modelo qwen3:4b --origem P,N --limite 20   # rodada-fumaça
    pfc-avaliar --modelo qwen3:4b --sem-sql          # só tradução (sem PostGIS)
    pfc-avaliar --provedor groq --modelo qwen/qwen3.8-27b   # resultado paralelo em nuvem
    pfc-avaliar --modelo qwen3:4b --abordagem saida_estruturada   # linha de base (Saída Estruturada)
    pfc-avaliar --modelo phi4:14b --abordagem prototipo           # linha de base (método do protótipo)

Os resultados de cada provedor ficam separados: `results/<modelo>/` (Ollama, local)
e `results/groq-<modelo>/` (Groq, nuvem); as linhas de base com Saída Estruturada, em
`results/se-<modelo>/` e `results/prototipo-<modelo>/`. O resumo é SEMPRE recalculado contra o
gabarito vigente em `data/dataset.json`: uma correção de gabarito não exige rodar
os modelos de novo; uma consulta cujo texto mudou é descartada do resumo.

Saída em `results/<modelo>/`:
    execucoes.jsonl   uma linha por (consulta × repetição); append; retomável
    manifesto.json    versões, tag/digest do modelo, hardware, hash do dataset (RNF4)
    resumo.json       métricas agregadas (geral e por repetição)
    resumo.md         o mesmo, legível

Ordem fixa do dataset, execução sequencial, sem paralelismo. Um erro por
consulta vira linha com `erro`; só uma sequência de falhas de infraestrutura
(servidor caiu) interrompe a rodada — que pode ser retomada com o mesmo
comando.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import date, datetime
from importlib.metadata import version as versao_pacote
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.text import Text

from pfc_busca import abordagens, agent, db, schema, tools
from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.dataset_builder import caminho_dataset, carregar_dataset
from pfc_busca.evaluation.gabarito import resolver_gabarito, resolver_leituras

RAIZ_REPO = Path(__file__).resolve().parents[3]
DIR_RESULTADOS = RAIZ_REPO / "results"
FALHAS_INFRA_PARA_ABORTAR = 3
CONSULTA_AQUECIMENTO = "cartas de São Paulo"


# Nomes, prefixos e fábricas vêm do registro único (pfc_busca.abordagens); uma versão nova entra só lá.
PREFIXO_ABORDAGEM = {a.nome: a.prefixo for a in abordagens.REGISTRO.values()}
ABORDAGENS = list(PREFIXO_ABORDAGEM)
SO_OLLAMA = tuple(a.nome for a in abordagens.REGISTRO.values() if a.so_ollama)


def slug(modelo: str, provedor: str = "ollama", abordagem: str = "tool_calling") -> str:
    base = modelo.replace("/", "-").replace(":", "-")
    base = PREFIXO_ABORDAGEM[abordagem] + base
    return base if provedor == "ollama" else f"{provedor}-{base}"


def _carregar_env() -> None:
    from dotenv import load_dotenv

    load_dotenv(RAIZ_REPO / ".env")
    load_dotenv(RAIZ_REPO.parent / "demo_vc" / ".env")  # chave do Groq usada na demonstração


def criar_tradutor(args, registrar=print):
    return abordagens.criar_tradutor(args.abordagem, args.modelo, provedor=args.provedor,
                                     base_url=args.base_url, registrar=registrar)


# ---------------------------------------------------------------------------
# Manifesto (reprodutibilidade — RNF4)
# ---------------------------------------------------------------------------

def _hash_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def _gpu() -> str | None:
    try:
        saida = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        return saida.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def _vram() -> dict | None:
    """Memória da GPU em uso/livre e utilização no início da sessão (a latência local depende disso)."""
    try:
        saida = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.free,utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10, check=False,
        )
        usada, livre, uso = (int(x.strip()) for x in saida.stdout.strip().splitlines()[0].split(","))
        return {"usada_mib": usada, "livre_mib": livre, "utilizacao_pct": uso}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return None


def _ollama_ps(base_url: str, modelo: str) -> dict | None:
    """Tamanho do modelo carregado e parcela na VRAM (`/api/ps`), medidos depois do aquecimento."""
    import httpx

    try:
        for m in httpx.get(f"{base_url}/api/ps", timeout=5).json().get("models", []):
            if m.get("name") in (modelo, f"{modelo}:latest") or m.get("model") in (modelo, f"{modelo}:latest"):
                total, vram = m.get("size") or 0, m.get("size_vram") or 0
                return {"tamanho_bytes": total, "na_vram_bytes": vram,
                        "fracao_na_gpu": round(vram / total, 3) if total else None,
                        "contexto": m.get("context_length")}
    except (httpx.HTTPError, ValueError):
        return None
    return None


def _descarregar_outros(base_url: str, modelo: str, espera_s: float = 15.0) -> list[str]:
    """Descarrega do Ollama todos os modelos residentes antes da rodada.

    Sem isso, o modelo da rodada anterior (keep_alive) continua ocupando VRAM e o
    modelo seguinte roda com menos camadas na GPU — a latência passaria a depender
    da ordem das rodadas.
    """
    import httpx

    try:
        residentes = [m.get("name") or m.get("model") for m in
                      httpx.get(f"{base_url}/api/ps", timeout=5).json().get("models", [])]
    except (httpx.HTTPError, ValueError):
        return []
    # inclusive o próprio modelo avaliado: a divisão GPU/CPU é decidida no carregamento,
    # então toda rodada começa a frio, com a VRAM que a máquina tem livre
    outros = [m for m in residentes if m]
    for m in outros:
        try:
            httpx.post(f"{base_url}/api/generate", json={"model": m, "keep_alive": 0}, timeout=30)
        except httpx.HTTPError:
            pass
    limite = time.monotonic() + espera_s
    while outros and time.monotonic() < limite:
        try:
            ainda = {x.get("name") or x.get("model") for x in
                     httpx.get(f"{base_url}/api/ps", timeout=5).json().get("models", [])}
        except (httpx.HTTPError, ValueError):
            break
        if not ainda & set(outros):
            break
        time.sleep(0.5)
    return outros


def versao_codigo() -> str | None:
    """Commit do código que executa a rodada: arquivo VERSAO (pacote do Colab) ou git."""
    arquivo = RAIZ_REPO / "VERSAO"
    if arquivo.exists():
        return arquivo.read_text(encoding="utf-8").strip() or None
    try:
        rev = subprocess.run(["git", "-C", str(RAIZ_REPO), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10, check=False).stdout.strip()
        sujo = subprocess.run(["git", "-C", str(RAIZ_REPO), "status", "--porcelain", "--", "src"],
                              capture_output=True, text=True, timeout=10, check=False).stdout.strip()
        return (rev + ("+alteracoes" if sujo else "")) if rev else None
    except (OSError, subprocess.SubprocessError):
        return None


def _para_hash(abordagem: str) -> str:
    # um nome fora do registro (manifesto antigo, ex.: tc3f do desenvolvimento) cai na v1, como sempre caiu:
    # pfc-conferir acusa a divergência em vez de quebrar
    return abordagem if abordagem in abordagens.REGISTRO else "tool_calling"


def hash_prompt(abordagem: str = "tool_calling") -> str:
    return abordagens.hash_prompt(_para_hash(abordagem))


def hash_ferramenta(abordagem: str = "tool_calling") -> str:
    return abordagens.hash_ferramenta(_para_hash(abordagem))


def _info_modelo(modelo: str, base_url: str) -> dict:
    import ollama

    cliente = ollama.Client(host=base_url, timeout=15)
    info: dict = {}
    try:
        show = cliente.show(modelo)
        detalhes = getattr(show, "details", None)
        info["details"] = (detalhes.model_dump() if hasattr(detalhes, "model_dump") else dict(detalhes or {}))
        info["capabilities"] = list(getattr(show, "capabilities", None) or [])
        info["modified_at"] = str(getattr(show, "modified_at", "") or "")
    except Exception as erro:  # noqa: BLE001
        info["erro_show"] = str(erro)[:200]
    try:
        for m in cliente.list().models:
            if m.model == modelo or m.model == f"{modelo}:latest":
                info["digest"] = m.digest
                info["tamanho_bytes"] = m.size
    except Exception as erro:  # noqa: BLE001
        info["erro_list"] = str(erro)[:200]
    return info


def montar_manifesto(args, tradutor: agent.Tradutor, executar_sql: bool) -> dict:
    nuvem = args.provedor != "ollama"
    linha_de_base = args.abordagem != "tool_calling"
    return {
        "modelo": args.modelo,
        "provedor": args.provedor,
        "abordagem": args.abordagem,
        "execucao": "nuvem (resultado paralelo, fora do requisito RNF1)" if nuvem else "local (Ollama)",
        "modelo_info": ({"base_url": tradutor.base_url, "esforco_de_raciocinio": getattr(tradutor, "esforco", None)}
                        if nuvem else _info_modelo(args.modelo, args.base_url)),
        "thinking_desativado": tradutor.thinking_desativado,
        "configuracao": ({**tradutor.descricao(), "timeout_s": agent.TIMEOUT_S, "keep_alive": agent.KEEP_ALIVE}
                         if linha_de_base or hasattr(tradutor, "descricao") else
                         {"temperature": 0, "num_predict": agent.MAX_TOKENS_SAIDA,
                          "timeout_s": agent.TIMEOUT_S, "keep_alive": agent.KEEP_ALIVE,
                          "zero_shot": True, "few_shot": False, "dicionario_normalizacao": False}),
        "hoje": args.hoje.isoformat(),
        "repeticoes": args.repeticoes,
        "executar_sql": executar_sql,
        "dataset": {"caminho": caminho_dataset().relative_to(RAIZ_REPO).as_posix(),
                    "sha256": _hash_arquivo(caminho_dataset())},
        "ferramenta_sha256": hash_ferramenta(args.abordagem),
        "prompt_sha256": hash_prompt(args.abordagem),
        "codigo": versao_codigo(),
        "software": {
            "python": platform.python_version(),
            "ollama_servidor": None if nuvem else agent.versao_servidor(args.base_url),
            "ollama_python": versao_pacote("ollama"),
            "langchain_core": versao_pacote("langchain-core"),
            "langchain_ollama": versao_pacote("langchain-ollama"),
            "langchain_openai": versao_pacote("langchain-openai") if nuvem else None,
            "so": platform.platform(),
        },
        "hardware": ({"gpu": None, "maquina": "servidores do provedor"} if nuvem
                     else {"gpu": _gpu(), "maquina": platform.node()}),
        "intervalo_entre_chamadas_s": args.intervalo,
        "iniciado_em": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

def selecionar(casos: list[dict], args) -> list[dict]:
    sel = casos
    if args.ids:
        ids = {i.strip() for i in args.ids.split(",") if i.strip()}
        sel = [c for c in sel if c["id"] in ids]
    if args.origem:
        origens = {o.strip().upper() for o in args.origem.split(",")}
        sel = [c for c in sel if c["origem"] in origens]
    if args.familias:
        fams = {f.strip().upper() for f in args.familias.split(",")}
        sel = [c for c in sel if c["familia"] in fams]
    if args.limite:
        sel = sel[: args.limite]
    return sel


def ja_executados(caminho_jsonl: Path) -> set[tuple[str, int]]:
    feitos: set[tuple[str, int]] = set()
    if caminho_jsonl.exists():
        for linha in caminho_jsonl.read_text(encoding="utf-8").splitlines():
            if linha.strip():
                d = json.loads(linha)
                feitos.add((d["id"], d["repeticao"]))
    return feitos


def consultas_com_texto_obsoleto(caminho_jsonl: Path) -> list[str]:
    """IDs já executados cujo texto de consulta difere do dataset vigente."""
    if not caminho_jsonl.exists():
        return []
    atuais = {c["id"]: c["consulta"] for c in carregar_dataset()}
    obsoletas = set()
    for linha in caminho_jsonl.read_text(encoding="utf-8").splitlines():
        if linha.strip():
            d = json.loads(linha)
            if atuais.get(d["id"]) != d["consulta"]:
                obsoletas.add(d["id"])
    return sorted(obsoletas)


def executar_caso(tradutor: agent.Tradutor, caso: dict, repeticao: int, hoje: date,
                  executar_sql: bool, dsn: str) -> dict:
    traducao = tradutor.traduzir(caso["consulta"], hoje)
    busca = None
    latencia_tool = None
    if executar_sql and traducao.predito is not None:
        resultado = tools.buscar_catalogo(traducao.predito, dsn)
        latencia_tool = resultado.latencia_ms
        busca = {"executado": resultado.executado, "total": resultado.total,
                 "erro": resultado.erro, "latencia_ms": resultado.latencia_ms}
    total = (traducao.latencia_llm_ms or 0.0) + (latencia_tool or 0.0)
    return {
        "id": caso["id"], "origem": caso["origem"], "familia": caso["familia"],
        "categorias": caso["categorias"], "consulta": caso["consulta"],
        "observacional": caso["observacional"], "espera_tool_call": caso["espera_tool_call"],
        "aceita_nao_chamar": bool(caso.get("aceita_nao_chamar")),
        "notas": caso.get("notas", ""),
        "modelo": tradutor.modelo, "repeticao": repeticao, "hoje": hoje.isoformat(),
        "esperado": caso["esperado"],
        "esperado_resolvido": resolver_gabarito(caso["esperado"], hoje),
        "alternativas": caso.get("alternativas", []),
        "alternativas_resolvidas": resolver_leituras(caso, hoje)[1:],
        "predito": traducao.predito, "chamou_ferramenta": traducao.chamou_ferramenta,
        "tool_calls": traducao.tool_calls, "texto_resposta": traducao.texto_resposta,
        "latencia_llm_ms": traducao.latencia_llm_ms, "latencia_tool_ms": latencia_tool,
        "latencia_total_ms": total if traducao.latencia_llm_ms is not None else None,
        "tokens_prompt": traducao.tokens_prompt, "tokens_saida": traducao.tokens_saida,
        "duracoes_ollama_ms": traducao.duracoes_ollama_ms,
        "erro": traducao.erro, "classe_erro": traducao.classe_erro,
        **({"extras": traducao.extras} if getattr(traducao, "extras", None) else {}),
        "busca": busca,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def _glifo(linha: dict) -> Text:
    if metrics.erro_de_infra(linha):
        return Text("×", style="red")
    aval = metrics.avaliar_linha(linha)
    return Text("✓", style="green") if aval.correto else Text("·", style="yellow")


def rodar(args, console: Console) -> int:
    casos = selecionar(carregar_dataset(), args)
    if not casos:
        console.print("[yellow]nenhuma consulta selecionada[/yellow]")
        return 1

    tradutor = criar_tradutor(args, registrar=console.print)
    executar_sql = not args.sem_sql and db.disponivel(args.dsn)
    if not args.sem_sql and not executar_sql:
        console.print("[yellow]banco indisponível — rodando só a tradução (SQL não executada)[/yellow]")

    dir_saida = args.saida / slug(args.modelo, args.provedor, args.abordagem)
    dir_saida.mkdir(parents=True, exist_ok=True)
    caminho_jsonl = dir_saida / "execucoes.jsonl"
    feitos = ja_executados(caminho_jsonl)
    obsoletas = consultas_com_texto_obsoleto(caminho_jsonl)
    if obsoletas:
        console.print(f"[red]{len(obsoletas)} consulta(s) já executada(s) em {dir_saida} têm texto diferente do dataset "
                      f"vigente (ex.: {', '.join(obsoletas[:5])}): a rodada foi feita com outra versão do dataset. "
                      "Retomar reaproveitaria respostas a consultas antigas. Use outra --saida.[/red]")
        return 3

    manifesto = montar_manifesto(args, tradutor, executar_sql)
    anterior = (json.loads((dir_saida / "manifesto.json").read_text(encoding="utf-8"))
                if (dir_saida / "manifesto.json").exists() else None)
    if anterior and feitos:
        divergentes = [k for k in ("ferramenta_sha256", "prompt_sha256", "hoje", "provedor", "abordagem")
                       if anterior.get(k) is not None and anterior.get(k) != manifesto.get(k)]
        if divergentes and not args.forcar_retomada:
            console.print(f"[red]a rodada existente em {dir_saida} foi feita com outro(s) {', '.join(divergentes)}; "
                          "retomar misturaria condições. Use outra --saida (ou --forcar-retomada).[/red]")
            return 3
    sessoes = list((anterior or {}).get("sessoes") or [])
    if anterior and not sessoes and feitos:  # manifesto antigo, sem histórico: preserva a sessão anterior
        sessoes.append({k: anterior.get(k) for k in ("iniciado_em", "encerrado_em", "hardware") if anterior.get(k)})
    descarregados = _descarregar_outros(args.base_url, args.modelo) if args.provedor == "ollama" else []
    if descarregados:
        console.print(f"descarregados do Ollama antes da rodada: {', '.join(descarregados)}")
    sessao = {"iniciado_em": manifesto["iniciado_em"], "ja_feitas_no_inicio": len(feitos),
              "descarregados": descarregados,
              "vram_inicio": None if args.provedor != "ollama" else _vram()}
    sessoes.append(sessao)
    manifesto["sessoes"] = sessoes
    (dir_saida / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    console.rule(f"[bold]{args.modelo}[/bold] · {args.provedor}"
                 + ("" if args.abordagem == "tool_calling" else f" · linha de base: {args.abordagem}"))
    console.print(f"consultas: {len(casos)} × {args.repeticoes} repetição(ões) · já feitas: {len(feitos)} · "
                  f"hoje={args.hoje} · thinking {'desativado' if tradutor.thinking_desativado else 'n/a'} · "
                  f"SQL {'sim' if executar_sql else 'não'}")

    if args.aquecer:
        inicio = time.perf_counter()
        aquecimento = tradutor.traduzir(CONSULTA_AQUECIMENTO, args.hoje)
        console.print(f"aquecimento: {(time.perf_counter() - inicio) * 1000:.0f} ms"
                      + (f" [red](erro: {aquecimento.erro})[/red]" if aquecimento.erro else ""))
        manifesto["aquecimento_ms"] = aquecimento.latencia_llm_ms
        sessao["aquecimento_ms"] = aquecimento.latencia_llm_ms
        if args.provedor == "ollama":
            sessao["ollama_ps"] = _ollama_ps(args.base_url, args.modelo)
            if sessao["ollama_ps"]:
                console.print(f"modelo na GPU: {100 * (sessao['ollama_ps']['fracao_na_gpu'] or 0):.0f}% · "
                              f"VRAM livre no início: {(sessao['vram_inicio'] or {}).get('livre_mib', '?')} MiB")
        if aquecimento.classe_erro == "indisponivel":
            console.print(f"[red]{aquecimento.erro}[/red]")
            return 2

    pendentes = [(c, r) for r in range(1, args.repeticoes + 1) for c in casos if (c["id"], r) not in feitos]
    falhas_infra_seguidas = 0
    with caminho_jsonl.open("a", encoding="utf-8") as arquivo, Progress(
        TextColumn("[progress.description]{task.description}"), BarColumn(), MofNCompleteColumn(),
        TimeElapsedColumn(), TimeRemainingColumn(), console=console,
    ) as progresso:
        tarefa = progresso.add_task("avaliando", total=len(pendentes))
        for i, (caso, repeticao) in enumerate(pendentes):
            if i and args.intervalo:
                time.sleep(args.intervalo)
            linha = executar_caso(tradutor, caso, repeticao, args.hoje, executar_sql, args.dsn)
            arquivo.write(json.dumps(linha, ensure_ascii=False) + "\n")
            arquivo.flush()
            if linha["classe_erro"] in ("indisponivel", "timeout"):
                falhas_infra_seguidas += 1
            else:
                falhas_infra_seguidas = 0
            detalhe = Text.assemble(
                _glifo(linha), f" r{repeticao} {linha['id']:<6} ",
                (f"{linha['latencia_llm_ms']:6.0f} ms " if linha["latencia_llm_ms"] else "      -  "),
                (Text(f"{linha['classe_erro']}: {linha['erro']}", style="dim") if linha["erro"] else ""),
            )
            progresso.console.print(detalhe)
            progresso.advance(tarefa)
            if falhas_infra_seguidas >= FALHAS_INFRA_PARA_ABORTAR:
                console.print(f"[red]{falhas_infra_seguidas} falhas de infraestrutura seguidas — "
                              "interrompendo. Rode o mesmo comando para retomar.[/red]")
                break

    manifesto["encerrado_em"] = datetime.now().isoformat(timespec="seconds")
    sessao["encerrado_em"] = manifesto["encerrado_em"]
    sessao["executadas"] = len(ja_executados(caminho_jsonl)) - len(feitos)
    (dir_saida / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")
    resumir(dir_saida, console)
    return 0


# ---------------------------------------------------------------------------
# Resumo
# ---------------------------------------------------------------------------

def carregar_execucoes(dir_saida: Path) -> list[dict]:
    caminho = dir_saida / "execucoes.jsonl"
    if not caminho.exists():
        return []
    return [json.loads(lin) for lin in caminho.read_text(encoding="utf-8").splitlines() if lin.strip()]


def dataset_da_rodada(dir_saida: Path) -> Path:
    """Dataset em que a rodada foi feita (manifesto); sem manifesto, o dataset ativo."""
    try:
        manifesto = json.loads((dir_saida / "manifesto.json").read_text(encoding="utf-8"))
        caminho = RAIZ_REPO / manifesto["dataset"]["caminho"]
        if caminho.exists():
            return caminho
    except (OSError, KeyError, TypeError, ValueError):
        pass
    return caminho_dataset()


def repontuar(linhas: list[dict], dataset: Path | None = None) -> tuple[list[dict], list[str]]:
    """Reaplica o gabarito VIGENTE do dataset (padrão: `data/dataset.json`) a execuções já feitas.

    Cada linha mantém o que o modelo respondeu (`predito`) e a data de referência
    da execução (`hoje`); gabarito, leituras alternativas, categorias e condição de
    observacional vêm do dataset atual. Linhas cujo id não existe mais, ou cujo texto
    de consulta mudou, são descartadas (e listadas).
    """
    atuais = {c["id"]: c for c in carregar_dataset(dataset)}
    validas, descartadas = [], []
    for lin in linhas:
        caso = atuais.get(lin["id"])
        if caso is None or caso["consulta"] != lin["consulta"]:
            descartadas.append(lin["id"])
            continue
        hoje = date.fromisoformat(lin["hoje"])
        leituras = resolver_leituras(caso, hoje)
        validas.append({**lin,
                        "esperado": caso["esperado"], "alternativas": caso["alternativas"],
                        "esperado_resolvido": leituras[0], "alternativas_resolvidas": leituras[1:],
                        "espera_tool_call": caso["espera_tool_call"], "observacional": caso["observacional"],
                        "aceita_nao_chamar": bool(caso.get("aceita_nao_chamar")),
                        "categorias": caso["categorias"], "origem": caso["origem"], "familia": caso["familia"]})
    return validas, descartadas


def resumir(dir_saida: Path, console: Console | None = None) -> dict:
    dataset = dataset_da_rodada(dir_saida)
    linhas, descartadas = repontuar(carregar_execucoes(dir_saida), dataset)
    if not linhas:
        return {}
    repeticoes = sorted({lin["repeticao"] for lin in linhas})
    resumo = {
        "modelo": linhas[0]["modelo"],
        "n_execucoes": len(linhas),
        "repeticoes": repeticoes,
        "geral": metrics.agregar(linhas),
        "por_repeticao": {str(r): metrics.agregar([lin for lin in linhas if lin["repeticao"] == r]) for r in repeticoes},
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "dataset_na_pontuacao": dataset.relative_to(RAIZ_REPO).as_posix(),
        "dataset_sha256_na_pontuacao": _hash_arquivo(dataset),
        "linhas_descartadas_texto_alterado": sorted(set(descartadas)),
    }
    (dir_saida / "resumo.json").write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    (dir_saida / "resumo.md").write_text(resumo_markdown(resumo), encoding="utf-8")
    if console:
        g = resumo["geral"]
        console.print(
            f"\n[bold]{resumo['modelo']}[/bold] · {g['n_consultas']} consultas · "
            f"acurácia {g['acuracia']:.1%} · F1 ponderado {g['f1_ponderado']:.3f} · "
            f"latência mediana {g['latencia_llm_ms'].get('mediana', 0):.0f} ms · "
            f"erros de infra {g['diagnosticos']['chamadas_com_erro']} · fora do schema {g['diagnosticos']['respostas_fora_do_schema']}"
        )
        console.print(f"→ {dir_saida / 'resumo.md'}")
    return resumo


def _pct(v: float | None) -> str:
    return "—" if v is None else f"{100 * v:.1f}%"


def _f(v: float | None, casas: int = 3) -> str:
    return "—" if v is None else f"{v:.{casas}f}"


def resumo_markdown(resumo: dict) -> str:
    g = resumo["geral"]
    out = [f"# {resumo['modelo']} — resumo da avaliação", "",
           f"{resumo['n_execucoes']} execuções · repetições {resumo['repeticoes']} · "
           f"gerado em {resumo['gerado_em']}", "",
           "## Geral (métricas principais)", "",
           "| Métrica | Valor |", "|---|---|",
           f"| Consultas | {g['n_consultas']} |",
           f"| Acurácia por consulta | {_pct(g['acuracia'])} |",
           f"| Precisão ponderada | {_f(g['precisao_ponderada'])} |",
           f"| Recall ponderado | {_f(g['recall_ponderado'])} |",
           f"| F1 ponderado | {_f(g['f1_ponderado'])} |",
           f"| F1 macro | {_f(g['f1_macro'])} |",
           f"| Micro P / R / F1 | {_f(g['micro']['precisao'])} / {_f(g['micro']['recall'])} / {_f(g['micro']['f1'])} |",
           ""]
    lat = g["latencia_llm_ms"]
    if lat:
        out += ["## Latência do LLM (ms)", "",
                "| n | mín | mediana | média | p95 | máx | desvio |", "|---|---|---|---|---|---|---|",
                f"| {lat['n']} | {lat['min']:.0f} | {lat['mediana']:.0f} | {lat['media']:.0f} | "
                f"{lat['p95']:.0f} | {lat['max']:.0f} | {lat['desvio']:.0f} |", ""]
    lt = g["latencia_tool_ms"]
    if lt:
        out += [f"Latência da ferramenta (SQL): mediana {lt['mediana']:.1f} ms, máx {lt['max']:.1f} ms.", ""]
    out += ["## Por campo", "", "| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |",
            "|---|---|---|---|---|---|---|---|"]
    for campo in schema.CAMPOS:
        c = g["por_campo"][campo]
        out.append(f"| {campo} | {c['ocorrencias']} | {c['tp']} | {c['fp']} | {c['fn']} | "
                   f"{_f(c['precisao'])} | {_f(c['recall'])} | {_f(c['f1'])} |")
    out += ["", "## Por categoria", "", "| Categoria | n | Acurácia | F1 ponderado |", "|---|---|---|---|"]
    nomes = {"S": "Simples", "C": "Compostas", "M": "Código MI/INOM", "T": "Tempo relativo",
             "O": "Ordenação", "A": "Ambíguas/informais", "F": "Fora do domínio", "E": "Subespecificadas"}
    for cat, v in g["por_categoria"].items():
        if not v["n"]:
            continue
        out.append(f"| {nomes[cat]} | {v['n']} | {_pct(v['acuracia'])} | {_f(v['f1_ponderado'])} |")
    out += ["", "## Por origem", "", "| Origem | n | Acurácia |", "|---|---|---|"]
    for o, v in g["por_origem"].items():
        out.append(f"| {o} | {v['n']} | {_pct(v['acuracia'])} |")
    d = g["diagnosticos"]
    out += ["", "## Diagnósticos", "",
            f"- Tipos de erro: {d['tipos_erro']}",
            f"- Campos fora do schema: {d['campos_fora_do_schema']}",
            f"- IoU médio de períodos: { {k: round(v, 3) for k, v in d['iou_periodos_medio'].items()} }",
            f"- Chamadas com erro de infraestrutura: {d['chamadas_com_erro']} {d['classes_de_erro']}",
            f"- Respostas do modelo fora do schema da ferramenta: {d['respostas_fora_do_schema']} {d['classes_fora_do_schema']}",
            f"- Não chamou a ferramenta quando devia: {d['nao_chamou_quando_devia']}", ""]
    obs = g["observacionais"]
    out += ["## Observacionais (fora das métricas principais)", "",
            f"{obs['n']} casos · acurácia {_pct(obs['acuracia'])} · chamou sem dever: {obs['chamou_sem_dever']}", ""]
    if len(resumo["repeticoes"]) > 1:
        out += ["## Por repetição", "", "| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |", "|---|---|---|---|"]
        for r, v in resumo["por_repeticao"].items():
            out.append(f"| {r} | {_pct(v['acuracia'])} | {_f(v['f1_ponderado'])} | "
                       f"{v['latencia_llm_ms'].get('mediana', 0):.0f} |")
        out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def analisar(argv: list[str] | None = None):
    p = argparse.ArgumentParser(description="Avalia um modelo sobre o dataset do PFC.")
    p.add_argument("--modelo", required=True, help="tag do Ollama (ex.: qwen3:4b) ou id do Groq")
    p.add_argument("--provedor", choices=["ollama", "groq"], default="ollama",
                   help="ollama = local (configuração avaliada); groq = nuvem (resultado paralelo)")
    p.add_argument("--abordagem", choices=ABORDAGENS, default="tool_calling",
                   help="abordagem do registro (lista completa: pfc abordagens). tool_calling = solução do Cap. 4; "
                        "saida_estruturada e prototipo = linhas de base; *_v2 e *_v3 = especificações dos lotes de "
                        f"validação; {abordagens.RECOMENDADA} = a recomendada. Só no Ollama: {', '.join(SO_OLLAMA)}")
    p.add_argument("--intervalo", type=float, default=None,
                   help="segundos entre chamadas (padrão: 0 no Ollama, 11 no Groq por causa do limite por minuto)")
    p.add_argument("--dataset", type=Path, help="dataset alternativo (ex.: data/lote_validacao.json); "
                   "equivale a definir PFC_DATASET")
    p.add_argument("--repeticoes", type=int, default=1)
    p.add_argument("--hoje", type=date.fromisoformat, default=date.today(),
                   help="data de referência (ISO) injetada no prompt e usada no gabarito")
    p.add_argument("--ids", help="lista de IDs separados por vírgula")
    p.add_argument("--origem", help="P,N,G")
    p.add_argument("--familias", help="GS,GC,GM,GT,GO,GA,GP,GF,P,N")
    p.add_argument("--limite", type=int)
    p.add_argument("--sem-sql", action="store_true", help="não executar a busca no PostGIS")
    p.add_argument("--sem-aquecer", dest="aquecer", action="store_false")
    p.add_argument("--saida", type=Path, default=DIR_RESULTADOS)
    p.add_argument("--base-url", default=agent.BASE_URL_PADRAO)
    p.add_argument("--dsn", default=db.DSN_PADRAO)
    p.add_argument("--so-resumir", action="store_true", help="recalcula resumo.json/md sem rodar nada")
    p.add_argument("--forcar-retomada", action="store_true",
                   help="retoma mesmo que prompt/ferramenta/data da rodada existente sejam outros (não recomendado)")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = analisar(argv)
    if args.dataset:
        import os

        os.environ["PFC_DATASET"] = str(args.dataset)
    if args.intervalo is None:
        args.intervalo = 11.0 if args.provedor == "groq" else 0.0
    if args.provedor == "groq":
        args.sem_sql = True  # a nuvem só traduz; a demonstração ponta a ponta é local
        if args.abordagem in SO_OLLAMA:
            print(f"a abordagem {args.abordagem} roda só no Ollama")
            return 2
    _carregar_env()
    console = Console(highlight=False)
    if args.so_resumir:
        resumir(args.saida / slug(args.modelo, args.provedor, args.abordagem), console)
        return 0
    try:
        return rodar(args, console)
    except agent.ModeloIndisponivel as erro:
        console.print(f"[red]{erro}[/red]")
        return 2
    except KeyboardInterrupt:
        console.print("\n[yellow]interrompido — rode o mesmo comando para retomar[/yellow]")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
