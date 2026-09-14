"""Roda o dataset inteiro sobre UM modelo e grava execuções + métricas (fase F6).

    pfc-avaliar --modelo qwen3:4b                    # 310 consultas, 1 repetição
    pfc-avaliar --modelo qwen3:4b --repeticoes 3     # protocolo completo
    pfc-avaliar --modelo qwen3:4b --ids P01,N04,GT001
    pfc-avaliar --modelo qwen3:4b --origem P,N --limite 20   # rodada-fumaça
    pfc-avaliar --modelo qwen3:4b --sem-sql          # só tradução (sem PostGIS)

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

from pfc_busca import agent, db, schema, tools
from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.dataset_builder import CAMINHO_SAIDA as CAMINHO_DATASET
from pfc_busca.evaluation.dataset_builder import carregar_dataset
from pfc_busca.evaluation.relative_time import resolver_gabarito

RAIZ_REPO = Path(__file__).resolve().parents[3]
DIR_RESULTADOS = RAIZ_REPO / "results"
FALHAS_INFRA_PARA_ABORTAR = 3
CONSULTA_AQUECIMENTO = "cartas de São Paulo"


def slug(modelo: str) -> str:
    return modelo.replace("/", "-").replace(":", "-")


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
    return {
        "modelo": args.modelo,
        "modelo_info": _info_modelo(args.modelo, args.base_url),
        "thinking_desativado": tradutor.thinking_desativado,
        "configuracao": {"temperature": 0, "num_predict": agent.MAX_TOKENS_SAIDA,
                         "timeout_s": agent.TIMEOUT_S, "keep_alive": agent.KEEP_ALIVE,
                         "zero_shot": True, "few_shot": False, "dicionario_normalizacao": False},
        "hoje": args.hoje.isoformat(),
        "repeticoes": args.repeticoes,
        "executar_sql": executar_sql,
        "dataset": {"caminho": str(CAMINHO_DATASET.relative_to(RAIZ_REPO)),
                    "sha256": _hash_arquivo(CAMINHO_DATASET)},
        "ferramenta_sha256": hashlib.sha256(
            json.dumps(schema.FERRAMENTA_BUSCAR_CATALOGO, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest(),
        "software": {
            "python": platform.python_version(),
            "ollama_servidor": agent.versao_servidor(args.base_url),
            "ollama_python": versao_pacote("ollama"),
            "langchain_core": versao_pacote("langchain-core"),
            "langchain_ollama": versao_pacote("langchain-ollama"),
            "so": platform.platform(),
        },
        "hardware": {"gpu": _gpu(), "maquina": platform.node()},
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
        "notas": caso.get("notas", ""),
        "modelo": tradutor.modelo, "repeticao": repeticao, "hoje": hoje.isoformat(),
        "esperado": caso["esperado"],
        "esperado_resolvido": resolver_gabarito(caso["esperado"], hoje),
        "predito": traducao.predito, "chamou_ferramenta": traducao.chamou_ferramenta,
        "tool_calls": traducao.tool_calls, "texto_resposta": traducao.texto_resposta,
        "latencia_llm_ms": traducao.latencia_llm_ms, "latencia_tool_ms": latencia_tool,
        "latencia_total_ms": total if traducao.latencia_llm_ms is not None else None,
        "tokens_prompt": traducao.tokens_prompt, "tokens_saida": traducao.tokens_saida,
        "duracoes_ollama_ms": traducao.duracoes_ollama_ms,
        "erro": traducao.erro, "classe_erro": traducao.classe_erro,
        "busca": busca,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }


def _glifo(linha: dict) -> Text:
    if metrics.erro_de_infra(linha):
        return Text("×", style="red")
    aval = metrics.avaliar_caso(linha["esperado_resolvido"], linha["predito"], linha["espera_tool_call"])
    return Text("✓", style="green") if aval.correto else Text("·", style="yellow")


def rodar(args, console: Console) -> int:
    casos = selecionar(carregar_dataset(), args)
    if not casos:
        console.print("[yellow]nenhuma consulta selecionada[/yellow]")
        return 1

    tradutor = agent.Tradutor(args.modelo, base_url=args.base_url)
    executar_sql = not args.sem_sql and db.disponivel(args.dsn)
    if not args.sem_sql and not executar_sql:
        console.print("[yellow]banco indisponível — rodando só a tradução (SQL não executada)[/yellow]")

    dir_saida = args.saida / slug(args.modelo)
    dir_saida.mkdir(parents=True, exist_ok=True)
    caminho_jsonl = dir_saida / "execucoes.jsonl"
    feitos = ja_executados(caminho_jsonl)

    manifesto = montar_manifesto(args, tradutor, executar_sql)
    (dir_saida / "manifesto.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding="utf-8")

    console.rule(f"[bold]{args.modelo}[/bold]")
    console.print(f"consultas: {len(casos)} × {args.repeticoes} repetição(ões) · já feitas: {len(feitos)} · "
                  f"hoje={args.hoje} · thinking {'desativado' if tradutor.thinking_desativado else 'n/a'} · "
                  f"SQL {'sim' if executar_sql else 'não'}")

    if args.aquecer:
        inicio = time.perf_counter()
        aquecimento = tradutor.traduzir(CONSULTA_AQUECIMENTO, args.hoje)
        console.print(f"aquecimento: {(time.perf_counter() - inicio) * 1000:.0f} ms"
                      + (f" [red](erro: {aquecimento.erro})[/red]" if aquecimento.erro else ""))
        manifesto["aquecimento_ms"] = aquecimento.latencia_llm_ms
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
        for caso, repeticao in pendentes:
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


def resumir(dir_saida: Path, console: Console | None = None) -> dict:
    linhas = carregar_execucoes(dir_saida)
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
             "O": "Ordenação", "A": "Ambíguas/informais"}
    for cat, v in g["por_categoria"].items():
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
    p.add_argument("--modelo", required=True, help="tag do Ollama, ex.: qwen3:4b")
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
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = analisar(argv)
    console = Console(highlight=False)
    if args.so_resumir:
        resumir(args.saida / slug(args.modelo), console)
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
