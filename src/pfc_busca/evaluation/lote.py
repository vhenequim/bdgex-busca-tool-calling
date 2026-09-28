"""Lote de validação e especificação v2: tabelas, macros e relatório (Cap. 5).

    python -m pfc_busca.evaluation.lote --paper ../paper_revisado

Um modelo (Gemma 4 E4B, o de maior acurácia com Tool Calling na T4), quatro configurações:

    tc1  Tool Calling v1 (a solução do Cap. 4)       pasta <modelo>/
    se1  Saída Estruturada v1 (linha de base)        pasta se-<modelo>/
    tc2  Tool Calling v2 (`pfc_busca.v2`)            pasta tc2-<modelo>/
    se2  Saída Estruturada v2 (`pfc_busca.v2`)       pasta se2-<modelo>/

em dois conjuntos: o lote de validação (`results/lote/`, independente do desenho da v2) e as
310 consultas (v1 em `results/`, das rodadas da T4; v2 em `results/v2_310/`, dentro da amostra
que orientou o desenho da v2).

Medidas por configuração: acurácia (IC de Wilson, n = consultas), F1 ponderado, macro e micro,
F1 por campo e por categoria; recusa como classificação (positivo = consulta fora do domínio;
previsto positivo = não buscou), com precisão, recall (a "recusa F" do Cap. 5), F1 e taxa de
falsa recusa nas consultas do domínio; comportamento na categoria E; acurácia nas consultas com
uma leitura e com mais de uma leitura aceita; acurácia por registro de linguagem e por subtipo.
Comparações entre pares: McNemar exato (uma observação por consulta) e bootstrap pareado
(2.000 reamostragens das consultas, semente 42) para a diferença de acurácia e de F1 ponderado.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from pfc_busca import schema
from pfc_busca.evaluation import gabarito, metrics, report
from pfc_busca.evaluation.dataset_builder import carregar_dataset
from pfc_busca.evaluation.run_evaluation import (
    DIR_RESULTADOS,
    carregar_execucoes,
    dataset_da_rodada,
    repontuar,
)

MODELO = "gemma4-e4b-it-qat"
CONFIGS = {"tc1": ("", "Tool Calling v1"), "se1": ("se-", "Saída Estruturada v1"),
           "tc2": ("tc2-", "Tool Calling v2"), "se2": ("se2-", "Saída Estruturada v2")}
CONJUNTOS = {"lote": (DIR_RESULTADOS / "lote", {"tc1": "", "se1": "", "tc2": "", "se2": ""}),
             "base": (DIR_RESULTADOS, {"tc1": "", "se1": "", "tc2": "v2_310/", "se2": "v2_310/"})}
PARES = [("tc1", "se1"), ("tc2", "se2"), ("tc1", "tc2"), ("se1", "se2"), ("tc1", "se2")]
CATEGORIAS = ["S", "C", "M", "T", "O", "A", "E", "F"]
REPETICOES_BOOTSTRAP = 2000


def pasta(conjunto: str, config: str) -> Path:
    base, sub = CONJUNTOS[conjunto]
    return base / sub[config] / (CONFIGS[config][0] + MODELO)


def carregar(conjunto: str, config: str) -> tuple[list[dict], dict[str, dict]] | None:
    p = pasta(conjunto, config)
    linhas = carregar_execucoes(p)
    if not linhas:
        return None
    dataset = dataset_da_rodada(p)
    validas, _ = repontuar(linhas, dataset)
    casos = {c["id"]: c for c in carregar_dataset(dataset)}
    return [lin for lin in validas if not lin.get("observacional")], casos


# ---------------------------------------------------------------------------
# Medidas
# ---------------------------------------------------------------------------

def _por_id(linhas: list[dict]) -> dict[str, list[dict]]:
    d: dict[str, list[dict]] = defaultdict(list)
    for lin in linhas:
        d[lin["id"]].append(lin)
    return d


def _multiplas(lin: dict) -> bool:
    esp = lin.get("esperado_resolvido") or {}
    return bool(lin.get("alternativas_resolvidas")) or any(
        gabarito.eh_um_de(v) or gabarito.eh_opcional(v) for v in esp.values())


def _majoritario(valores: list[bool]) -> bool:
    return 2 * sum(valores) > len(valores)


def medidas(linhas: list[dict], casos: dict[str, dict]) -> dict[str, Any]:
    g = metrics.agregar(linhas)
    por_id = _por_id(linhas)
    correto = report.correcao_por_id(linhas)
    nao_buscou = {i: _majoritario([lin["predito"] is None for lin in ls]) for i, ls in por_id.items()}
    fora = {i for i, ls in por_id.items() if not ls[0]["espera_tool_call"]}
    subesp = {i for i, ls in por_id.items() if ls[0].get("aceita_nao_chamar")}
    dominio = set(por_id) - fora - subesp

    tp = sum(1 for i in fora if nao_buscou[i])
    fn = len(fora) - tp
    fp = sum(1 for i in dominio if nao_buscou[i])
    p_rec, r_rec, f1_rec = metrics.precisao_recall_f1(tp, fp, fn)

    def acc(ids: set[str] | list[str]) -> float | None:
        ids = list(ids)
        return sum(correto[i] for i in ids) / len(ids) if ids else None

    e_sem_param = sum(1 for i in subesp if not nao_buscou[i] and not (por_id[i][0]["predito"] or {}))
    e_com_param = sum(1 for i in subesp if not nao_buscou[i] and (por_id[i][0]["predito"] or {}))
    mult = {i for i, ls in por_id.items() if i not in fora and _multiplas(ls[0])}
    unica = set(por_id) - fora - mult - subesp
    registros = defaultdict(list)
    subtipos = defaultdict(list)
    for i in por_id:
        c = casos.get(i, {})
        if c.get("registro"):
            registros[c["registro"]].append(i)
        if c.get("subtipo"):
            subtipos[f"{c['familia']}·{c['subtipo']}"].append(i)
    lo, hi = report.wilson(sum(correto.values()), len(correto))
    return {
        "n": len(por_id), "acuracia": acc(list(correto)), "ic": (lo, hi),
        "f1": g["f1_ponderado"], "f1macro": g["f1_macro"], "f1micro": g["micro"]["f1"],
        "precisao": g["precisao_ponderada"], "recall": g["recall_ponderado"],
        "por_campo": g["por_campo"],
        "por_categoria": {c: {"n": g["por_categoria"][c]["n_consultas"],
                              "acuracia": acc([i for i in por_id if c in por_id[i][0]["categorias"]]),
                              "f1": g["por_categoria"][c]["f1_ponderado"]} for c in CATEGORIAS},
        "accdominio": acc(dominio),
        "recusa": {"tp": tp, "fp": fp, "fn": fn, "tn": len(dominio) - fp, "precisao": p_rec, "recall": r_rec,
                   "f1": f1_rec, "falsa": fp / len(dominio) if dominio else None, "n_fora": len(fora)},
        "subespecificadas": {"n": len(subesp), "sem_parametros": e_sem_param, "nao_buscou": len(subesp) - e_sem_param - e_com_param,
                             "com_parametros": e_com_param, "acuracia": acc(subesp)},
        "leituras": {"unica": {"n": len(unica), "acuracia": acc(unica)},
                     "multiplas": {"n": len(mult), "acuracia": acc(mult)}},
        "por_registro": {r: {"n": len(ids), "acuracia": acc(ids)} for r, ids in sorted(registros.items())},
        "por_subtipo": {s: {"n": len(ids), "acuracia": acc(ids)} for s, ids in sorted(subtipos.items())},
        "latmed": (g["latencia_llm_ms"] or {}).get("mediana"),
        "fora_do_schema": g["diagnosticos"]["respostas_fora_do_schema"],
        "erros_infra": g["diagnosticos"]["chamadas_com_erro"],
    }


def _matriz(linhas: list[dict], ids: list[str]) -> dict[str, np.ndarray]:
    """Por consulta (uma linha: a primeira repetição com o resultado majoritário) e campo: tp/fp/fn/ocorrências."""
    por_id = _por_id(linhas)
    correto = report.correcao_por_id(linhas)
    idx = {c: k for k, c in enumerate(schema.CAMPOS)}
    m = {k: np.zeros((len(ids), len(schema.CAMPOS))) for k in ("tp", "fp", "fn", "oc")}
    acertos = np.zeros(len(ids))
    for r, i in enumerate(ids):
        lin = next((x for x in por_id[i] if metrics.avaliar_linha(x).correto == correto[i]), por_id[i][0])
        a = metrics.avaliar_linha(lin)
        for nome, conjunto in (("tp", a.tp), ("fp", a.fp), ("fn", a.fn), ("oc", a.ocorrencias)):
            for c in conjunto:
                m[nome][r, idx[c]] += 1
        acertos[r] = correto[i]
    m["acertos"] = acertos
    return m


def _f1_ponderado(tp: np.ndarray, fp: np.ndarray, fn: np.ndarray, oc: np.ndarray) -> np.ndarray:
    """F1 ponderado pelas ocorrências, vetorizado sobre as reamostragens (linhas)."""
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        r = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f1 = np.where(p + r > 0, 2 * p * r / (p + r), 0.0)
        peso = oc.sum(axis=1)
        return np.where(peso > 0, (f1 * oc).sum(axis=1) / peso, 0.0)


def comparar(a: list[dict], b: list[dict]) -> dict[str, Any]:
    ca, cb = report.correcao_por_id(a), report.correcao_por_id(b)
    ids = sorted(set(ca) & set(cb))
    so_a = sum(1 for i in ids if ca[i] and not cb[i])
    so_b = sum(1 for i in ids if cb[i] and not ca[i])
    ma, mb = _matriz(a, ids), _matriz(b, ids)
    rng = np.random.default_rng(42)
    amostras = rng.integers(0, len(ids), size=(REPETICOES_BOOTSTRAP, len(ids)))
    contagem = np.zeros((REPETICOES_BOOTSTRAP, len(ids)))
    for k in range(REPETICOES_BOOTSTRAP):
        contagem[k] = np.bincount(amostras[k], minlength=len(ids))
    dif_acc = (contagem @ (mb["acertos"] - ma["acertos"])) / len(ids)
    f1a = _f1_ponderado(*(contagem @ ma[x] for x in ("tp", "fp", "fn", "oc")))
    f1b = _f1_ponderado(*(contagem @ mb[x] for x in ("tp", "fp", "fn", "oc")))
    dif_f1 = f1b - f1a
    base_f1 = _f1_ponderado(*(ma[x].sum(axis=0, keepdims=True) for x in ("tp", "fp", "fn", "oc")))[0]
    base_f1b = _f1_ponderado(*(mb[x].sum(axis=0, keepdims=True) for x in ("tp", "fp", "fn", "oc")))[0]
    return {"n": len(ids), "so_a": so_a, "so_b": so_b, "p": report.mcnemar_exato(so_a, so_b),
            "dif_acc": (mb["acertos"].mean() - ma["acertos"].mean()),
            "ic_dif_acc": tuple(np.percentile(dif_acc, [2.5, 97.5])),
            "dif_f1": base_f1b - base_f1, "ic_dif_f1": tuple(np.percentile(dif_f1, [2.5, 97.5]))}


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

def _pp(v: float) -> str:
    """Diferença em pontos percentuais, com sinal."""
    return ("+" if v > 0 else "") + f"{100 * v:.1f}".replace(".", ",")


def _ic_pp(ic: tuple[float, float]) -> str:
    return f"{_pp(ic[0])} a {_pp(ic[1])}"


def _p(pv: float) -> str:
    return r"$<$\,0,001" if pv < 0.001 else report._f(pv, 3)


def gerar() -> dict[str, Any]:
    dados: dict[str, dict[str, Any]] = {}
    for conjunto in CONJUNTOS:
        for config in CONFIGS:
            r = carregar(conjunto, config)
            if r is not None:
                dados.setdefault(conjunto, {})[config] = {"linhas": r[0], "casos": r[1]}
    resultado: dict[str, Any] = {"medidas": {}, "pares": {}}
    for conjunto, cfgs in dados.items():
        # só entram configurações que cobrem o conjunto inteiro (rodada incompleta fica de fora)
        n_total = len(next(iter(cfgs.values()))["casos"])
        completos = {k: v for k, v in cfgs.items()
                     if len({lin["id"] for lin in v["linhas"]}) >= n_total - sum(
                         1 for c in v["casos"].values() if c.get("observacional"))}
        for k in set(cfgs) - set(completos):
            print(f"{conjunto}/{k}: rodada incompleta ({len({lin['id'] for lin in cfgs[k]['linhas']})} consultas), fora")
        resultado["medidas"][conjunto] = {k: medidas(v["linhas"], v["casos"]) for k, v in completos.items()}
        resultado["pares"][conjunto] = {f"{a}{b}": comparar(completos[a]["linhas"], completos[b]["linhas"])
                                        for a, b in PARES if a in completos and b in completos}
    return resultado


def macros(res: dict[str, Any]) -> str:
    defs: dict[str, str] = {}

    def put(rodada: str, chave: str, medida: str, valor: str) -> None:
        defs[f"res@{rodada}@{chave}@{medida}"] = valor

    for conjunto, cfgs in res["medidas"].items():
        for k, m in cfgs.items():
            put(conjunto, k, "n", str(m["n"]))
            put(conjunto, k, "acuracia", report._pct(m["acuracia"]))
            put(conjunto, k, "ic", f"{report._pct(m['ic'][0])} a {report._pct(m['ic'][1])}")
            put(conjunto, k, "f1", report._f(m["f1"]))
            put(conjunto, k, "f1macro", report._f(m["f1macro"]))
            put(conjunto, k, "accdominio", report._pct(m["accdominio"]))
            put(conjunto, k, "recusa", report._pct(m["recusa"]["recall"]))
            put(conjunto, k, "recusaprec", report._pct(m["recusa"]["precisao"]))
            put(conjunto, k, "recusaf", report._f(m["recusa"]["f1"]))
            put(conjunto, k, "falsarecusa", report._pct(m["recusa"]["falsa"]))
            put(conjunto, k, "nfora", str(m["recusa"]["n_fora"]))
            e = m["subespecificadas"]
            if e["n"]:
                put(conjunto, k, "esem", report._pct(e["sem_parametros"] / e["n"]))
                put(conjunto, k, "enao", report._pct(e["nao_buscou"] / e["n"]))
                put(conjunto, k, "ecom", report._pct(e["com_parametros"] / e["n"]))
                put(conjunto, k, "en", str(e["n"]))
            put(conjunto, k, "accunica", report._pct(m["leituras"]["unica"]["acuracia"]))
            put(conjunto, k, "accmultiplas", report._pct(m["leituras"]["multiplas"]["acuracia"]))
            put(conjunto, k, "nmultiplas", str(m["leituras"]["multiplas"]["n"]))
            put(conjunto, k, "latmed", report._num((m["latmed"] or 0) / 1000, 2))
            for c in CATEGORIAS:
                put(conjunto, k, f"acc{c}", report._pct(m["por_categoria"][c]["acuracia"]))
        for par, cmp in res["pares"].get(conjunto, {}).items():
            put(conjunto, par, "p", _p(cmp["p"]))
            put(conjunto, par, "soa", str(cmp["so_a"]))
            put(conjunto, par, "sob", str(cmp["so_b"]))
            put(conjunto, par, "difacc", _pp(cmp["dif_acc"]))
            put(conjunto, par, "icdifacc", _ic_pp(cmp["ic_dif_acc"]))
            put(conjunto, par, "diff", report._f(cmp["dif_f1"]))
            put(conjunto, par, "icdiff", f"{report._f(cmp['ic_dif_f1'][0])} a {report._f(cmp['ic_dif_f1'][1])}")
    linhas = ["% AUTO-GERADO por pfc_busca.evaluation.lote — não editar à mão",
              r"\providecommand{\res}[3]{\ifcsname res@#1@#2@#3\endcsname\csname res@#1@#2@#3\endcsname\else\textbf{??}\fi}"]
    linhas += [f"\\expandafter\\def\\csname {k}\\endcsname{{{v}}}" for k, v in sorted(defs.items())]
    return "\n".join(linhas) + "\n"


def tabela_principal(res: dict[str, Any]) -> str:
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{Gemma 4 E4B no lote de validação e nas 310 consultas: especificações v1 e v2}",
         r"\label{tab:lote}", r"\footnotesize", r"\ajustartabela{%",
         r"\begin{tabular}{|l|l|c|c|c|c|c|c|c|}", r"\hline",
         r"\textbf{Conjunto} & \textbf{Configuração} & \textbf{Acurácia} & \textbf{IC 95\%} & \textbf{F1} & "
         r"\textbf{Recusa F} & \textbf{Falsa recusa} & \textbf{F1 recusa} & \textbf{Múltiplas leituras} \\", r"\hline"]
    nomes = {"lote": "Lote de validação", "base": "310 consultas"}
    for conjunto in ("lote", "base"):
        cfgs = res["medidas"].get(conjunto, {})
        if not cfgs:
            continue
        n = next(iter(cfgs.values()))["n"]
        primeira = True
        for k in CONFIGS:
            if k not in cfgs:
                continue
            m = cfgs[k]
            rotulo = (rf"\multirow{{{len(cfgs)}}}{{*}}{{\shortstack[l]{{{nomes[conjunto]}\\(n={n})}}}}"
                      if primeira else "")
            primeira = False
            L.append(f"{rotulo} & {CONFIGS[k][1]} & {report._pct(m['acuracia'])} & "
                     f"{report._pct(m['ic'][0])}--{report._pct(m['ic'][1])} & {report._f(m['f1'])} & "
                     f"{report._pct(m['recusa']['recall'])} & {report._pct(m['recusa']['falsa'])} & "
                     f"{report._f(m['recusa']['f1'])} & {report._pct(m['leituras']['multiplas']['acuracia'])} \\\\")
        L.append(r"\hline")
    L += [r"\end{tabular}}",
          r"\fonte{Elaborado pelos autores. Gemma 4 E4B, GPU T4. Acurácia por consulta, com IC de Wilson. "
          r"Recusa F: proporção das consultas fora do domínio sem busca (recall da recusa). Falsa recusa: "
          r"proporção das consultas do domínio (fora das categorias F e E) sem busca. F1 recusa: média harmônica "
          r"da precisão e do recall da recusa. Múltiplas leituras: acurácia nas consultas do domínio com mais de "
          r"uma leitura aceita. Na v1, a Saída Estruturada não tem como recusar. A v2 foi desenhada a partir dos "
          r"erros nas 310 consultas: nesse conjunto, o resultado da v2 é dentro da amostra.}",
          r"\end{table}", ""]
    return "\n".join(L)


def tabela_categorias(res: dict[str, Any]) -> str:
    cfgs = res["medidas"].get("lote", {})
    if not cfgs:
        return ""
    cols = [k for k in CONFIGS if k in cfgs]
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{Acurácia por categoria no lote de validação (Gemma 4 E4B)}", r"\label{tab:lote_categorias}",
         r"\footnotesize", r"\begin{tabular}{|l|c|" + "c|" * len(cols) + "}", r"\hline",
         r"\textbf{Categoria} & \textbf{n} & " + " & ".join(rf"\textbf{{{CONFIGS[k][1]}}}" for k in cols) + r" \\",
         r"\hline"]
    nomes = dict(report.CATEGORIA_TABELA)
    primeiro = cfgs[cols[0]]
    for c in CATEGORIAS:
        n = primeiro["por_categoria"][c]["n"]
        if not n:
            continue
        L.append(f"{nomes[c]} & {n} & " + " & ".join(report._pct(cfgs[k]["por_categoria"][c]["acuracia"])
                                                    for k in cols) + r" \\")
    L += [r"\hline", r"\textbf{Todas} & " + str(primeiro["n"]) + " & " + " & ".join(
        rf"\textbf{{{report._pct(cfgs[k]['acuracia'])}}}" for k in cols) + r" \\", r"\hline", r"\end{tabular}",
          r"\fonte{Elaborado pelos autores. Uma consulta pode pertencer a mais de uma categoria. Subespecificadas: "
          r"buscar sem filtros ou não buscar são ambos corretos.}", r"\end{table}", ""]
    return "\n".join(L)


def tabela_campos(res: dict[str, Any]) -> str:
    cfgs = res["medidas"].get("lote", {})
    if not cfgs:
        return ""
    cols = [k for k in CONFIGS if k in cfgs]
    L = [r"\begin{table}[htbp!]", r"\centering", r"\caption{F1 por campo no lote de validação (Gemma 4 E4B)}",
         r"\label{tab:lote_campos}", r"\footnotesize", r"\begin{tabular}{|l|c|" + "c|" * len(cols) + "}", r"\hline",
         r"\textbf{Campo} & \textbf{Ocorr.} & " + " & ".join(rf"\textbf{{{CONFIGS[k][1]}}}" for k in cols) + r" \\",
         r"\hline"]
    for campo in schema.CAMPOS:
        oc = max(cfgs[k]["por_campo"][campo]["ocorrencias"] for k in cols)
        L.append(rf"\texttt{{{campo}}} & {oc} & " + " & ".join(report._f(cfgs[k]["por_campo"][campo]["f1"])
                                                              for k in cols) + r" \\")
    L += [r"\hline", r"\textbf{Ponderado} & & " + " & ".join(rf"\textbf{{{report._f(cfgs[k]['f1'])}}}" for k in cols)
          + r" \\", r"\textbf{Macro} & & " + " & ".join(report._f(cfgs[k]["f1macro"]) for k in cols) + r" \\",
          r"\hline", r"\end{tabular}", r"\fonte{Elaborado pelos autores. Ocorr.: ocorrências do campo no gabarito "
          r"(a maior entre as configurações, porque os campos opcionais contam quando emitidos).}",
          r"\end{table}", ""]
    return "\n".join(L)


def tabela_pares(res: dict[str, Any]) -> str:
    nomes_par = {"tc1se1": "TC v1 × SE v1", "tc2se2": "TC v2 × SE v2", "tc1tc2": "TC v1 × TC v2",
                 "se1se2": "SE v1 × SE v2", "tc1se2": "TC v1 × SE v2"}
    L = [r"\begin{table}[htbp!]", r"\centering", r"\caption{Comparações pareadas (Gemma 4 E4B)}",
         r"\label{tab:lote_pares}", r"\footnotesize", r"\ajustartabela{%",
         r"\begin{tabular}{|l|l|c|c|c|c|c|}", r"\hline",
         r"\textbf{Conjunto} & \textbf{Par (A × B)} & \textbf{Só A} & \textbf{Só B} & \textbf{\textit{p}} & "
         r"\textbf{B $-$ A, acurácia (IC)} & \textbf{B $-$ A, F1 (IC)} \\", r"\hline"]
    for conjunto, rotulo in (("lote", "Lote"), ("base", "310")):
        for par, c in res["pares"].get(conjunto, {}).items():
            L.append(f"{rotulo} & {nomes_par[par]} & {c['so_a']} & {c['so_b']} & {_p(c['p'])} & "
                     f"{_pp(c['dif_acc'])} p.p. ({_ic_pp(c['ic_dif_acc'])}) & "
                     f"{report._f(c['dif_f1'])} ({report._f(c['ic_dif_f1'][0])} a {report._f(c['ic_dif_f1'][1])}) \\\\")
        L.append(r"\hline")
    L += [r"\end{tabular}}", r"\fonte{Elaborado pelos autores. Só A / Só B: consultas em que só uma das "
          r"configurações acerta. \textit{p}: McNemar exato, uma observação por consulta. IC: bootstrap pareado "
          r"(2.000 reamostragens das consultas), percentis 2,5 e 97,5. TC: \textit{Tool Calling}; SE: Saída "
          r"Estruturada.}", r"\end{table}", ""]
    return "\n".join(L)


def relatorio_md(res: dict[str, Any]) -> str:
    L = ["# Lote de validação e especificação v2 — Gemma 4 E4B", "",
         "Gerado por `python -m pfc_busca.evaluation.lote`. Metodologia: `docs/lote_validacao.md`.", ""]
    for conjunto, titulo in (("lote", "Lote de validação"), ("base", "310 consultas")):
        cfgs = res["medidas"].get(conjunto, {})
        if not cfgs:
            continue
        L += [f"## {titulo}", "", "| Medida | " + " | ".join(CONFIGS[k][1] for k in cfgs) + " |",
              "|---|" + "---|" * len(cfgs)]

        def linha(nome: str, f, cfgs=cfgs) -> str:
            return f"| {nome} | " + " | ".join(f(m) for m in cfgs.values()) + " |"

        L += [linha("Consultas", lambda m: str(m["n"])),
              linha("Acurácia [IC 95%]", lambda m: f"{report._pct_md(m['acuracia'])} "
                    f"[{report._pct_md(m['ic'][0])}–{report._pct_md(m['ic'][1])}]"),
              linha("Acurácia no domínio (fora de F e E)", lambda m: report._pct_md(m["accdominio"])),
              linha("F1 ponderado / macro / micro", lambda m: f"{m['f1']:.3f} / {m['f1macro']:.3f} / {m['f1micro']:.3f}"),
              linha("Recusa: recall (recusa F)", lambda m: report._pct_md(m["recusa"]["recall"])),
              linha("Recusa: precisão", lambda m: report._pct_md(m["recusa"]["precisao"])),
              linha("Recusa: F1", lambda m: f"{m['recusa']['f1']:.3f}"),
              linha("Falsa recusa (domínio)", lambda m: report._pct_md(m["recusa"]["falsa"])),
              linha("E: buscou sem filtros / não buscou / buscou com filtro (erro)",
                    lambda m: (f"{m['subespecificadas']['sem_parametros']} / {m['subespecificadas']['nao_buscou']} / "
                               f"{m['subespecificadas']['com_parametros']}") if m["subespecificadas"]["n"] else "—"),
              linha("Acurácia, uma leitura", lambda m: report._pct_md(m["leituras"]["unica"]["acuracia"])),
              linha("Acurácia, múltiplas leituras", lambda m: report._pct_md(m["leituras"]["multiplas"]["acuracia"])),
              linha("Latência mediana (s)", lambda m: f"{(m['latmed'] or 0) / 1000:.2f}"),
              linha("Respostas fora do schema", lambda m: str(m["fora_do_schema"]))]
        L += ["", "| Categoria | " + " | ".join(CONFIGS[k][1] for k in cfgs) + " |", "|---|" + "---|" * len(cfgs)]
        for c in CATEGORIAS:
            if next(iter(cfgs.values()))["por_categoria"][c]["n"]:
                L.append(linha(f"{report.NOMES_CATEGORIA[c]} (n={next(iter(cfgs.values()))['por_categoria'][c]['n']})",
                               lambda m, c=c: report._pct_md(m["por_categoria"][c]["acuracia"])))
        L += ["", "| Campo | " + " | ".join(CONFIGS[k][1] for k in cfgs) + " |", "|---|" + "---|" * len(cfgs)]
        for campo in schema.CAMPOS:
            L.append(linha(f"`{campo}`", lambda m, campo=campo: (
                f"{m['por_campo'][campo]['f1']:.3f} (P {m['por_campo'][campo]['precisao']:.2f}, "
                f"R {m['por_campo'][campo]['recall']:.2f})")))
        primeira = next(iter(cfgs.values()))
        if primeira["por_registro"]:
            L += ["", "| Registro | " + " | ".join(CONFIGS[k][1] for k in cfgs) + " |", "|---|" + "---|" * len(cfgs)]
            for r in primeira["por_registro"]:
                L.append(linha(f"{r} (n={primeira['por_registro'][r]['n']})",
                               lambda m, r=r: report._pct_md(m["por_registro"][r]["acuracia"])))
        if primeira["por_subtipo"]:
            L += ["", "| Subtipo | " + " | ".join(CONFIGS[k][1] for k in cfgs) + " |", "|---|" + "---|" * len(cfgs)]
            for s in primeira["por_subtipo"]:
                L.append(linha(f"{s} (n={primeira['por_subtipo'][s]['n']})",
                               lambda m, s=s: report._pct_md(m["por_subtipo"][s]["acuracia"])))
        pares = res["pares"].get(conjunto, {})
        if pares:
            L += ["", "| Par (A × B) | Só A | Só B | p (McNemar) | B − A, acurácia [IC] | B − A, F1 [IC] |",
                  "|---|---|---|---|---|---|"]
            for par, c in pares.items():
                L.append(f"| {par} | {c['so_a']} | {c['so_b']} | {c['p']:.4g} | "
                         f"{100 * c['dif_acc']:+.1f} p.p. [{100 * c['ic_dif_acc'][0]:+.1f}, {100 * c['ic_dif_acc'][1]:+.1f}] | "
                         f"{c['dif_f1']:+.3f} [{c['ic_dif_f1'][0]:+.3f}, {c['ic_dif_f1'][1]:+.3f}] |")
        L.append("")
    return "\n".join(L)


def _serializavel(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: _serializavel(v) for k, v in x.items()}
    if isinstance(x, list | tuple):
        return [_serializavel(v) for v in x]
    if isinstance(x, np.floating | np.integer):
        return x.item()
    return x


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--paper", type=Path, help="diretório do texto (grava em DIR/tabelas)")
    args = p.parse_args(argv)
    res = gerar()
    if not res["medidas"]:
        print("nenhuma rodada do lote encontrada")
        return 0
    saida = DIR_RESULTADOS / "lote" / "consolidado"
    saida.mkdir(parents=True, exist_ok=True)
    arquivos = {"numeros_lote.tex": macros(res), "tab_lote.tex": tabela_principal(res),
                "tab_lote_categorias.tex": tabela_categorias(res), "tab_lote_campos.tex": tabela_campos(res),
                "tab_lote_pares.tex": tabela_pares(res)}
    for nome, conteudo in arquivos.items():
        (saida / nome).write_text(conteudo, encoding="utf-8")
        if args.paper:
            (args.paper / "tabelas").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(saida / nome, args.paper / "tabelas" / nome)
    (saida / "lote.md").write_text(relatorio_md(res), encoding="utf-8")
    (saida / "lote.json").write_text(json.dumps(_serializavel(res), ensure_ascii=False, indent=1), encoding="utf-8")
    contagem = Counter(f"{c}:{k}" for c, cfgs in res["medidas"].items() for k in cfgs)
    print(f"lote: {', '.join(sorted(contagem))} -> {saida}" + (f" e {args.paper / 'tabelas'}" if args.paper else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
