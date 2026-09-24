"""Consolida `results/<modelo>/` de vários modelos nas tabelas e figuras do Cap. 5.

    pfc-relatorio                              # todos os modelos em results/
    pfc-relatorio --modelos qwen3:4b,gemma4:e4b-it-qat --saida results/consolidado

Produz em `results/consolidado/`:
    comparativo.md                 tudo, legível
    tab_comparativo.tex            Tabela "Comparativo de desempenho entre os modelos"
    tab_por_categoria.tex          Tabela "F1 por categoria de consulta e por modelo"
    tab_por_campo.tex              Tabela "F1 por campo do schema"
    tab_latencia.tex               estatísticas de latência por modelo
    fig_latencia_boxplot.pdf/.png  Figura "Distribuição de latência por modelo"
    fig_f1_por_campo.pdf/.png      barras agrupadas
    fig_acuracia_por_categoria.pdf/.png
    erros_representativos.md       amostra de falhas por tipo, para a análise de erros
    estatistica.md                 IC de Wilson (acurácia) e McNemar pareado entre modelos

Nada aqui interpreta resultado: só organiza. A interpretação é o texto do Cap. 5.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

from pfc_busca import schema
from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.run_evaluation import (
    DIR_RESULTADOS,
    carregar_execucoes,
    repontuar,
    resumir,
    slug,
)

ROTULOS = {
    "qwen3:4b-instruct-2507-q4_K_M": "Qwen 3 4B",
    "qwen3:4b": "Qwen 3 4B (build com thinking — descartado)",
    "gemma4:e4b-it-qat": "Gemma 4 E4B",
    "gemma4:e2b-it-qat": "Gemma 4 E2B",
    "mistral-nemo:12b": "Mistral Nemo 12B",
    "qwen/qwen3.8-27b": "Qwen 3.8 27B (Groq)",
    "openai/gpt-oss-20b": "GPT-OSS 20B (Groq)",
    "openai/gpt-oss-120b": "GPT-OSS 120B (Groq)",
}
# chave curta de cada modelo nas macros \res{rodada}{modelo}{medida} usadas na prosa do Cap. 5
CHAVES = {
    "qwen3:4b-instruct-2507-q4_K_M": "qwen", "gemma4:e4b-it-qat": "e4b", "gemma4:e2b-it-qat": "e2b",
    "mistral-nemo:12b": "mistral", "qwen/qwen3.8-27b": "qwen38", "openai/gpt-oss-20b": "gptoss20",
    "openai/gpt-oss-120b": "gptoss120",
}
SUFIXO = ""   # ex.: "_groq" — distingue rótulos e arquivos do resultado paralelo
TITULO = ""   # ex.: " --- resultado paralelo em nuvem (Groq)"
NOMES_CATEGORIA = {"S": "Simples", "C": "Compostas", "M": "Com código MI/INOM",
                   "T": "Com referência temporal relativa", "O": "Com ordenação",
                   "A": "Ambíguas / variações ortográficas", "F": "Fora do domínio (recusa)"}
CATEGORIA_CURTA = {"S": "Simples", "C": "Compostas", "M": "Código\nMI/INOM", "T": "Tempo\nrelativo",
                   "O": "Ordenação", "A": "Ambíguas /\ninformais", "F": "Fora do\ndomínio"}
CATEGORIA_TABELA = {"S": "Simples", "C": "Compostas", "M": "Código MI/INOM", "T": "Tempo relativo",
                    "O": "Ordenação", "A": "Ambíguas/informais", "F": "Fora do domínio"}
# F1 não se aplica à categoria F (gabarito sem campos): ela aparece só nas visões de acurácia.
CATS_F1 = ["S", "C", "M", "T", "O", "A"]
CATS_ACC = ["S", "C", "M", "T", "O", "A", "F"]


def rotulo(modelo: str) -> str:
    return ROTULOS.get(modelo, modelo)


def _tex(texto: str) -> str:
    return (texto.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
            .replace("#", r"\#").replace("—", "---"))


def _pct(v: float | None) -> str:
    return "---" if v is None else f"{100 * v:.1f}".replace(".", ",") + "\\%"


def _pct_md(v: float | None) -> str:
    return "—" if v is None else f"{100 * v:.1f}%"


def _f(v: float | None, casas: int = 3) -> str:
    return "---" if v is None else f"{v:.{casas}f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Estatística
# ---------------------------------------------------------------------------

def wilson(acertos: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Intervalo de confiança de Wilson (95%) para uma proporção."""
    if n == 0:
        return (0.0, 0.0)
    p = acertos / n
    denom = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / denom
    meio = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (max(0.0, centro - meio), min(1.0, centro + meio))


def mcnemar_exato(b: int, c: int) -> float:
    """p-valor bicaudal exato (binomial) para pares discordantes b e c."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    cauda = sum(math.comb(n, i) for i in range(0, k + 1)) / 2 ** n
    return min(1.0, 2 * cauda)


def correcao_por_consulta(linhas: list[dict]) -> dict[tuple[str, int], bool]:
    return {
        (lin["id"], lin["repeticao"]): metrics.avaliar_linha(lin).correto
        for lin in linhas if not lin.get("observacional")
    }


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

def carregar_modelos(dir_resultados: Path, modelos: list[str] | None) -> dict[str, dict]:
    """{modelo: {"resumo": ..., "linhas": [...]}} para cada diretório com execucoes.jsonl.

    O resumo é SEMPRE recalculado (`resumir`) contra o gabarito vigente, e não lido
    de um resumo.json possivelmente anterior a uma correção do gabarito.
    """
    saida = {}
    if not dir_resultados.is_dir():
        return saida
    for pasta in sorted(dir_resultados.iterdir()):
        if not pasta.is_dir() or not (pasta / "execucoes.jsonl").exists():
            continue
        r = resumir(pasta)
        if not r:
            continue
        modelo = r["modelo"]
        if modelos and modelo not in modelos:
            continue
        saida[modelo] = {"resumo": r, "linhas": repontuar(carregar_execucoes(pasta))[0],
                         "manifesto": json.loads((pasta / "manifesto.json").read_text(encoding="utf-8"))
                         if (pasta / "manifesto.json").exists() else {}}
    if modelos:  # preserva a ordem pedida
        saida = {m: saida[m] for m in modelos if m in saida}
    return saida


# ---------------------------------------------------------------------------
# Tabelas LaTeX (mesmos rótulos/labels do cap05-resultados.tex)
# ---------------------------------------------------------------------------

def ajustar_largura(tex: str) -> str:
    """Envolve cada tabular em \\ajustartabela{...}: reduz à largura do texto só se não couber."""
    tex = tex.replace("\\begin{tabular}", "\\ajustartabela{%\n\\begin{tabular}")
    return tex.replace("\\end{tabular}", "\\end{tabular}}")


def tab_comparativo(dados: dict[str, dict]) -> str:
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{Comparativo de desempenho entre os modelos avaliados{TITULO}}}",
              rf"\label{{tab:resultados_comparativo{SUFIXO}}}", r"\small",
              r"\begin{tabular}{|l|c|c|c|c|c|c|}", r"\hline",
              r"\textbf{Modelo} & \textbf{Acurácia} & \textbf{IC 95\%} & \textbf{Precisão} & \textbf{Recall} & \textbf{F1} & \textbf{Lat. med. (ms)} \\",
              r"\hline"]
    for modelo, d in dados.items():
        g = d["resumo"]["geral"]
        corr = correcao_por_consulta(d["linhas"])
        lo, hi = wilson(sum(corr.values()), len(corr))
        linhas.append(f"{_tex(rotulo(modelo))} & {_pct(g['acuracia'])} & {_pct(lo)}--{_pct(hi)} & "
                      f"{_f(g['precisao_ponderada'])} & {_f(g['recall_ponderado'])} & {_f(g['f1_ponderado'])} & "
                      f"{g['latencia_llm_ms'].get('mediana', 0):.0f} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. IC 95\%: intervalo de confiança de Wilson para a acurácia. Precisão, \textit{recall} e F1 ponderados pela frequência de cada campo no gabarito. Latência mediana da chamada de tradução, no ambiente de cada rodada.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_por_categoria(dados: dict[str, dict]) -> str:
    cols = "|l|" + "c|" * len(dados)
    cab = " & ".join(rf"\textbf{{{_tex(rotulo(m))}}}" for m in dados)
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{F1-\textit{{score}} por categoria de consulta e por modelo{TITULO}}}",
              rf"\label{{tab:resultados_por_categoria{SUFIXO}}}", r"\small",
              rf"\begin{{tabular}}{{{cols}}}", r"\hline",
              rf"\textbf{{Categoria}} & {cab} \\", r"\hline"]
    for cat in CATS_F1:
        vals = " & ".join(_f(d["resumo"]["geral"]["por_categoria"][cat]["f1_ponderado"]) for d in dados.values())
        n = next(iter(dados.values()))["resumo"]["geral"]["por_categoria"][cat]["n_consultas"]
        linhas.append(f"{CATEGORIA_TABELA[cat]} (n={n}) & {vals} \\\\")
    linhas.append(r"\hline")
    vals = " & ".join(_f(d["resumo"]["geral"]["f1_ponderado"]) for d in dados.values())
    linhas.append(rf"\textbf{{Média ponderada}} & {vals} \\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. Uma consulta pode pertencer a mais de uma categoria; n = consultas distintas da categoria nas métricas principais (cada uma pontuada em todas as repetições). As consultas fora do domínio (categoria F), cujo gabarito é não chamar a ferramenta, não têm campos e aparecem na Figura de acurácia por categoria.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_por_campo(dados: dict[str, dict]) -> str:
    cols = "|l|c|" + "c|" * len(dados)
    cab = " & ".join(rf"\textbf{{{_tex(rotulo(m))}}}" for m in dados)
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{F1-\textit{{score}} por campo do \textit{{schema}} de busca, por modelo{TITULO}}}",
              rf"\label{{tab:resultados_por_campo{SUFIXO}}}", r"\small",
              rf"\begin{{tabular}}{{{cols}}}", r"\hline",
              rf"\textbf{{Campo}} & \textbf{{Ocorr.}} & {cab} \\", r"\hline"]
    primeiro = next(iter(dados.values()))["resumo"]["geral"]["por_campo"]
    for campo in schema.CAMPOS:
        vals = " & ".join(_f(d["resumo"]["geral"]["por_campo"][campo]["f1"]) for d in dados.values())
        linhas.append(rf"\texttt{{{_tex(campo)}}} & {primeiro[campo]['ocorrencias']} & {vals} \\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. Ocorr. = vezes que o campo aparece no gabarito.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_latencia(dados: dict[str, dict]) -> str:
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{Latência da tradução, em milissegundos, por modelo{TITULO}}}",
              rf"\label{{tab:latencia{SUFIXO}}}", r"\small",
              r"\begin{tabular}{|l|c|c|c|c|c|c|}", r"\hline",
              r"\textbf{Modelo} & \textbf{n} & \textbf{Mín.} & \textbf{Mediana} & \textbf{Média} & \textbf{p95} & \textbf{Máx.} \\",
              r"\hline"]
    for modelo, d in dados.items():
        lat = d["resumo"]["geral"]["latencia_llm_ms"]
        if not lat:
            continue
        linhas.append(f"{_tex(rotulo(modelo))} & {lat['n']} & {lat['min']:.0f} & {lat['mediana']:.0f} & "
                      f"{lat['media']:.0f} & {lat['p95']:.0f} & {lat['max']:.0f} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               rf"\fonte{{Elaborado pelos autores. Tempo da chamada de tradução, medido no ambiente de cada rodada (Tabela~\ref{{tab:ambiente{SUFIXO}}}); execuções com erro de infraestrutura excluídas.}}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def _gpu_curta(texto: str | None) -> str:
    if not texto:
        return "---"
    partes = [x.strip() for x in texto.split(",")]
    nome = partes[0].replace("NVIDIA GeForce ", "").replace("NVIDIA ", "").replace(" GPU", "")
    return f"{nome}, {partes[1]}" if len(partes) > 1 else nome   # memória como o nvidia-smi informa (MiB)


def _gpu_das_sessoes(manifesto: dict) -> tuple[str, str]:
    """(parcela na GPU, VRAM livre) das sessões registradas; '---' quando não medidas (nuvem, rodadas antigas)."""
    sessoes = manifesto.get("sessoes") or []
    fracoes = sorted({round(100 * x["ollama_ps"]["fracao_na_gpu"]) for x in sessoes
                      if (x.get("ollama_ps") or {}).get("fracao_na_gpu") is not None})
    livres = sorted({x["vram_inicio"]["livre_mib"] for x in sessoes if x.get("vram_inicio")})
    na_gpu = "---" if not fracoes else (f"{fracoes[0]}\\%" if len(fracoes) == 1 else f"{fracoes[0]}--{fracoes[-1]}\\%")
    livre = "---" if not livres else (f"{livres[0] / 1024:.1f} GB".replace(".", ",") if len(livres) == 1
                                      else f"{livres[0] / 1024:.1f}--{livres[-1] / 1024:.1f} GB".replace(".", ","))
    return na_gpu, livre


def tab_por_origem(dados: dict[str, dict]) -> str:
    """Acurácia por camada de origem das consultas (P: protótipo, N: autores, G: geradas)."""
    cols = "|l|c|" + "c|" * len(dados)
    cab = " & ".join(rf"\textbf{{{_tex(rotulo(m))}}}" for m in dados)
    nomes = {"P": "Protótipo (P)", "N": "Autores (N)", "G": "Geradas (G)"}
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{Acurácia por camada de origem das consultas{TITULO}}}",
              rf"\label{{tab:resultados_por_origem{SUFIXO}}}", r"\small",
              rf"\begin{{tabular}}{{{cols}}}", r"\hline",
              rf"\textbf{{Camada}} & \textbf{{Consultas}} & {cab} \\", r"\hline"]
    primeiro = next(iter(dados.values()))["resumo"]["geral"]["por_origem"]
    for origem in ("P", "N", "G"):
        if not primeiro.get(origem, {}).get("n_consultas"):
            continue
        vals = " & ".join(_pct(d["resumo"]["geral"]["por_origem"][origem]["acuracia"]) for d in dados.values())
        linhas.append(f"{nomes[origem]} & {primeiro[origem]['n_consultas']} & {vals} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. Consultas distintas das métricas principais; acurácia sobre todas as repetições.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_mcnemar(dados: dict[str, dict]) -> str:
    """Teste de McNemar exato entre cada par de modelos (mesmas consultas e repetições)."""
    correcoes = {m: correcao_por_consulta(d["linhas"]) for m, d in dados.items()}
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{Teste de McNemar exato entre pares de modelos{TITULO}}}",
              rf"\label{{tab:mcnemar{SUFIXO}}}", r"\small",
              r"\begin{tabular}{|l|l|c|c|c|}", r"\hline",
              r"\textbf{Modelo A} & \textbf{Modelo B} & \textbf{Só A acerta} & \textbf{Só B acerta} & \textbf{\textit{p}-valor} \\",
              r"\hline"]
    modelos = list(dados)
    for i in range(len(modelos)):
        for j in range(i + 1, len(modelos)):
            so_a, so_b = _discordantes(correcoes[modelos[i]], correcoes[modelos[j]])
            linhas.append(f"{_tex(rotulo(modelos[i]))} & {_tex(rotulo(modelos[j]))} & {so_a} & {so_b} & "
                          f"{_f(mcnemar_exato(so_a, so_b), 4)} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. Pares discordantes sobre as mesmas consultas e repetições das métricas principais; \textit{p}-valor bicaudal exato.}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def _discordantes(a: dict, b: dict) -> tuple[int, int]:
    comuns = set(a) & set(b)
    return (sum(1 for k in comuns if a[k] and not b[k]), sum(1 for k in comuns if b[k] and not a[k]))


def _num(v: float, casas: int = 1) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


EXTENSO = {1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco", 6: "seis", 7: "sete"}
EXTENSO_EN = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven"}


def _lista(itens: list[str]) -> str:
    return itens[0] if len(itens) == 1 else ", ".join(itens[:-1]) + " e " + itens[-1]


def descricao_modelos(dados: dict[str, dict]) -> dict[str, str]:
    """Quantos e quais modelos a rodada tem, e o esforço de raciocínio de cada um (nuvem)."""
    modelos = list(dados)
    n = len(modelos)
    tags = [f"\\texttt{{{_tex(m)}}}" for m in modelos]
    por_esforco: dict[str, list[str]] = defaultdict(list)
    for m in modelos:
        esforco = (dados[m].get("manifesto", {}).get("modelo_info") or {}).get("esforco_de_raciocinio")
        if esforco:
            por_esforco[esforco].append(f"o \\texttt{{{_tex(m)}}}")
    esforcos = _lista([f"\\texttt{{{e}}} para {_lista(ms)}" for e, ms in por_esforco.items()]) if por_esforco else ""
    return {"nmodelos": EXTENSO.get(n, str(n)), "nmodelosmaiusc": EXTENSO.get(n, str(n)).capitalize(),
            "nmodelosen": EXTENSO_EN.get(n, str(n)),
            "tags": _lista(tags) if tags else "", "nomes": _lista([_tex(rotulo(m)) for m in modelos]) if modelos else "",
            "esforcos": esforcos}


def cobertura(dados: dict[str, dict]) -> dict[str, str]:
    """Consultas do dataset vigente cobertas pela rodada (as mesmas para todos os modelos consolidados).

    Uma consulta executada com texto diferente do vigente é descartada na repontuação; quando isso
    ocorre, a macro `frasecobertura` traz a frase que o texto precisa exibir. Com cobertura completa,
    ela fica vazia.
    """
    from pfc_busca.evaluation.dataset_builder import carregar_dataset

    casos = carregar_dataset()
    por_id = {c["id"]: c for c in casos}
    ids = set.intersection(*[{lin["id"] for lin in d["linhas"]} for d in dados.values()]) if dados else set()
    origem = Counter(por_id[i]["origem"] for i in ids)
    principais = sum(1 for i in ids if not por_id[i]["observacional"])
    n_f = sum(1 for i in ids if "F" in por_id[i]["categorias"])
    total_f = sum(1 for c in casos if "F" in c["categorias"])
    n_pn = origem.get("P", 0) + origem.get("N", 0)
    total_pn = sum(1 for c in casos if c["origem"] in "PN")
    total_g = sum(1 for c in casos if c["origem"] == "G")
    frase = ""
    if len(ids) < len(casos):
        frase = (f"Nessas rodadas, a camada G foi executada a partir de uma versão anterior do gerador, cujas consultas "
                 f"diferem em redação das do \\textit{{dataset}} final. As métricas das rodadas completas cobrem, "
                 f"por isso, as {len(ids)} consultas cujo texto coincide com o do \\textit{{dataset}} final "
                 f"--- {'todas as' if n_pn == total_pn else ''} {n_pn} das camadas P e N e {origem.get('G', 0)} das "
                 f"{total_g} da camada G ---, das quais {principais} entram nas métricas principais.")
    item = ""
    if frase:
        item = (f"\\item \\textbf{{Cobertura das rodadas completas}}: as métricas das rodadas completas cobrem "
                f"{len(ids)} das {len(casos)} consultas do \\textit{{dataset}}, com a camada G representada por "
                f"{origem.get('G', 0)} consultas; os resultados por categoria e por campo dessas rodadas refletem, "
                f"sobretudo, as consultas redigidas por pessoas (camadas P e N).")
    return {"nexecutadas": str(len(ids)), "ntotal": str(len(casos)), "nprincipais": str(principais),
            "itemlimitacao": item, "nF": str(n_f), "ntotalF": str(total_f),
            "nPN": str(n_pn), "nG": str(origem.get("G", 0)), "completa": "sim" if len(ids) == len(casos) else "não",
            "frasecobertura": frase}


def macros_latex(dados: dict[str, dict]) -> str:
    """Valores citados na prosa do Cap. 5, como macros: \\res{rodada}{modelo}{medida}.

    Assim nenhum número da prosa é digitado à mão: ao regenerar o relatório, o texto se atualiza.
    """
    rodada = SUFIXO.lstrip("_") or "principal"
    defs: dict[str, str] = {}

    def put(modelo: str, medida: str, valor: str) -> None:
        defs[f"res@{rodada}@{modelo}@{medida}"] = valor

    correcoes = {m: correcao_por_consulta(d["linhas"]) for m, d in dados.items()}
    for m, d in dados.items():
        chave = CHAVES.get(m, slug(m))
        g = d["resumo"]["geral"]
        corr = correcoes[m]
        lo, hi = wilson(sum(corr.values()), len(corr))
        lat = g["latencia_llm_ms"] or {}
        put(chave, "nome", _tex(rotulo(m)))
        put(chave, "n", str(g["n_consultas"]))
        put(chave, "acertos", str(sum(corr.values())))
        put(chave, "execucoes", str(len(corr)))
        put(chave, "acuracia", _pct(g["acuracia"]))
        put(chave, "ic", f"{_pct(lo)} a {_pct(hi)}")
        for campo, rotulo_campo in (("precisao_ponderada", "precisao"), ("recall_ponderado", "recall"),
                                    ("f1_ponderado", "f1"), ("f1_macro", "f1macro")):
            put(chave, rotulo_campo, _f(g[campo]))
        if lat:
            put(chave, "latmed", f"{lat['mediana']:.0f}")
            put(chave, "latmeds", _num(lat["mediana"] / 1000))
            put(chave, "latpnoventaecinco", _num(lat["p95"] / 1000))
        for cat, v in g["por_categoria"].items():
            put(chave, f"acc{cat}", _pct(v["acuracia"]))
            put(chave, f"fum{cat}", _f(v["f1_ponderado"]))
        for campo, v in g["por_campo"].items():
            put(chave, f"f1{campo}", _f(v["f1"]))
        for tipo, qtd in g["diagnosticos"]["tipos_erro"].items():
            put(chave, "erro" + tipo.replace("_", ""), str(qtd))
        toks = sorted(lin["tokens_saida"] for lin in d["linhas"]
                      if lin.get("tokens_saida") and not lin.get("observacional"))
        if toks:
            put(chave, "toksaida", _num(statistics.median(toks), 0))
        na_gpu, livre = _gpu_das_sessoes(d.get("manifesto", {}))
        put(chave, "nagpu", na_gpu)
        put(chave, "vramlivre", livre)
        for origem, v in g["por_origem"].items():
            put(chave, f"n{origem}", str(v["n"]))
            put(chave, f"accorigem{origem}", _pct(v["acuracia"]))
        for cat, v in g["por_categoria"].items():
            put(chave, f"ncat{cat}", str(v["n_consultas"]))
        for origem, v in g["por_origem"].items():
            put(chave, f"nconsultas{origem}", str(v["n_consultas"]))
        obs = g.get("observacionais") or {}
        if obs:
            put(chave, "obsn", str(obs.get("n", 0)))
            put(chave, "obschamou", str(obs.get("chamou_sem_dever", 0)))
        narrada = esclarecimento = escopo = 0
        for lin in d["linhas"]:
            if lin.get("observacional") or metrics.avaliar_linha(lin).tipo_erro != "nao_chamou":
                continue
            texto = (lin.get("texto_resposta") or "").lower()
            if "buscar_catalogo" in texto:
                narrada += 1
            elif "fora do escopo" in texto:
                escopo += 1
            elif any(p in texto for p in ("especifi", "mais informa", "mais detalhes", "poderia", "qual ")):
                esclarecimento += 1
        # estabilidade entre repetições: consultas com a mesma resposta em todas as repetições
        por_id: dict[str, list] = defaultdict(list)
        for lin in d["linhas"]:
            if not lin.get("observacional"):
                por_id[lin["id"]].append(json.dumps(lin.get("predito"), sort_keys=True, ensure_ascii=False))
        multi = {i: v for i, v in por_id.items() if len(v) > 1}
        if multi:
            put(chave, "estaveis", str(sum(1 for v in multi.values() if len(set(v)) == 1)))
            put(chave, "nestaveis", str(len(multi)))
        put(chave, "naochamounarrada", str(narrada))
        put(chave, "naochamouescopo", str(escopo))
        put(chave, "naochamouesclarecimento", str(esclarecimento))
        erros = g["diagnosticos"]
        put(chave, "errosinfra", str(erros.get("chamadas_com_erro", 0)))
        put(chave, "foradoschema", str(erros.get("respostas_fora_do_schema", 0)))
    for medida, valor in descricao_modelos(dados).items():
        put("geral", medida, valor)
    # cobertura da rodada: quantas consultas do dataset vigente foram de fato executadas e pontuadas
    for medida, valor in cobertura(dados).items():
        put("geral", medida, valor)
    modelos = list(dados)
    for i in range(len(modelos)):
        for j in range(i + 1, len(modelos)):
            a, b = modelos[i], modelos[j]
            par = f"{CHAVES.get(a, slug(a))}-{CHAVES.get(b, slug(b))}"
            so_a, so_b = _discordantes(correcoes[a], correcoes[b])
            put(par, "soa", str(so_a))
            put(par, "sob", str(so_b))
            pv = mcnemar_exato(so_a, so_b)
            put(par, "p", "inferior a 0,001" if pv < 0.001 else _f(pv, 3))
            la = (dados[a]["resumo"]["geral"]["latencia_llm_ms"] or {}).get("mediana")
            lb = (dados[b]["resumo"]["geral"]["latencia_llm_ms"] or {}).get("mediana")
            if la and lb:
                put(par, "razaolat", _num(max(la, lb) / min(la, lb)))
    out = [f"% AUTO-GERADO por pfc-relatorio (rodada '{rodada}') — não editar à mão",
           r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname\else\textbf{??}\fi}"]
    out += [f"\\expandafter\\def\\csname {k}\\endcsname{{{v}}}" for k, v in sorted(defs.items())]
    return "\n".join(out) + "\n"


def concordancia_ambientes(principal: dict[str, dict], outro: dict[str, dict]) -> list[dict]:
    """Mesmo modelo em dois ambientes: nas consultas comuns (1ª repetição de cada lado), com que
    frequência a resposta é idêntica e a pontuação (certo/errado) coincide."""
    saida = []
    for m in principal:
        if m not in outro:
            continue
        rep_a = min(x["repeticao"] for x in principal[m]["linhas"])
        rep_b = min(x["repeticao"] for x in outro[m]["linhas"])
        a = {x["id"]: x for x in principal[m]["linhas"] if x["repeticao"] == rep_a and not x.get("observacional")}
        b = {x["id"]: x for x in outro[m]["linhas"] if x["repeticao"] == rep_b and not x.get("observacional")}
        comuns = sorted(set(a) & set(b))
        if not comuns:
            continue
        iguais = sum(1 for i in comuns if a[i]["predito"] == b[i]["predito"])
        mesma_nota = sum(1 for i in comuns
                         if metrics.avaliar_linha(a[i]).correto == metrics.avaliar_linha(b[i]).correto)
        acc_a = sum(metrics.avaliar_linha(a[i]).correto for i in comuns) / len(comuns)
        acc_b = sum(metrics.avaliar_linha(b[i]).correto for i in comuns) / len(comuns)
        saida.append({"modelo": m, "n": len(comuns), "respostas_identicas": iguais,
                      "mesma_pontuacao": mesma_nota, "acuracia_principal": acc_a, "acuracia_outro": acc_b})
    return saida


def tab_concordancia_ambientes(linhas_c: list[dict], nome: str, rotulos: tuple[str, str], legenda: str) -> str:
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{{legenda}}}",
              rf"\label{{tab:concordancia-{nome}}}", r"\small",
              r"\begin{tabular}{|l|c|>{\centering\arraybackslash}p{2.0cm}|>{\centering\arraybackslash}p{2.0cm}|>{\centering\arraybackslash}p{2.2cm}|>{\centering\arraybackslash}p{2.2cm}|}", r"\hline",
              r"\textbf{Modelo} & \textbf{n} & \textbf{Resposta idêntica} & \textbf{Mesma pontuação} & "
              rf"\textbf{{Acurácia ({_tex(rotulos[0])})}} & \textbf{{Acurácia ({_tex(rotulos[1])})}} \\",
              r"\hline"]
    for c in linhas_c:
        linhas.append(f"{_tex(rotulo(c['modelo']))} & {c['n']} & {c['respostas_identicas']} & {c['mesma_pontuacao']} & "
                      f"{_pct(c['acuracia_principal'])} & {_pct(c['acuracia_outro'])} \\\\")
    linhas += [r"\hline", r"\end{tabular}",
               r"\fonte{Elaborado pelos autores. Resposta idêntica: mesmos parâmetros emitidos (ou nenhuma chamada nos dois ambientes).}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


def tab_ambiente(dados: dict[str, dict]) -> str:
    """Ambiente de cada rodada, transcrito dos manifestos (nada digitado à mão)."""
    linhas = [r"\begin{table}[htbp!]", r"\centering",
              rf"\caption{{Ambiente de execução de cada rodada{TITULO}}}",
              rf"\label{{tab:ambiente{SUFIXO}}}", r"\footnotesize",
              r"\begin{tabular}{|l|l|l|c|c|c|c|}", r"\hline",
              r"\textbf{Modelo} & \textbf{GPU / máquina} & \textbf{Servidor} & \textbf{Rep.} & \textbf{Exec.} & \textbf{Na GPU} & \textbf{VRAM livre} \\",
              r"\hline"]
    for modelo, d in dados.items():
        m, r = d.get("manifesto", {}), d["resumo"]
        hw = m.get("hardware", {})
        gpu = _gpu_curta(hw.get("gpu")) if hw.get("gpu") else (hw.get("maquina") or "---")
        sw = m.get("software", {})
        servidor = (f"Ollama {sw['ollama_servidor']}" if sw.get("ollama_servidor")
                    else ("Groq (API)" if m.get("provedor") == "groq" else "---"))
        na_gpu, livre = _gpu_das_sessoes(m)
        linhas.append(f"{_tex(rotulo(modelo))} & {_tex(gpu)} & {_tex(servidor)} & "
                      f"{len(r.get('repeticoes', []))} & {r.get('n_execucoes', 0)} & {na_gpu} & {livre} \\\\")
    datas = sorted({d.get("manifesto", {}).get("hoje") for d in dados.values() if d.get("manifesto", {}).get("hoje")})
    data_ref = ", ".join(datas) if datas else "---"
    versoes = next((d["manifesto"].get("software", {}) for d in dados.values() if d.get("manifesto")), {})
    extra = ", ".join(f"{k.replace('_', '-')} {v}" for k, v in versoes.items()
                      if k.startswith("langchain") and v)
    linhas += [r"\hline", r"\end{tabular}",
               rf"\fonte{{Elaborado pelos autores a partir de \texttt{{results/<modelo>/manifesto.json}}. Na GPU: parcela do modelo carregado (pesos e contexto) alocada na VRAM pelo Ollama, medida após o aquecimento; VRAM livre: no início da rodada, com os demais modelos descarregados. Data de referência: {data_ref}. Python {versoes.get('python', '---')}; {_tex(extra)}.}}",
               r"\end{table}"]
    return "\n".join(linhas) + "\n"


# ---------------------------------------------------------------------------
# Figuras
# ---------------------------------------------------------------------------

def figuras(dados: dict[str, dict], saida: Path) -> list[str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    virgula = FuncFormatter(lambda v, _pos: f"{v:.1f}".replace(".", ","))
    porcento = FuncFormatter(lambda v, _pos: f"{100 * v:.0f}%")
    gerados = []
    modelos = list(dados)
    nomes = [rotulo(m) for m in modelos]

    # 1) boxplot de latência
    series = [[lin["latencia_llm_ms"] for lin in dados[m]["linhas"]
               if lin.get("latencia_llm_ms") is not None and not lin.get("erro") and not lin.get("observacional")]
              for m in modelos]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.boxplot(series, tick_labels=nomes, showfliers=True, flierprops={"markersize": 2, "alpha": 0.4})
    ax.set_ylabel("latência da tradução (s)")
    ax.set_yscale("log")
    todos = [v for serie in series for v in serie] or [1000]
    marcas = [v for v in (100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 30000, 60000, 120000)
              if min(todos) / 1.5 <= v <= max(todos) * 1.5]
    ax.yaxis.set_major_locator(FixedLocator(marcas))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _pos: f"{v / 1000:g}".replace(".", ",")))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_latencia_boxplot{SUFIXO}.{ext}", dpi=200)
    plt.close(fig)
    gerados.append(f"fig_latencia_boxplot{SUFIXO}")

    # 2) F1 por campo, barras agrupadas
    fig, ax = plt.subplots(figsize=(9, 3.8))
    largura = 0.8 / max(1, len(modelos))
    x = list(range(len(schema.CAMPOS)))
    for i, m in enumerate(modelos):
        f1s = [dados[m]["resumo"]["geral"]["por_campo"][c]["f1"] for c in schema.CAMPOS]
        ax.bar([xi + i * largura for xi in x], f1s, width=largura, label=rotulo(m))
    ax.set_xticks([xi + largura * (len(modelos) - 1) / 2 for xi in x])
    ax.set_xticklabels(schema.CAMPOS, rotation=35, ha="right")
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(virgula)
    ax.set_ylabel("F1 por campo")
    ax.legend(frameon=False, ncol=len(modelos), fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.01))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_f1_por_campo{SUFIXO}.{ext}", dpi=200)
    plt.close(fig)
    gerados.append(f"fig_f1_por_campo{SUFIXO}")

    # 3) acurácia por categoria
    cats = CATS_ACC
    fig, ax = plt.subplots(figsize=(8, 3.6))
    for i, m in enumerate(modelos):
        acc = [dados[m]["resumo"]["geral"]["por_categoria"][c]["acuracia"] or 0 for c in cats]
        ax.bar([xi + i * largura for xi in range(len(cats))], acc, width=largura, label=rotulo(m))
    ax.set_xticks([xi + largura * (len(modelos) - 1) / 2 for xi in range(len(cats))])
    ax.set_xticklabels([CATEGORIA_CURTA[c] for c in cats], fontsize=8)
    ax.set_ylim(0, 1.0)
    ax.yaxis.set_major_formatter(porcento)
    ax.set_ylabel("acurácia por consulta")
    ax.legend(frameon=False, ncol=len(modelos), fontsize=8, loc="lower left", bbox_to_anchor=(0.0, 1.01))
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(saida / f"fig_acuracia_por_categoria{SUFIXO}.{ext}", dpi=200)
    plt.close(fig)
    gerados.append(f"fig_acuracia_por_categoria{SUFIXO}")
    return gerados


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def comparativo_markdown(dados: dict[str, dict]) -> str:
    out = ["# Comparativo entre modelos", ""]
    out += ["| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for m, d in dados.items():
        g = d["resumo"]["geral"]
        corr = correcao_por_consulta(d["linhas"])
        lo, hi = wilson(sum(corr.values()), len(corr))
        lat = g["latencia_llm_ms"]
        out.append(f"| {rotulo(m)} | {g['n_consultas']} | {_pct_md(g['acuracia'])} | {100*lo:.1f}–{100*hi:.1f}% | "
                   f"{g['precisao_ponderada']:.3f} | {g['recall_ponderado']:.3f} | {g['f1_ponderado']:.3f} | {g['f1_macro']:.3f} | "
                   f"{lat.get('mediana', 0):.0f} | {lat.get('p95', 0):.0f} | {g['diagnosticos']['chamadas_com_erro']} |")
    out += ["", "## F1 ponderado por categoria", "",
            "| Categoria | " + " | ".join(rotulo(m) for m in dados) + " |",
            "|---|" + "---|" * len(dados)]
    for cat in CATS_F1:
        out.append(f"| {NOMES_CATEGORIA[cat]} | " + " | ".join(
            f"{d['resumo']['geral']['por_categoria'][cat]['f1_ponderado']:.3f}" for d in dados.values()) + " |")
    out += ["", "## Acurácia por categoria", "",
            "| Categoria | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|" + "---|" * len(dados)]
    for cat in CATS_ACC:
        out.append(f"| {NOMES_CATEGORIA[cat]} | " + " | ".join(
            _pct_md(d['resumo']['geral']['por_categoria'][cat]['acuracia']) for d in dados.values()) + " |")
    out += ["", "## F1 por campo", "",
            "| Campo | Ocorr. | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|---|" + "---|" * len(dados)]
    primeiro = next(iter(dados.values()))["resumo"]["geral"]["por_campo"]
    for campo in schema.CAMPOS:
        out.append(f"| `{campo}` | {primeiro[campo]['ocorrencias']} | " + " | ".join(
            f"{d['resumo']['geral']['por_campo'][campo]['f1']:.3f}" for d in dados.values()) + " |")
    out += ["", "## Acurácia por origem do caso", "",
            "| Origem | " + " | ".join(rotulo(m) for m in dados) + " |", "|---|" + "---|" * len(dados)]
    for o in ["P", "N", "G"]:
        out.append(f"| {o} | " + " | ".join(
            _pct_md(d['resumo']['geral']['por_origem'][o]['acuracia']) for d in dados.values()) + " |")
    out += ["", "## Diagnósticos", ""]
    for m, d in dados.items():
        g = d["resumo"]["geral"]
        dg = g["diagnosticos"]
        obs = g["observacionais"]
        out += [f"### {rotulo(m)}", "",
                f"- tipos de erro: {dg['tipos_erro']}",
                f"- campos fora do schema: {dg['campos_fora_do_schema']}",
                f"- IoU médio de períodos: { {k: round(v, 3) for k, v in dg['iou_periodos_medio'].items()} }",
                f"- chamadas com erro: {dg['chamadas_com_erro']} {dg['classes_de_erro']}",
                f"- não chamou quando devia: {dg['nao_chamou_quando_devia']}",
                f"- observacionais: {obs['n']} casos, acurácia {_pct_md(obs['acuracia'])}, chamou sem dever {obs['chamou_sem_dever']}",
                f"- thinking desativado: {d['manifesto'].get('thinking_desativado')} · Ollama {d['manifesto'].get('software', {}).get('ollama_servidor')} · "
                f"repetições {d['resumo']['repeticoes']}", ""]
    return "\n".join(out) + "\n"


def estatistica_markdown(dados: dict[str, dict]) -> str:
    out = ["# Estatística", "", "## Acurácia com IC 95% (Wilson)", "",
           "| Modelo | acertos / n | acurácia | IC 95% |", "|---|---|---|---|"]
    correcoes = {m: correcao_por_consulta(d["linhas"]) for m, d in dados.items()}
    for m, corr in correcoes.items():
        n, k = len(corr), sum(corr.values())
        lo, hi = wilson(k, n)
        out.append(f"| {rotulo(m)} | {k} / {n} | {100*k/n if n else 0:.1f}% | {100*lo:.1f}–{100*hi:.1f}% |")
    out += ["", "## McNemar pareado (mesmas consultas × repetições)", "",
            "| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |", "|---|---|---|---|---|"]
    modelos = list(dados)
    for i in range(len(modelos)):
        for j in range(i + 1, len(modelos)):
            a, b = correcoes[modelos[i]], correcoes[modelos[j]]
            comuns = set(a) & set(b)
            so_a = sum(1 for k in comuns if a[k] and not b[k])
            so_b = sum(1 for k in comuns if b[k] and not a[k])
            out.append(f"| {rotulo(modelos[i])} | {rotulo(modelos[j])} | {so_a} | {so_b} | "
                       f"{mcnemar_exato(so_a, so_b):.4f} |")
    out += ["", "Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as "
            "mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares "
            "independentes — é uma aproximação, declarada como tal no texto.", ""]
    return "\n".join(out)


def erros_markdown(dados: dict[str, dict], por_tipo: int = 4, semente: int = 42) -> str:
    rng = random.Random(semente)
    out = ["# Erros representativos (amostra aleatória por tipo, semente 42)", ""]
    for m, d in dados.items():
        out += [f"## {rotulo(m)}", ""]
        grupos: dict[str, list] = defaultdict(list)
        for lin in d["linhas"]:
            if lin.get("observacional") or lin["repeticao"] != min(x["repeticao"] for x in d["linhas"]):
                continue
            aval = metrics.avaliar_linha(lin)
            if not aval.correto:
                grupos[aval.tipo_erro or "outro"].append((lin, aval))
        for tipo, itens in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
            out += [f"### {tipo} ({len(itens)} casos)", ""]
            for lin, aval in rng.sample(itens, min(por_tipo, len(itens))):
                out += [f"- **{lin['id']}** — \"{lin['consulta']}\"",
                        f"  - esperado: `{json.dumps(lin['esperado_resolvido'], ensure_ascii=False)}`",
                        f"  - predito: `{json.dumps(lin['predito'], ensure_ascii=False)}`"
                        + (f" · erro: {lin['erro']}" if lin.get("erro") else ""),
                        f"  - FP {sorted(aval.fp)} · FN {sorted(aval.fn)} · fora do schema {sorted(aval.fora_do_schema)}"]
            out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(description="Consolida resultados de vários modelos.")
    p.add_argument("--resultados", type=Path, default=DIR_RESULTADOS)
    p.add_argument("--modelos", help="tags separadas por vírgula, na ordem das tabelas")
    p.add_argument("--saida", type=Path, default=None)
    p.add_argument("--sufixo", default="", help="sufixo de arquivos e rótulos (ex.: _groq)")
    p.add_argument("--titulo", default="", help="complemento do título das tabelas")
    p.add_argument("--comparar-com", type=Path, metavar="DIR_RESULTADOS",
                   help="outro conjunto de rodadas (ex.: results/estacao) para medir a concordância entre ambientes")
    p.add_argument("--nome-comparacao", default="ambientes", help="nome da comparação (arquivos, label e macros)")
    p.add_argument("--rotulos-comparacao", default="rodada completa,estação",
                   help="rótulos das duas rodadas comparadas, separados por vírgula")
    p.add_argument("--legenda-comparacao",
                   default="Mesmo modelo nas rodadas completas e na estação de referência (camadas P e N, primeira repetição)")
    p.add_argument("--so-comparacao", action="store_true", help="gera só a comparação (com --comparar-com)")
    p.add_argument("--mesmas-consultas-de", type=Path, metavar="DIR_RESULTADOS",
                   help="restringe a pontuação às consultas cobertas pelas rodadas deste diretório "
                        "(comparação justa entre rodadas de cobertura diferente)")
    p.add_argument("--modelos-referencia", help="modelos de --mesmas-consultas-de cuja cobertura vale (vírgula)")
    p.add_argument("--paper", type=Path, metavar="DIR",
                   help="copia tab_*.tex para DIR/tabelas e fig_*.pdf para DIR/figuras (o Cap. 5 os inclui)")
    args = p.parse_args(argv)

    global SUFIXO, TITULO
    SUFIXO, TITULO = args.sufixo, args.titulo
    modelos = [m.strip() for m in args.modelos.split(",")] if args.modelos else None
    dados = carregar_modelos(args.resultados, modelos)
    if not dados:
        print("nenhum results/<modelo>/resumo.json encontrado", file=sys.stderr)
        return 1
    if args.mesmas_consultas_de:
        ref_modelos = [m.strip() for m in args.modelos_referencia.split(",")] if args.modelos_referencia else None
        referencia = carregar_modelos(args.mesmas_consultas_de, ref_modelos)
        if not referencia:
            print("nenhuma rodada de referência encontrada", file=sys.stderr)
            return 1
        ids = set.intersection(*[{lin["id"] for lin in d["linhas"]} for d in referencia.values()])
        for d in dados.values():
            d["linhas"] = [lin for lin in d["linhas"] if lin["id"] in ids]
            d["resumo"] = {**d["resumo"], "geral": metrics.agregar(d["linhas"]), "n_execucoes": len(d["linhas"]),
                           "restrito_a": len(ids)}
        print(f"pontuação restrita às {len(ids)} consultas cobertas por {args.mesmas_consultas_de}")
    saida = args.saida or (args.resultados / "consolidado")
    saida.mkdir(parents=True, exist_ok=True)
    produzidos: list[Path] = []   # só o que ESTA execução gerou vai para o texto (--paper)

    def gravar(nome: str, conteudo: str) -> None:
        if nome.startswith("tab_"):
            conteudo = ajustar_largura(conteudo)
        (saida / nome).write_text(conteudo, encoding="utf-8")
        produzidos.append(saida / nome)

    if args.so_comparacao and not args.comparar_com:
        print("--so-comparacao exige --comparar-com", file=sys.stderr)
        return 1

    if not args.so_comparacao:
        gravar(f"comparativo{SUFIXO}.md", comparativo_markdown(dados))
        gravar(f"estatistica{SUFIXO}.md", estatistica_markdown(dados))
        gravar(f"erros_representativos{SUFIXO}.md", erros_markdown(dados))
        gravar(f"tab_comparativo{SUFIXO}.tex", tab_comparativo(dados))
        gravar(f"tab_por_categoria{SUFIXO}.tex", tab_por_categoria(dados))
        gravar(f"tab_por_campo{SUFIXO}.tex", tab_por_campo(dados))
        gravar(f"tab_latencia{SUFIXO}.tex", tab_latencia(dados))
        gravar(f"tab_ambiente{SUFIXO}.tex", tab_ambiente(dados))
        gravar(f"tab_mcnemar{SUFIXO}.tex", tab_mcnemar(dados))
        gravar(f"tab_por_origem{SUFIXO}.tex", tab_por_origem(dados))
        gravar(f"numeros{SUFIXO}.tex", macros_latex(dados))
        produzidos.extend(saida / f"{nome}.pdf" for nome in figuras(dados, saida))

    if args.comparar_com:
        outro = carregar_modelos(args.comparar_com, modelos)
        conc = concordancia_ambientes(dados, outro)
        nome = args.nome_comparacao
        rotulos = tuple(x.strip() for x in args.rotulos_comparacao.split(","))[:2]
        if conc:
            gravar(f"tab_concordancia_{nome}.tex", tab_concordancia_ambientes(conc, nome, rotulos, args.legenda_comparacao))
            macros = [f"% AUTO-GERADO por pfc-relatorio --comparar-com (comparação '{nome}')"]
            for c in conc:
                chave = CHAVES.get(c["modelo"], slug(c["modelo"]))
                for medida, valor in (("n", c["n"]), ("identicas", c["respostas_identicas"]),
                                      ("mesmanota", c["mesma_pontuacao"]),
                                      ("acuraciaa", _pct(c["acuracia_principal"])),
                                      ("acuraciab", _pct(c["acuracia_outro"]))):
                    macros.append(f"\\expandafter\\def\\csname res@{nome}@{chave}@{medida}\\endcsname{{{valor}}}")
            gravar(f"numeros_{nome}.tex", "\n".join(macros) + "\n")
            print(f"comparação '{nome}': {len(conc)} modelo(s) → tab_concordancia_{nome}.tex, numeros_{nome}.tex")
        else:
            print(f"comparação '{nome}': nenhum modelo em comum com {args.comparar_com}", file=sys.stderr)

    if args.paper:
        import shutil
        for f in produzidos:
            if f.suffix == ".tex":
                destino = args.paper / "tabelas"
            elif f.suffix == ".pdf":
                destino = args.paper / "figuras"
            else:
                continue
            destino.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, destino / f.name)
        print(f"{sum(f.suffix in ('.tex', '.pdf') for f in produzidos)} arquivo(s) copiados para {args.paper}")
    print(f"consolidado {len(dados)} modelo(s) em {saida}: " + ", ".join(f.name for f in produzidos))
    for m in dados:
        print(f"  - {m} ({slug(m)}) → {rotulo(m)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
