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

Configurações derivadas, simuladas post hoc sobre as rodadas (docs/lote_validacao.md, seção 9.5):
`hib` (duas etapas: o TC v2 decide, a SE v1 extrai) e `se1vazio` (SE v1 com o objeto vazio como
não busca), com as mesmas medidas e pares contra as configurações rodadas; e as medidas
complementares da síntese do lote (`analise_complementar`, `auditoria_complementar`).
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from functools import cache, lru_cache
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
        "accdominio": acc(dominio), "n_dominio": len(dominio),
        "recusa": {"tp": tp, "fp": fp, "fn": fn, "tn": len(dominio) - fp, "precisao": p_rec, "recall": r_rec,
                   "f1": f1_rec, "falsa": fp / len(dominio) if dominio else None, "n_fora": len(fora)},
        "subespecificadas": {"n": len(subesp), "sem_parametros": e_sem_param, "nao_buscou": len(subesp) - e_sem_param - e_com_param,
                             "com_parametros": e_com_param, "acuracia": acc(subesp)},
        "leituras": {"unica": {"n": len(unica), "acuracia": acc(unica)},
                     "multiplas": {"n": len(mult), "acuracia": acc(mult)}},
        "por_registro": {r: {"n": len(ids), "acuracia": acc(ids)} for r, ids in sorted(registros.items())},
        "por_subtipo": {s: {"n": len(ids), "acuracia": acc(ids)} for s, ids in sorted(subtipos.items())},
        "accnaof": acc(set(por_id) - fora),
        "latmed": (g["latencia_llm_ms"] or {}).get("mediana"),
        "latp95": (g["latencia_llm_ms"] or {}).get("p95"),
        "fora_do_schema": g["diagnosticos"]["respostas_fora_do_schema"],
        "erros_infra": g["diagnosticos"]["chamadas_com_erro"],
    }


PEDE_ESCLARECIMENTO = re.compile(
    r"preciso|precisa|poderia|pode(ria)? (me )?(informar|especificar|fornecer|dizer)|especifi|mais informa|informe"
    r"|forne[çc]a|esclare|confirm|qual (é|e) |quais s[ãa]o|voc[êe] (gostaria|quer|deseja)|por favor", re.I)


def diagnostico_v1(linhas: list[dict]) -> dict[str, int]:
    """Erros do Tool Calling v1 que motivaram a v2 (contagem por execução, métricas principais)."""

    def aceitos(lin: dict, campo: str) -> list:
        leituras = [lin["esperado_resolvido"]] + list(lin.get("alternativas_resolvidas") or [])
        return [v for le in leituras if campo in le for v in gabarito.valores_aceitos(le[campo])]

    d = Counter()
    for lin in linhas:
        d["execucoes"] += 1
        aval = metrics.avaliar_linha(lin)
        d["erradas"] += not aval.correto
        pred = lin["predito"]
        dominio = lin["espera_tool_call"] and not lin.get("aceita_nao_chamar")
        if pred is None:
            if dominio:
                d["naochamou"] += 1
                d["naochamouesclarece"] += bool(PEDE_ESCLARECIMENTO.search(lin.get("texto_resposta") or ""))
            continue
        if "productType" in pred and not aceitos(lin, "productType"):
            d["tipoinventado"] += 1
        for campo in ("publicationPeriod", "creationPeriod"):
            p = pred.get(campo)
            if isinstance(p, dict) and set(p) == {"start"} and p["start"] == lin["hoje"] and aceitos(lin, campo) \
                    and p not in aceitos(lin, campo):
                d["periodohoje"] += 1
        kw = pred.get("keyword")
        if isinstance(kw, str) and "keyword" in aval.fp:
            if kw.lower() in ("folha", "carta", "mapa") or any(
                    isinstance(a, str) and kw.upper().startswith(a.upper() + "-") for a in aceitos(lin, "keyword")):
                d["codigoalterado"] += 1
        if isinstance(pred.get("scale"), str) and re.fullmatch(r"1:\d{4,}", pred["scale"]):
            d["escalasemponto"] += 1
    return dict(d)


# ---------------------------------------------------------------------------
# Análise TC × SE: composição, contrafactual, extração condicional, efeitos da v2
# ---------------------------------------------------------------------------

def normalizar_saida(pred: dict[str, Any] | None) -> dict[str, Any] | None:
    """As três normalizações determinísticas (sem gabarito) dos erros de forma da v2: sigla → nome da UF,
    prefixo MI/INOM/folha/carta retirado da keyword, keyword genérica descartada."""
    from pfc_busca import ferramentas as F

    if pred is None:
        return None
    p = dict(pred)
    st = p.get("state")
    if isinstance(st, str):
        t, partes = st.strip(), st.strip().split()
        if t.upper() in F.UFS:
            p["state"] = F.UFS[t.upper()]
        elif partes and partes[0].upper() in F.UFS and F.norm(" ".join(partes[1:])) in F.NOMES_UF:
            p["state"] = F.NOMES_UF[F.norm(" ".join(partes[1:]))]
    kw = p.get("keyword")
    if isinstance(kw, str):
        sem = kw.strip()
        for _ in range(3):
            sem = F.PREFIXOS_CODIGO.sub("", sem).strip()
        if F.norm(sem) in F.PALAVRAS_GENERICAS or not F.norm(sem):
            p.pop("keyword")
        else:
            p["keyword"] = sem
    return p


def _correto_com(lin: dict, pred: dict | None) -> bool:
    return metrics.avaliar_caso(lin["esperado_resolvido"], pred, lin["espera_tool_call"],
                                lin.get("alternativas_resolvidas"), bool(lin.get("aceita_nao_chamar"))).correto


def _uma_por_id(linhas: list[dict]) -> dict[str, dict]:
    """Uma execução por consulta: a primeira cujo resultado coincide com o da maioria das repetições."""
    correto = report.correcao_por_id(linhas)
    saida = {}
    for i, ls in _por_id(linhas).items():
        saida[i] = next((x for x in ls if metrics.avaliar_linha(x).correto == correto[i]), ls[0])
    return saida


def _aceitos(lin: dict, campo: str) -> list:
    leituras = [lin["esperado_resolvido"]] + list(lin.get("alternativas_resolvidas") or [])
    return [v for le in leituras if campo in le for v in gabarito.valores_aceitos(le[campo])]


def efeitos_de_forma(linhas: list[dict]) -> dict[str, tuple[int, int]]:
    """(numerador, denominador) dos quatro efeitos colaterais da v2, por execução que buscou."""
    from pfc_busca import ferramentas as F

    d = {k: [0, 0] for k in ("sigla", "prefixo", "limite", "tipo")}
    re_mi = re.compile(r"\bmi[\s-]*\d", re.I)
    for lin in linhas:
        pred = lin["predito"]
        if pred is None or not (lin["espera_tool_call"] and not lin.get("aceita_nao_chamar")):
            continue
        st = pred.get("state")
        if isinstance(st, str):
            d["sigla"][1] += 1
            partes = st.strip().split()
            d["sigla"][0] += bool(partes) and partes[0].upper() in F.UFS
        if re_mi.search(lin["consulta"]) and isinstance(pred.get("keyword"), str):
            d["prefixo"][1] += 1
            d["prefixo"][0] += bool(re.match(r"^\s*mi\b", pred["keyword"], re.I))
        if not _aceitos(lin, "limit"):
            d["limite"][1] += 1
            d["limite"][0] += "limit" in pred
        if not _aceitos(lin, "productType"):
            d["tipo"][1] += 1
            d["tipo"][0] += "productType" in pred
    return {k: (v[0], v[1]) for k, v in d.items()}


def analise_abordagens(cfgs: dict[str, dict]) -> dict[str, Any]:
    """Medidas da discussão TC × SE num conjunto (cfgs: config -> {"linhas", "casos"})."""
    un = {k: _uma_por_id(v["linhas"]) for k, v in cfgs.items()}
    saida: dict[str, Any] = {}
    ids_f = {i for i, x in next(iter(un.values())).items() if not x["espera_tool_call"]}
    ids_dom = {i for i, x in next(iter(un.values())).items()
               if x["espera_tool_call"] and not x.get("aceita_nao_chamar")}
    ids_nf = set(next(iter(un.values()))) - ids_f
    for tc, se in (("tc1", "se1"), ("tc2", "se2")):
        if tc not in un or se not in un:
            continue
        a, b = un[tc], un[se]
        ok_a = {i: metrics.avaliar_linha(x).correto for i, x in a.items()}
        ok_b = {i: metrics.avaliar_linha(x).correto for i, x in b.items()}
        # ponto de equilíbrio da proporção de consultas F: acc_TC(p) = acc_SE(p)
        nf, f = sorted(ids_nf), sorted(ids_f)

        def pstar(nf_ids, f_ids, ok_a=ok_a, ok_b=ok_b):
            at = np.mean([ok_a[i] for i in nf_ids]) if nf_ids else 0.0
            asse = np.mean([ok_b[i] for i in nf_ids]) if nf_ids else 0.0
            ft = np.mean([ok_a[i] for i in f_ids]) if f_ids else 1.0
            fs = np.mean([ok_b[i] for i in f_ids]) if f_ids else 0.0
            den = (asse - at) + (ft - fs)
            return (asse - at) / den if den else float("nan")

        rng = np.random.default_rng(42)
        amostras = [pstar(list(rng.choice(nf, len(nf))), list(rng.choice(f, len(f))) if f else [])
                    for _ in range(REPETICOES_BOOTSTRAP)]
        saida[f"{tc}{se}"] = {
            "pstar": pstar(nf, f), "ic_pstar": tuple(np.nanpercentile(amostras, [2.5, 97.5])),
            "proporcao_f": len(f) / len(ok_a),
        }
        # quando as duas buscam, nas consultas do domínio
        ambos = [i for i in ids_dom if a[i]["predito"] is not None and b[i]["predito"] is not None]
        so_a = sum(1 for i in ambos if ok_a[i] and not ok_b[i])
        so_b = sum(1 for i in ambos if ok_b[i] and not ok_a[i])
        saida[f"{tc}{se}"].update({
            "ambos_n": len(ambos), "ambos_acc_tc": np.mean([ok_a[i] for i in ambos]) if ambos else None,
            "ambos_acc_se": np.mean([ok_b[i] for i in ambos]) if ambos else None,
            "ambos_p": report.mcnemar_exato(so_a, so_b), "ambos_soa": so_a, "ambos_sob": so_b})
        # contrafactual: o TC nas consultas do domínio em que não buscou, com a resposta da SE
        nao = [i for i in ids_dom if a[i]["predito"] is None]
        saida[f"{tc}{se}"].update({
            "falsas": len(nao), "falsas_se_acerta": sum(ok_b[i] for i in nao),
            "falsas_esclarece": sum(bool(PEDE_ESCLARECIMENTO.search(a[i].get("texto_resposta") or "")) for i in nao),
            "contrafactual": (sum(ok_a[i] for i in ids_dom if a[i]["predito"] is not None)
                              + sum(ok_b[i] for i in nao)) / len(ids_dom)})
    re_chamada = re.compile(r"\b(?:buscar_catalogo|recusar_consulta|pedir_esclarecimento)\s*[{(]")
    for k, x in un.items():
        saida[k] = {"chamadas_em_texto": sum(1 for lin in x.values() if lin["predito"] is None
                                             and re_chamada.search(lin.get("texto_resposta") or "")),
                    "malformadas": sum(1 for lin in x.values() if lin.get("classe_erro") == "args_invalidos"),
                    "efeitos": efeitos_de_forma(list(x.values())),
                    "acc_normalizada": np.mean([_correto_com(lin, normalizar_saida(lin["predito"]))
                                                for lin in x.values()]),
                    "acc_dominio_normalizada": np.mean([_correto_com(x[i], normalizar_saida(x[i]["predito"]))
                                                        for i in ids_dom])}
    return saida


ARQ_AUDITORIA_ERROS = Path(__file__).resolve().parents[3] / "data" / "lote_validacao" / "auditoria_erros.json"


def auditoria_erros() -> dict[str, Any] | None:
    """Proporções da auditoria dos erros do lote 1 (erro real / gabarito discutível / gabarito errado)."""
    if not ARQ_AUDITORIA_ERROS.exists():
        return None
    bruto = json.loads(ARQ_AUDITORIA_ERROS.read_text(encoding="utf-8"))["julgamentos"]
    saida: dict[str, Any] = {}
    todas = Counter()
    for cfg, casos in bruto.items():
        c = Counter(v["classe"] for v in casos.values())
        todas.update(c)
        saida[cfg] = {"n": len(casos), **{k: c.get(k, 0) for k in "abc"}}
    n = sum(todas.values())
    completo = json.loads(ARQ_AUDITORIA_ERROS.read_text(encoding="utf-8"))
    saida["sql"] = (completo.get("sql_das_respostas_erradas") or {}).get("por_configuracao") or {}
    saida["todas"] = {"n": n, **{k: todas.get(k, 0) for k in "abc"},
                      "ic_a": report.wilson(todas.get("a", 0), n), "ic_b": report.wilson(todas.get("b", 0), n),
                      "ic_c": report.wilson(todas.get("c", 0), n)}
    return saida


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
            "dif_f1": base_f1b - base_f1, "ic_dif_f1": tuple(np.percentile(dif_f1, [2.5, 97.5])),
            "f1_a": base_f1, "f1_b": base_f1b}


# ---------------------------------------------------------------------------
# Configurações derivadas: simulações post hoc sobre as rodadas existentes
# ---------------------------------------------------------------------------

DERIVADAS = {"hib": "Duas etapas (TC v2 decide, SE v1 extrai)", "se1vazio": "SE v1, objeto vazio = não busca"}
# (A, B) com a convenção de `comparar`: só A / só B acertam; diferença = B − A
PARES_DERIVADOS = [("se2", "hib"), ("se1", "hib"), ("tc2", "hib"), ("se1vazio", "hib"), ("se2norm", "hib")]


def duas_etapas(decisao: list[dict], extracao: list[dict]) -> list[dict]:
    """Arquitetura em duas etapas simulada com duas rodadas já feitas sobre as mesmas consultas.

    A primeira configuração decide (sem tool call = não busca: recusa ou esclarecimento); quando ela busca,
    valem os parâmetros da segunda. Uma execução por consulta de cada rodada (`_uma_por_id`); a linha
    resultante é a da extração, com `predito=None` quando a decisão não buscou. A latência é a soma das
    duas chamadas quando há busca (duas chamadas em série, sem cache nem sobreposição) e a da decisão
    quando não há.
    """
    dec, ext = _uma_por_id(decisao), _uma_por_id(extracao)
    saida = []
    for i, e in ext.items():
        d = dec.get(i)
        if d is None:
            continue
        lin = dict(e)
        if d["predito"] is None:
            lin.update(predito=None, texto_resposta=d.get("texto_resposta"),
                       latencia_llm_ms=d.get("latencia_llm_ms"), erro=d.get("erro"), classe_erro=d.get("classe_erro"))
        else:
            lat = (d.get("latencia_llm_ms"), e.get("latencia_llm_ms"))
            lin["latencia_llm_ms"] = None if None in lat else lat[0] + lat[1]
        saida.append(lin)
    return saida


def regra_objeto_vazio(linhas: list[dict]) -> list[dict]:
    """Saída Estruturada com a regra "resposta sem nenhum campo do schema ({} ou só chaves fora dele) = não
    buscar" (regra definida depois de ver os dados)."""
    return [{**lin, "predito": None} if lin["predito"] is not None
            and not any(k in schema.CAMPOS for k in lin["predito"]) else lin for lin in linhas]


def _com_predito(linhas: list[dict], f) -> list[dict]:
    return [{**lin, "predito": f(lin["predito"])} for lin in linhas]


def derivadas(cfgs: dict[str, dict]) -> dict[str, list[dict]]:
    saida: dict[str, list[dict]] = {}
    if "tc2" in cfgs and "se1" in cfgs:
        saida["hib"] = duas_etapas(cfgs["tc2"]["linhas"], cfgs["se1"]["linhas"])
    if "se1" in cfgs:
        saida["se1vazio"] = regra_objeto_vazio(cfgs["se1"]["linhas"])
    return saida


# ---------------------------------------------------------------------------
# Medidas complementares (síntese da análise do lote)
# ---------------------------------------------------------------------------

def _grupo(lin: dict) -> str:
    if not lin["espera_tool_call"]:
        return "F"
    return "E" if lin.get("aceita_nao_chamar") else "D"


def _n_obrigatorios(lin: dict) -> int:
    return sum(1 for v in (lin["esperado_resolvido"] or {}).values() if not gabarito.eh_opcional(v))


def _leituras(lin: dict) -> list[dict]:
    return [lin["esperado_resolvido"]] + list(lin.get("alternativas_resolvidas") or [])


def _pstar(ok_a: dict[str, bool], ok_b: dict[str, bool], nf: list[str], f: list[str]) -> dict[str, float]:
    """Ponto de equilíbrio da proporção de F entre A (melhor em F) e B (melhor fora de F)."""
    at = float(np.mean([ok_a[i] for i in nf])) if nf else 0.0
    ab = float(np.mean([ok_b[i] for i in nf])) if nf else 0.0
    fa = float(np.mean([ok_a[i] for i in f])) if f else 1.0
    fb = float(np.mean([ok_b[i] for i in f])) if f else 0.0
    den = (ab - at) + (fa - fb)
    return {"pstar": (ab - at) / den if den else float("nan"), "a_a": at, "a_b": ab, "f_a": fa, "f_b": fb,
            "propf": len(f) / (len(f) + len(nf)) if f or nf else float("nan")}


def fisher_exato(a: int, b: int, c: int, d: int) -> float:
    """p-valor bicaudal exato de Fisher da tabela 2×2 [[a, b], [c, d]]."""
    r1, c1, n = a + b, a + c, a + b + c + d

    def prob(x: int) -> float:
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)

    p0 = prob(a)
    return min(1.0, sum(p for x in range(max(0, r1 - (n - c1)), min(r1, c1) + 1)
                        if (p := prob(x)) <= p0 * (1 + 1e-9)))


# Forma das respostas sem busca do Tool Calling (critério do verificador da análise, por expressões regulares,
# em ordem de precedência): narra a chamada; delega a chamada ao usuário; nega na primeira frase (recusa);
# pede algo ao usuário (esclarecimento); outro.
_NARRA = re.compile(r"utilizarei a ferramenta|vou (usar|utilizar|chamar) a ferramenta|```json|irei (usar|utilizar)", re.I)
_DELEGA = re.compile(r"(por favor,? (utilize|use)|voc[êe] pode (usar|utilizar)) (a )?ferramenta", re.I)
_NEGA = re.compile(r"^\s*(n[ãa]o\b|infelizmente)", re.I)
_FALTA = re.compile(r"n[ãa]o foi (especificad|informad|fornecid)|n[ãa]o especific", re.I)
_PEDE = re.compile(r"preciso (saber|de mais|de informa|que)|precisaria|por favor|especifique|forne[çc]a|informe|me diga"
                   r"|poderia|voc[êe] (gostaria|tem|deseja|quer|se refere|est[áa])|confirme|verifique|qual (é|o|a) ", re.I)
_CHAMADA_EM_TEXTO = re.compile(r"(buscar_catalogo|recusar_consulta)\s*\{")


def forma_nao_busca(texto: str | None) -> str:
    t = (texto or "").strip()
    if not t:
        return "vazio"
    if _NARRA.search(t):
        return "narra"
    if _DELEGA.search(t):
        return "delega"
    m = re.search(r"[.!?](\s|$)", t)
    primeira = t[:m.end()] if m else t
    if _NEGA.search(primeira) and not _FALTA.search(primeira):
        return "recusa"
    if _PEDE.search(t) or t.endswith("?") or _FALTA.search(primeira):
        return "esclarecimento"
    return "outro"


# --- consequências na SQL de `tools.montar_sql`, sem banco: o ILIKE sobre os 27 nomes de UF e os 5.571
# municípios do IBGE (unaccent(lower(nome)) ILIKE unaccent(lower('%valor%'))) é reproduzido em Python.

ARQ_MUNICIPIOS = Path(__file__).resolve().parents[3] / "data" / "lote_validacao" / "ibge_municipios.json"


def _sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def _like(padrao: str, texto: str) -> bool:
    """LIKE do PostgreSQL (% e _ curingas, \\ escape), já sem caixa nem acento."""
    rx, k = [], 0
    while k < len(padrao):
        ch = padrao[k]
        if ch == "\\" and k + 1 < len(padrao):
            rx.append(re.escape(padrao[k + 1]))
            k += 1
        elif ch == "%":
            rx.append(".*")
        elif ch == "_":
            rx.append(".")
        else:
            rx.append(re.escape(ch))
        k += 1
    return re.fullmatch("".join(rx), texto, re.S) is not None


def _ilike_contem(valor: str, nome: str) -> bool:
    return _like(_sem_acento(f"%{valor}%"), _sem_acento(nome))


@cache
def _ufs_ilike(valor: str) -> frozenset[str]:
    from pfc_busca import ferramentas as F
    return frozenset(n for n in F.UFS.values() if _ilike_contem(valor, n))


@lru_cache(maxsize=1)
def _municipios() -> tuple[tuple[str, str], ...]:
    def uf(m: dict) -> str | None:
        for k in ("microrregiao", "regiao-imediata"):
            x = m.get(k) or {}
            x = x.get("mesorregiao") or x.get("regiao-intermediaria") or {}
            if x.get("UF"):
                return x["UF"]["nome"]
        return None
    bruto = json.loads(ARQ_MUNICIPIOS.read_text(encoding="utf-8"))
    return tuple((m["nome"], uf(m)) for m in bruto)


@cache
def _muns_ilike(valor: str) -> frozenset[tuple[str, str]]:
    return frozenset(m for m in _municipios() if _ilike_contem(valor, m[0]))


def _geo_efetivo(city: str | None, state: str | None) -> tuple[str, frozenset] | None:
    """Conjunto efetivo de municípios (com city) ou de UFs (só state) que a busca casa."""
    if city:
        ms = _muns_ilike(str(city))
        if state:
            us = _ufs_ilike(str(state))
            ms = frozenset(m for m in ms if m[1] in us)
        return ("mun", ms)
    return ("uf", _ufs_ilike(str(state))) if state else None


def _forma_uf(valor: Any) -> str:
    from pfc_busca import ferramentas as F
    if not isinstance(valor, str):
        return "outro"
    t = valor.strip()
    if len(t) == 2 and t.upper() in F.UFS:
        return "sigla"
    m = re.match(r"^([A-Za-z]{2})\b[\s\-–:(]+(.+?)\)?$", t)
    if m and m.group(1).upper() in F.UFS and schema.normalizar_texto(m.group(2)) == \
            schema.normalizar_texto(F.UFS[m.group(1).upper()]):
        return "sigla_nome"
    return "outro"


def efeitos_sql_sigla(linhas: list[dict]) -> dict[str, tuple[int, int]]:
    """state como sigla ou 'XX Nome' e o que o ILIKE sobre os nomes das UFs faz com ele.

    Por valor emitido (todas as buscas): não casa nenhuma UF / só uma UF errada / a certa e outras / só a
    certa. Nas buscas com state no gabarito, considerando também o município: busca vazia ou igual à do
    gabarito."""
    from pfc_busca import ferramentas as F
    c = Counter()
    vals = [lin["predito"]["state"] for lin in linhas if lin["predito"] is not None
            and _forma_uf(lin["predito"].get("state")) in ("sigla", "sigla_nome")]
    for v in vals:
        u, certo = _ufs_ilike(v), F.UFS[v.strip()[:2].upper()]
        c["nenhuma" if not u else "ampla" if len(u) >= 2 else "certa" if u == {certo} else "errada"] += 1
    xx = re.compile(r"^([A-Z]{2})\s+\S")
    mun = Counter()
    for lin in linhas:
        p = lin["predito"]
        if p is None or not lin["espera_tool_call"]:
            continue
        st = p.get("state")
        if not isinstance(st, str) or not st.strip() or not any("state" in le for le in _leituras(lin)):
            continue
        if not (st.strip().upper() in F.UFS or xx.match(st.strip())):
            continue
        mun["n"] += 1
        le = _leituras(lin)[metrics.avaliar_linha(lin).leitura]
        if "state" not in le:
            le = next(x for x in _leituras(lin) if "state" in x)
        cp = p.get("city")
        efetivo = _geo_efetivo(cp if isinstance(cp, str) and cp.strip() else None, st)
        cg = gabarito.valores_aceitos(le["city"])[0] if le.get("city") else None
        esperados = [_geo_efetivo(cg, v) for v in gabarito.valores_aceitos(le["state"])]
        mun["vazia" if efetivo is None or not efetivo[1] else "igual" if efetivo in esperados else "diferente"] += 1
    n = len(vals)
    return {"vazia": (c["nenhuma"], n), "errada": (c["errada"], n), "ampla": (c["ampla"], n),
            "certa": (c["certa"], n), "vaziamun": (mun["vazia"], mun["n"]), "igualmun": (mun["igual"], mun["n"])}


_STOP_FTS = {"a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "em", "no", "na", "nos", "nas"}


def _fts_aproximado(documento: str, consulta: str) -> bool:
    """Aproximação do texto_busca @@ websearch_to_tsquery('portuguese', ...): todos os termos da consulta
    (fora as palavras vazias mais comuns, sem radicalização) presentes no documento."""
    termos = set(re.findall(r"\w+", consulta.lower())) - _STOP_FTS
    return bool(termos) and termos <= set(re.findall(r"\w+", documento.lower()))


def _keyword_casa(keyword: str, codigo: str) -> bool:
    """Condição de keyword de `tools.montar_sql` para uma folha cujo código (MI ou INOM) ou nome é `codigo`."""
    from pfc_busca import tools
    mi = inom = None
    nome = "Rio Teste"
    if re.search(tools._REGEX_MI, codigo):
        mi = codigo
    elif re.search(tools._REGEX_INOM, codigo):
        inom = codigo
    else:
        nome = codigo
    if _fts_aproximado(f"{nome} {mi or ''} {inom or ''} Mapeamento Sistemático", keyword):
        return True
    if re.search(tools._REGEX_MI, keyword):
        return mi == keyword
    if re.search(tools._REGEX_INOM, keyword):
        return inom == keyword
    return _like(f"%{keyword}%".lower(), nome.lower())


_PREFIXO_SQL = re.compile(r"^(mi|inom|folha|carta)[\s-]+", re.I)


def efeito_sql_prefixo(linhas: list[dict]) -> tuple[int, int]:
    """(execuções erradas com keyword prefixada cuja busca não encontra a folha do gabarito, total delas)."""
    falha = n = 0
    for lin in linhas:
        kw = (lin["predito"] or {}).get("keyword")
        if not isinstance(kw, str) or not _PREFIXO_SQL.match(kw.strip()):
            continue
        a = metrics.avaliar_linha(lin)
        if a.correto or "keyword" not in a.fp:
            continue
        le = _leituras(lin)[a.leitura]
        if "keyword" not in le:
            continue
        n += 1
        falha += not _keyword_casa(kw, gabarito.valores_aceitos(le["keyword"])[0])
    return falha, n


def _mcnemar_em(ok_a: dict[str, bool], ok_b: dict[str, bool], ids: list[str]) -> dict[str, Any]:
    so_a = sum(1 for i in ids if ok_a[i] and not ok_b[i])
    so_b = sum(1 for i in ids if ok_b[i] and not ok_a[i])
    return {"n": len(ids), "so_a": so_a, "so_b": so_b, "p": report.mcnemar_exato(so_a, so_b),
            "dif": (so_b - so_a) / len(ids) if ids else None}


def analise_complementar(cfgs: dict[str, dict], der: dict[str, list[dict]], detalhe: bool = True) -> dict[str, Any]:
    """Medidas novas da síntese do lote num conjunto: falsa recusa por forma e por subgrupo, decomposição
    v1 → v2, saldos, extração quando as duas buscam, subconjunto comum, leituras múltiplas, registro,
    efeitos na SQL. Uma execução por consulta (`_uma_por_id`), como em `analise_abordagens`. Sem `detalhe`
    (nas 310), só as medidas de par que a síntese compara entre os conjuntos."""
    un = {k: _uma_por_id(v["linhas"]) for k, v in cfgs.items()}
    un.update({k: _uma_por_id(v) for k, v in der.items()})
    casos = next(iter(cfgs.values()))["casos"]
    ids = sorted(set.intersection(*(set(u) for u in un.values())))
    ref = next(iter(un.values()))
    grupo = {i: _grupo(ref[i]) for i in ids}
    dom = [i for i in ids if grupo[i] == "D"]
    ok = {k: {i: metrics.avaliar_linha(u[i]).correto for i in ids} for k, u in un.items()}
    busca = {k: {i: u[i]["predito"] is not None for i in ids} for k, u in un.items()}
    registro = {i: casos.get(i, {}).get("registro") for i in ids}
    out: dict[str, Any] = {"config": {}, "par": {}}

    def taxa_fr(k: str, sub: list[str]) -> tuple[int, int]:
        return sum(1 for i in sub if not busca[k][i]), len(sub)

    ncampos = {i: _n_obrigatorios(ref[i]) for i in dom}
    chaves = {i: set(ref[i]["esperado_resolvido"] or {}) for i in dom}
    for k in (k for k in un if k in CONFIGS and detalhe):
        m: dict[str, Any] = {}
        fr = {c: taxa_fr(k, [i for i in dom if c in ref[i]["categorias"]]) for c in "TM"}
        fr["1campo"] = taxa_fr(k, [i for i in dom if ncampos[i] == 1])
        fr["4campos"] = taxa_fr(k, [i for i in dom if ncampos[i] >= 4])
        fr["1campostate"] = taxa_fr(k, [i for i in dom if chaves[i] == {"state"}])
        fr["1campocity"] = taxa_fr(k, [i for i in dom if chaves[i] == {"city"}])
        if any(registro[i] for i in dom):
            dt = {i for i in dom if registro[i] in ("direto", "telegrafico")}
            fr["dirtel"] = taxa_fr(k, sorted(dt))
            fr["outros"] = taxa_fr(k, [i for i in dom if i not in dt])
            g = [i for i in dom if registro[i] in ("sem_acento", "telegrafico")]
            r = [i for i in dom if registro[i] not in ("sem_acento", "telegrafico")]
            a1, a2 = sum(ok[k][i] for i in g), sum(ok[k][i] for i in r)
            m["sematel"] = {"a": (a1, len(g)), "resto": (a2, len(r)),
                            "p": fisher_exato(a1, len(g) - a1, a2, len(r) - a2)}
        nao = [i for i in dom if not busca[k][i]]
        if nao:   # falsa recusa por subgrupo só onde a configuração deixa de buscar no domínio
            m["fr"] = fr
        if k.startswith("tc"):   # Tool Calling: a resposta sem busca é texto (ou a ferramenta de recusa, na v2)
            m["formas"] = dict(Counter(forma_nao_busca(un[k][i].get("texto_resposta")) for i in nao))
        if k.startswith("tc") and any("recusou" in (un[k][i].get("extras") or {}) for i in ids):
            ferr = {i for i in nao if (un[k][i].get("extras") or {}).get("recusou")}
            vaz = [i for i in nao if i not in ferr and _CHAMADA_EM_TEXTO.search(un[k][i].get("texto_resposta") or "")]
            m["fraldesc"] = {"ferramenta": len(ferr), "vazada": len(vaz), "texto": len(nao) - len(ferr) - len(vaz)}
        E = [i for i in ids if grupo[i] == "E"]
        if E:
            m["accEerro"] = sum(ok[k][i] and not (grupo[i] == "E" and not busca[k][i]) for i in ids) / len(ids)
        lista = [un[k][i] for i in ids]
        m["sigla_sql"] = efeitos_sql_sigla(lista)
        m["prefixo_sql"] = efeito_sql_prefixo(lista)
        out["config"][k] = m

    # v1: TC × SE -- decomposição da diferença no domínio e extração quando os dois buscam
    if {"tc1", "se1"} <= set(un):
        falsas = [i for i in dom if not busca["tc1"][i]]
        ambos = [i for i in dom if busca["tc1"][i] and busca["se1"][i]]
        nd = len(dom)
        g_f = sum(ok["se1"][i] - ok["tc1"][i] for i in falsas) / nd
        g_a = sum(ok["se1"][i] - ok["tc1"][i] for i in ambos) / nd
        g_t = sum(ok["se1"][i] - ok["tc1"][i] for i in dom) / nd
        c = comparar([un["tc1"][i] for i in ambos], [un["se1"][i] for i in ambos])
        nf, f = [i for i in ids if grupo[i] != "F"], [i for i in ids if grupo[i] == "F"]
        out["par"]["tc1se1"] = {"gapfalsas": g_f, "gapambos": g_a, "gaptotal": g_t,
                                "gapfalsasfracao": g_f / g_t if g_t else None,
                                "f1ambos": (c["f1_a"], c["f1_b"], c["dif_f1"], c["ic_dif_f1"]),
                                "pstar": _pstar(ok["tc1"], ok["se1"], nf, f)}
        if "se1vazio" in ok:
            out["par"]["tc1se1"]["pstarvazio"] = _pstar(ok["tc1"], ok["se1vazio"], nf, f)["pstar"]
        if "hib" in ok:
            out["par"]["se1hib"] = {"pstar": _pstar(ok["hib"], ok["se1"], nf, f)["pstar"]}
    if {"tc2", "se2"} <= set(un) and detalhe:
        ambos = [i for i in dom if busca["tc2"][i] and busca["se2"][i]]
        c = comparar([un["tc2"][i] for i in ambos], [un["se2"][i] for i in ambos])
        out["par"]["tc2se2"] = {"f1ambos": (c["f1_a"], c["f1_b"], c["dif_f1"], c["ic_dif_f1"])}
    # sigla da UF nas mesmas consultas (TC v2 × SE v2): domínio, estado no gabarito, as duas buscaram;
    # sigla = primeira palavra do valor de state é uma sigla de UF (o critério de `efeitos_de_forma`)
    if {"tc2", "se2"} <= set(un):
        from pfc_busca import ferramentas as F

        def _sigla(lin: dict) -> bool:
            st = lin["predito"].get("state")
            partes = st.strip().split() if isinstance(st, str) else []
            return bool(partes) and partes[0].upper() in F.UFS

        com_estado = [i for i in dom if busca["tc2"][i] and busca["se2"][i] and _aceitos(ref[i], "state")]
        s_tc = {i: _sigla(un["tc2"][i]) for i in com_estado}
        s_se = {i: _sigla(un["se2"][i]) for i in com_estado}
        out["par"].setdefault("tc2se2", {})["siglamesmas"] = {
            "tc2": sum(s_tc.values()), "se2": sum(s_se.values()), **_mcnemar_em(s_tc, s_se, com_estado)}
    # v1 → v2 no Tool Calling: o que consertou e o que quebrou
    if {"tc1", "tc2"} <= set(un):
        quebradas = [i for i in ids if ok["tc1"][i] and not ok["tc2"][i]]
        consertos = [i for i in ids if ok["tc2"][i] and not ok["tc1"][i]]
        certas_dom = [i for i in dom if ok["tc1"][i]]
        ambos = [i for i in ids if busca["tc1"][i] and busca["tc2"][i]]
        sem_tipo = [i for i in dom if busca["tc1"][i] and busca["tc2"][i] and not _aceitos(un["tc1"][i], "productType")]
        t1 = {i: "productType" in un["tc1"][i]["predito"] for i in sem_tipo}
        t2 = {i: "productType" in un["tc2"][i]["predito"] for i in sem_tipo}
        n = len(ids)
        out["par"]["tc1tc2"] = {
            "n": n, "frconsertadas": sum(1 for i in consertos if not busca["tc1"][i]),
            "camposconsertados": sum(1 for i in consertos if busca["tc1"][i]), "quebradas": len(quebradas),
            "quebradasE": sum(1 for i in quebradas if grupo[i] == "E"),
            "taxaquebra": (sum(1 for i in certas_dom if not ok["tc2"][i]), len(certas_dom)),
            "ambos": (len(ambos), sum(ok["tc1"][i] for i in ambos), sum(ok["tc2"][i] for i in ambos)),
            "tipomesmas": {"n": len(sem_tipo), "tc1": sum(t1.values()), "tc2": sum(t2.values()),
                           **_mcnemar_em(t1, t2, sem_tipo)} if detalhe else None,
            "dominio": _mcnemar_em(ok["tc1"], ok["tc2"], dom)}
    # v1 → v2 na Saída Estruturada: saldos por grupo e extração quando a se2 busca
    if {"se1", "se2"} <= set(un):
        saldo = {g_: sum(ok["se2"][i] - ok["se1"][i] for i in ids if grupo[i] == g_) if any(
            grupo[i] == g_ for i in ids) else None for g_ in "FED"}
        busc2 = [i for i in dom if busca["se2"][i]]
        out["par"]["se1se2"] = {"saldo": saldo, "buscouse": (len(busc2), sum(ok["se1"][i] for i in busc2),
                                                             sum(ok["se2"][i] for i in busc2)),
                                "dominio": _mcnemar_em(ok["se1"], ok["se2"], dom)}
    # subconjunto comum: consultas do domínio em que as quatro configurações buscaram
    if set(CONFIGS) <= set(un) and detalhe:
        comum = [i for i in dom if all(busca[k][i] for k in CONFIGS)]
        out["comum"] = {"n": len(comum), "acc": {k: sum(ok[k][i] for i in comum) / len(comum) for k in CONFIGS}
                        if comum else {},
                        "v1": _mcnemar_em(ok["tc1"], ok["se1"], comum), "v2": _mcnemar_em(ok["tc2"], ok["se2"], comum)}
    # leituras múltiplas: diferença das diferenças SE − TC (múltiplas − única), bootstrap estratificado
    fora = {i for i in ids if grupo[i] == "F"}
    conj_mult = {i for i in ids if i not in fora and _multiplas(ref[i])}
    mult = sorted(conj_mult)
    unica = sorted(i for i in ids if i not in fora and grupo[i] != "E" and i not in conj_mult)
    if mult and unica and detalhe:
        rng = np.random.default_rng(42)
        out["multiplas"] = {}
        for nome, tc, se in (("v1", "tc1", "se1"), ("v2", "tc2", "se2")):
            if not {tc, se} <= set(un):
                continue
            xm = np.array([ok[se][i] - ok[tc][i] for i in mult], float)
            xu = np.array([ok[se][i] - ok[tc][i] for i in unica], float)
            bm = xm[rng.integers(0, len(xm), (REPETICOES_BOOTSTRAP, len(xm)))].mean(axis=1)
            bu = xu[rng.integers(0, len(xu), (REPETICOES_BOOTSTRAP, len(xu)))].mean(axis=1)
            out["multiplas"][nome] = (xm.mean() - xu.mean(), tuple(np.percentile(bm - bu, [2.5, 97.5])))
    return out


# ---------------------------------------------------------------------------
# Auditoria: convenções não informadas, SQL das respostas erradas e critérios da classe b
# ---------------------------------------------------------------------------

ARQ_AUDITORIA_CRITERIOS = ARQ_AUDITORIA_ERROS.parent / "auditoria_criterios.json"


def _correto_leituras(lin: dict, leituras: list[dict]) -> bool:
    return metrics.avaliar_caso(leituras[0], lin["predito"], lin["espera_tool_call"], leituras[1:],
                                bool(lin.get("aceita_nao_chamar"))).correto


def _convencoes() -> dict[str, tuple]:
    """Convenções do gabarito que a descrição v1 não informa ao modelo (critério de seleção, alargamento
    do gabarito que aceita a leitura natural). K3 é a regra 6.3 do manual (UF junto do município)."""
    N = schema.normalizar_texto

    def k1(lin):   # 'atualização' → creationDate
        return "atualiza" in N(lin["consulta"]) and lin["esperado"].get("sortField") == "creationDate"

    def k1f(L, lin):
        return [{**le, "sortField": {"$um_de": gabarito.valores_aceitos(le["sortField"]) + ["publicationDate"]}}
                if "sortField" in le else dict(le) for le in L]

    def _fechado(le, hoje):
        for f in ("publicationPeriod", "creationPeriod"):
            if f in le:
                vs = gabarito.valores_aceitos(le[f])
                if all(isinstance(v, dict) and "end" in v for v in vs) and any(
                        v.get("end") == hoje and v.get("start") for v in vs):
                    return True
        return False

    def k2(lin):   # fim obrigatório nos períodos 'até hoje'
        return lin["espera_tool_call"] and _fechado(lin["esperado_resolvido"], lin["hoje"])

    def k2f(L, lin):
        saida = []
        for le in L:
            le = dict(le)
            for f in ("publicationPeriod", "creationPeriod"):
                if f in le:
                    vs = gabarito.valores_aceitos(le[f])
                    le[f] = {"$um_de": vs + [{"start": v["start"]} for v in vs if v.get("end") == lin["hoje"] and v.get("start")]}
            saida.append(le)
        return saida

    def k3(lin):   # UF junto do município sem a UF escrita na consulta
        e = lin["esperado_resolvido"]
        return "city" in e and "state" in e and all(
            N(v) not in N(lin["consulta"]) for v in gabarito.valores_aceitos(e["state"]))

    def k3f(L, lin):
        return [{k: ({"$opcional": v} if k == "state" else v) for k, v in le.items()} for le in L]

    def k4(lin):   # 'cartas X' telegráfico só como city
        c = lin["esperado_resolvido"].get("city")
        if not isinstance(c, str) or any("keyword" in le for le in _leituras(lin)):
            return False
        return re.search(r"\b(cartas?|mapas?|folhas?)\s+" + re.escape(N(c)) + r"\b", N(lin["consulta"])) is not None

    def k4f(L, lin):
        extra = []
        for le in L:
            if "city" in le:
                d = dict(le)
                d["keyword"] = d.pop("city")
                extra.append(d)
        return L + extra

    def k5(lin):   # escala qualitativa com valor obrigatório
        e = lin["esperado_resolvido"]
        return "scale" in e and gabarito.eh_um_de(e["scale"]) and len(gabarito.valores_aceitos(e["scale"])) >= 5

    def k5f(L, lin):
        return [{k: ({"$opcional": v} if k == "scale" else v) for k, v in le.items()} for le in L]

    return {"K1": (k1, k1f), "K2": (k2, k2f), "K3": (k3, k3f), "K4": (k4, k4f), "K5": (k5, k5f)}


def _sql_efetiva(p: dict, hoje: str, datas: bool) -> tuple:
    """Filtros efetivos da busca; com `datas`, fim >= hoje vale como aberto e início <= 1900-01-01 também."""
    r: dict[str, Any] = {}
    kw = p.get("keyword")
    r["kw"] = kw.strip().lower() if isinstance(kw, str) and kw.strip() else None
    for f in ("scale", "productType", "project", "supplyArea"):
        r[f] = p.get(f) or None
    for f in ("publicationPeriod", "creationPeriod"):
        per, s, e = p.get(f), None, None
        if isinstance(per, dict) and per:
            s, e = per.get("start") or None, per.get("end") or None
            if datas:
                if e and str(e) >= hoje:
                    e = None
                if s and str(s) <= "1900-01-01":
                    s = None
        r[f] = (s, e) if (s or e) else None
    c, st = p.get("city"), p.get("state")
    r["geo"] = _geo_efetivo(c or None, st or None) if (c or st) else None
    lim = p.get("limit")
    lim = lim if isinstance(lim, int) and lim > 0 else 10
    r["ordem"] = ("c" if p.get("sortField") == "creationDate" else "p",
                  "ASC" if str(p.get("sortDirection", "DESC")).upper() == "ASC" else "DESC", min(lim, 100))
    return tuple(sorted(r.items()))


def _concretas(le: dict):
    campos = list(le)
    opcoes = []
    for c in campos:
        v = le[c]
        o = list(gabarito.valores_aceitos(v))
        if gabarito.eh_opcional(v):
            o = [None, *o]
        opcoes.append(o)
    for comb in itertools.product(*opcoes):
        yield {c: x for c, x in zip(campos, comb, strict=True) if x is not None}


def classe_sql(lin: dict) -> str:
    """Busca de uma execução errada comparada com a das leituras aceitas: sql_identica, equivalente sem
    aproximação de datas, equivalente só com as aproximações de datas, diferente (ou não buscou / buscou em F)."""
    from pfc_busca import tools
    if lin["predito"] is None:
        return "nao_buscou"
    if not lin["espera_tool_call"]:
        return "buscou_em_F"
    p = lin["predito"]
    sp, e1, e0 = tools.montar_sql(p), _sql_efetiva(p, lin["hoje"], True), _sql_efetiva(p, lin["hoje"], False)
    ident = eq0 = eq1 = False
    for le in _leituras(lin):
        for c in _concretas(le):
            ident |= tools.montar_sql(c) == sp
            eq0 |= _sql_efetiva(c, lin["hoje"], False) == e0
            eq1 |= _sql_efetiva(c, lin["hoje"], True) == e1
    return "sql_identica" if ident else "equiv_sem_datas" if eq0 else "equiv_com_datas" if eq1 else "diferente"


def auditoria_complementar(cfgs: dict[str, dict]) -> dict[str, Any]:
    """No lote: convenções não informadas (conversões se a leitura natural fosse aceita), SQL das respostas
    erradas sem as aproximações de datas e a classe b da auditoria sob os critérios estrito e amplo."""
    un = {k: _uma_por_id(v["linhas"]) for k, v in cfgs.items() if k in CONFIGS}
    if "tc1" not in un:
        return {}
    ids = sorted(un["tc1"])
    K = _convencoes()
    kid = {k: {i for i in ids if f(un["tc1"][i])} for k, (f, _) in K.items()}
    saida: dict[str, Any] = {"conv_n": len(kid["K1"] | kid["K2"] | kid["K4"] | kid["K5"]), "convuf_n": len(kid["K3"]),
                             "config": {}}
    convertidas: dict[str, set[str]] = {}
    for c, u in un.items():
        corretas = sum(metrics.avaliar_linha(x).correto for x in u.values())
        vira = {k: {i for i in kid[k] if u[i]["predito"] is not None and not metrics.avaliar_linha(u[i]).correto
                    and _correto_leituras(u[i], fl(_leituras(u[i]), u[i]))} for k, (_, fl) in K.items()}
        v4 = vira["K1"] | vira["K2"] | vira["K4"] | vira["K5"]
        convertidas[c] = v4 | vira["K3"]
        classes = Counter(classe_sql(x) for x in u.values() if not metrics.avaliar_linha(x).correto)
        erradas = sum(classes.values())
        saida["config"][c] = {"n": len(u), "corretas": corretas, "conv": len(v4), "convuf": len(v4 | vira["K3"]),
                              "sql": dict(classes), "erradas": erradas,
                              "sqlinocuasemdata": (classes["sql_identica"] + classes["equiv_sem_datas"]) / erradas
                              if erradas else None}
    # classe b da auditoria: critério do analista (auditoria_erros.json), estrito e amplo
    if ARQ_AUDITORIA_ERROS.exists():
        julg = json.loads(ARQ_AUDITORIA_ERROS.read_text(encoding="utf-8"))["julgamentos"]
        estrito = {}
        if ARQ_AUDITORIA_CRITERIOS.exists():
            estrito = json.loads(ARQ_AUDITORIA_CRITERIOS.read_text(encoding="utf-8"))[
                "criterio_estrito"]["reclassificados_como_a"]
        b = {"analista": 0, "estrito": 0, "amplo": 0}
        for c, js in julg.items():
            for i, v in js.items():
                eh_b = v["classe"] == "b"
                b["analista"] += eh_b
                b["estrito"] += eh_b and i not in estrito.get(c, {})
                inocua = c in un and classe_sql(un[c][i]) in ("sql_identica", "equiv_sem_datas", "equiv_com_datas")
                b["amplo"] += eh_b or inocua or i in convertidas.get(c, set())
        saida["b"] = b
        saida["b_n"] = sum(len(js) for js in julg.values())
    return saida


# ---------------------------------------------------------------------------
# Saída
# ---------------------------------------------------------------------------

def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _pp(v: float) -> str:
    """Diferença em pontos percentuais, com sinal."""
    return ("+" if v > 0 else "") + f"{100 * v:.1f}".replace(".", ",")


def _ic_pp(ic: tuple[float, float]) -> str:
    return f"{_pp(ic[0])} a {_pp(ic[1])}"


def _p(pv: float) -> str:
    return r"$<$\,0,001" if pv < 0.001 else report._f(pv, 3)


def _razao(k: int, n: int) -> str:
    return f"{_milhar(k)}/{_milhar(n)}"


def _int_sinal(v: int | None) -> str:
    return "---" if v is None else ("+" if v > 0 else "") + _milhar(v)


def _macros_complementares(put, res: dict[str, Any]) -> None:
    """Macros das medidas novas da síntese do lote (ver `analise_complementar` e `auditoria_complementar`)."""

    def pct_n(conj: str, cfg: str, nome: str, k: int, n: int) -> None:
        put(conj, cfg, nome, report._pct(k / n) if n else "---")
        put(conj, cfg, nome + "n", _razao(k, n))

    def f1_ambos(conj: str, par: str, x: tuple) -> None:
        f1a, f1b, dif, ic = x
        put(conj, par, "f1ambostc", report._f(f1a))
        put(conj, par, "f1ambosse", report._f(f1b))
        put(conj, par, "f1ambosdif", report._f(dif))
        put(conj, par, "icf1ambos", f"{report._f(ic[0])} a {report._f(ic[1])}")

    def mcnemar(conj: str, cfg: str, nome: str, d: dict) -> None:
        put(conj, cfg, nome, _pp(d["dif"]) if d["dif"] is not None else "---")
        put(conj, cfg, nome + "soa", str(d["so_a"]))
        put(conj, cfg, nome + "sob", str(d["so_b"]))
        put(conj, cfg, nome + "p", _p(d["p"]))

    formas = (("falsasesclarecimento", "esclarecimento"), ("falsasrecusa", "recusa"), ("falsasdelega", "delega"),
              ("falsasnarra", "narra"), ("falsasoutro", "outro"))
    for conj, x in (res.get("complementar") or {}).items():
        for k, m in x["config"].items():
            for sub, (a, n) in (m.get("fr") or {}).items():
                pct_n(conj, k, "fr" + sub, a, n)
            if "sematel" in m:
                s = m["sematel"]
                pct_n(conj, k, "sematel", *s["a"])
                pct_n(conj, k, "sematelresto", *s["resto"])
                put(conj, k, "sematelp", _p(s["p"]))
            if k == "tc1":   # forma das falsas recusas do Tool Calling v1 (texto da resposta)
                for nome, chave in formas:
                    put(conj, k, nome, _milhar(m["formas"].get(chave, 0)))
            if "fraldesc" in m:
                for chave, v in m["fraldesc"].items():
                    put(conj, k, "fraldesc" + chave, str(v))
            if "accEerro" in m:
                put(conj, k, "accEerro", report._pct(m["accEerro"]))
            for nome, (a, n) in (m.get("sigla_sql") or {}).items():
                if n:   # só onde há sigla emitida
                    pct_n(conj, k, "siglasql" + nome, a, n)
            if m.get("prefixo_sql", (0, 0))[1]:
                pct_n(conj, k, "prefixosqlfalha", *m["prefixo_sql"])
        par = x["par"]
        if "tc1se1" in par:
            p = par["tc1se1"]
            for nome in ("gapfalsas", "gapambos", "gaptotal"):
                put(conj, "tc1se1", nome, _pp(p[nome]))
            put(conj, "tc1se1", "gapfalsasfracao", report._pct(p["gapfalsasfracao"]))
            f1_ambos(conj, "tc1se1", p["f1ambos"])
            if "pstarvazio" in p:
                put(conj, "tc1se1", "pstarvazio", report._pct(p["pstarvazio"]))
        if "se1hib" in par:
            put(conj, "se1hib", "pstar", report._pct(par["se1hib"]["pstar"]))
        if "tc2se2" in par:
            if "f1ambos" in par["tc2se2"]:
                f1_ambos(conj, "tc2se2", par["tc2se2"]["f1ambos"])
            sm = par["tc2se2"].get("siglamesmas")
            if sm:   # sigla nas mesmas consultas: só A = só o TC v2 escreveu a sigla
                put(conj, "tc2se2", "siglamesmasn", _milhar(sm["n"]))
                pct_n(conj, "tc2", "siglamesmas", sm["tc2"], sm["n"])
                pct_n(conj, "se2", "siglamesmas", sm["se2"], sm["n"])
                put(conj, "tc2se2", "siglamesmassoa", str(sm["so_a"]))
                put(conj, "tc2se2", "siglamesmassob", str(sm["so_b"]))
                put(conj, "tc2se2", "siglamesmasp", _p(sm["p"]))
        if "tc1tc2" in par:
            p = par["tc1tc2"]
            n = p["n"]
            for nome, sinal in (("frconsertadas", 1), ("camposconsertados", 1), ("quebradas", -1), ("quebradasE", -1)):
                put(conj, "tc1tc2", nome, _milhar(p[nome]))
                put(conj, "tc1tc2", nome + "pp", _pp(sinal * p[nome] / n))
            pct_n(conj, "tc1tc2", "taxaquebra", *p["taxaquebra"])
            na, a1, a2 = p["ambos"]
            put(conj, "tc1tc2", "ambosn", _milhar(na))
            put(conj, "tc1tc2", "ambosacc1", report._pct(a1 / na) if na else "---")
            put(conj, "tc1tc2", "ambosacc2", report._pct(a2 / na) if na else "---")
            tm = p["tipomesmas"]
            if tm:
                pct_n(conj, "tc1", "tipomesmas", tm["tc1"], tm["n"])
                pct_n(conj, "tc2", "tipomesmas", tm["tc2"], tm["n"])
                put(conj, "tc1tc2", "tipomesmassoa", str(tm["so_a"]))
                put(conj, "tc1tc2", "tipomesmassob", str(tm["so_b"]))
                put(conj, "tc1tc2", "tipomesmasp", _p(tm["p"]))
            mcnemar(conj, "dominio", "tcv2menosv1", p["dominio"])
        if "se1se2" in par:
            p = par["se1se2"]
            for g_ in "FED":
                put(conj, "se1se2", "saldo" + g_, _int_sinal(p["saldo"][g_]))
            nb, k1, k2 = p["buscouse"]
            pct_n(conj, "se1se2", "buscouse1", k1, nb)
            pct_n(conj, "se1se2", "buscouse2", k2, nb)
            mcnemar(conj, "dominio", "sev2menosv1", p["dominio"])
        if "comum" in x:
            c = x["comum"]
            put(conj, "comum", "n", _milhar(c["n"]))
            for cfg, v in c["acc"].items():
                put(conj, "comum", "acc" + cfg, report._pct(v))
            for nome in ("v1", "v2"):
                put(conj, "comum", nome + "difacc", _pp(c[nome]["dif"]) if c[nome]["dif"] is not None else "---")
                put(conj, "comum", nome + "soa", str(c[nome]["so_a"]))
                put(conj, "comum", nome + "sob", str(c[nome]["so_b"]))
                put(conj, "comum", nome + "p", _p(c[nome]["p"]))
        for nome, (did, ic) in (x.get("multiplas") or {}).items():
            put(conj, "multiplas", "did" + nome, _pp(did))
            put(conj, "multiplas", "icdid" + nome, _ic_pp(ic))
    # acurácias da v1 com a proporção de consultas F do outro conjunto
    comp = {conj: x["par"]["tc1se1"]["pstar"] for conj, x in (res.get("complementar") or {}).items()
            if "tc1se1" in x["par"]}
    if {"lote", "base"} <= set(comp):
        for conj, outro in (("lote", "base"), ("base", "lote")):
            q, c = comp[outro]["propf"], comp[conj]
            put(conj, "tc1se1", "pstartrocatc", report._pct((1 - q) * c["a_a"] + q * c["f_a"]))
            put(conj, "tc1se1", "pstartrocase", report._pct((1 - q) * c["a_b"] + q * c["f_b"]))
            put(conj, "tc1se1", "pstartrocapropf", report._pct(q))
    aud = res.get("auditoria_complementar") or {}
    if aud:
        cf = aud["config"]
        for nome, chave in (("conv", "conv"), ("convuf", "convuf")):
            put("auditoria", nome, "n", _milhar(aud[chave + "_n"]))
            for c, a in cf.items():
                put("auditoria", nome, c, str(a[chave]))
                put("auditoria", nome, "acc" + c, report._pct((a["corretas"] + a[chave]) / a["n"]))
            if "tc1" in cf and "tc2" in cf:
                t1, t2 = cf["tc1"], cf["tc2"]
                put("auditoria", nome, "diftc", _pp((t2["corretas"] + t2[chave] - t1["corretas"] - t1[chave]) / t1["n"]))
        taxas = [a["sqlinocuasemdata"] for a in cf.values() if a["sqlinocuasemdata"] is not None]
        for c, a in cf.items():
            put("auditoria", c, "sqlinocuasemdata", report._pct(a["sqlinocuasemdata"]))
        if taxas:
            put("auditoria", "erros", "sqlinocuasemdata", f"{report._pct(min(taxas))} a {report._pct(max(taxas))}")
        if "b" in aud:
            put("auditoria", "erros", "bmin", str(aud["b"]["estrito"]))
            put("auditoria", "erros", "bmax", str(aud["b"]["amplo"]))
            put("auditoria", "erros", "amin", str(aud["b_n"] - aud["b"]["amplo"]))


def gerar() -> dict[str, Any]:
    dados: dict[str, dict[str, Any]] = {}
    for conjunto in CONJUNTOS:
        for config in CONFIGS:
            r = carregar(conjunto, config)
            if r is not None:
                dados.setdefault(conjunto, {})[config] = {"linhas": r[0], "casos": r[1]}
    resultado: dict[str, Any] = {"medidas": {}, "pares": {}, "auditoria_erros": auditoria_erros()}
    if "tc1" in dados.get("base", {}):
        resultado["diagnostico_v1"] = diagnostico_v1(dados["base"]["tc1"]["linhas"])
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
        resultado.setdefault("analise", {})[conjunto] = analise_abordagens(completos)
        # configurações derivadas (post hoc): duas etapas e regra do objeto vazio
        der = derivadas(completos)
        casos = next(iter(completos.values()))["casos"]
        resultado.setdefault("derivadas", {})[conjunto] = {k: medidas(v, casos) for k, v in der.items()}
        linhas = {**{k: v["linhas"] for k, v in completos.items()}, **der}
        if "se2" in completos:
            linhas["se2norm"] = _com_predito(completos["se2"]["linhas"], normalizar_saida)
        resultado.setdefault("pares_derivados", {})[conjunto] = {
            f"{a}{b}": comparar(linhas[a], linhas[b]) for a, b in PARES_DERIVADOS if a in linhas and b in linhas}
        resultado.setdefault("complementar", {})[conjunto] = analise_complementar(completos, der,
                                                                                 detalhe=conjunto == "lote")
        if conjunto == "lote":
            resultado["auditoria_complementar"] = auditoria_complementar(completos)
    return resultado


def macros(res: dict[str, Any]) -> str:
    defs: dict[str, str] = {}

    def put(rodada: str, chave: str, medida: str, valor: str) -> None:
        defs[f"res@{rodada}@{chave}@{medida}"] = valor

    aud = res.get("auditoria_erros") or {}
    if aud:
        t = aud["todas"]
        put("auditoria", "erros", "n", str(t["n"]))
        for k in "abc":
            put("auditoria", "erros", k, str(t[k]))
            put("auditoria", "erros", "pct" + k, report._pct(t[k] / t["n"]))
            put("auditoria", "erros", "ic" + k, f"{report._pct(t['ic_' + k][0])} a {report._pct(t['ic_' + k][1])}")
        for cfg in CONFIGS:
            if cfg in aud:
                put("auditoria", cfg, "a", f"{aud[cfg]['a']}/{aud[cfg]['n']}")
        sql = aud.get("sql") or {}
        if sql:
            taxas = {cfg: (s.get("equivalente", 0) + s.get("sql_identica", 0)) / s["erradas"] for cfg, s in sql.items()}
            for cfg, t in taxas.items():
                put("auditoria", cfg, "sqlinocua", report._pct(t))
            put("auditoria", "erros", "sqlinocuamax", report._pct(max(taxas.values())))
    for conjunto, an in (res.get("analise") or {}).items():
        for par in ("tc1se1", "tc2se2"):
            x = an.get(par)
            if not x:
                continue
            if par == "tc1se1":   # na v2 as duas recusam: o ponto de equilíbrio não se aplica
                put(conjunto, par, "pstar", report._pct(x["pstar"]))
                put(conjunto, par, "icpstar", f"{report._pct(x['ic_pstar'][0])} a {report._pct(x['ic_pstar'][1])}")
            put(conjunto, par, "propf", report._pct(x["proporcao_f"]))
            put(conjunto, par, "ambosn", _milhar(x["ambos_n"]))
            put(conjunto, par, "amboscc", report._pct(x["ambos_acc_tc"]))
            put(conjunto, par, "ambosse", report._pct(x["ambos_acc_se"]))
            put(conjunto, par, "ambosp", _p(x["ambos_p"]))
            put(conjunto, par, "ambossoa", str(x["ambos_soa"]))
            put(conjunto, par, "ambossob", str(x["ambos_sob"]))
            put(conjunto, par, "falsas", _milhar(x["falsas"]))
            put(conjunto, par, "falsasse", _milhar(x["falsas_se_acerta"]))
            put(conjunto, par, "falsasesclarece", _milhar(x["falsas_esclarece"]))
            put(conjunto, par, "contrafactual", report._pct(x["contrafactual"]))
        for k in CONFIGS:
            x = an.get(k)
            if not x:
                continue
            put(conjunto, k, "chamadastexto", str(x["chamadas_em_texto"]))
            put(conjunto, k, "malformadas", str(x["malformadas"]))
            put(conjunto, k, "accnormalizada", report._pct(x["acc_normalizada"]))
            put(conjunto, k, "domnormalizada", report._pct(x["acc_dominio_normalizada"]))
            for efeito, (num, den) in x["efeitos"].items():
                put(conjunto, k, efeito, report._pct(num / den) if den else "---")
                put(conjunto, k, efeito + "n", f"{num}/{_milhar(den)}")
    diag = res.get("diagnostico_v1") or {}
    for chave, valor in diag.items():
        put("diag", "tc1", chave, _milhar(valor))
    if diag.get("execucoes"):
        put("diag", "tc1", "pctnaochamou", report._pct(diag.get("naochamou", 0) / diag["execucoes"]))

    def por_config(conjunto: str, k: str, m: dict[str, Any]) -> None:
        put(conjunto, k, "n", _milhar(m["n"]))
        put(conjunto, k, "acuracia", report._pct(m["acuracia"]))
        put(conjunto, k, "ic", f"{report._pct(m['ic'][0])} a {report._pct(m['ic'][1])}")
        put(conjunto, k, "f1", report._f(m["f1"]))
        put(conjunto, k, "f1macro", report._f(m["f1macro"]))
        put(conjunto, k, "accdominio", report._pct(m["accdominio"]))
        put(conjunto, k, "ndominio", _milhar(m["n_dominio"]))
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
        put(conjunto, k, "latp95", report._num((m["latp95"] or 0) / 1000, 2))
        put(conjunto, k, "accnaof", report._pct(m["accnaof"]))
        r = m["recusa"]
        put(conjunto, k, "recusan", _razao(r["tp"], r["n_fora"]))
        put(conjunto, k, "recusaprecn", _razao(r["tp"], r["tp"] + r["fp"]))
        put(conjunto, k, "falsarecusan", _razao(r["fp"], m["n_dominio"]))

    def por_par(conjunto: str, par: str, cmp: dict[str, Any]) -> None:
        put(conjunto, par, "p", _p(cmp["p"]))
        put(conjunto, par, "soa", str(cmp["so_a"]))
        put(conjunto, par, "sob", str(cmp["so_b"]))
        put(conjunto, par, "difacc", _pp(cmp["dif_acc"]))
        put(conjunto, par, "icdifacc", _ic_pp(cmp["ic_dif_acc"]))
        put(conjunto, par, "diff", report._f(cmp["dif_f1"]))
        put(conjunto, par, "icdiff", f"{report._f(cmp['ic_dif_f1'][0])} a {report._f(cmp['ic_dif_f1'][1])}")

    for conjunto, cfgs in res["medidas"].items():
        for k, m in cfgs.items():
            por_config(conjunto, k, m)
        for par, cmp in res["pares"].get(conjunto, {}).items():
            por_par(conjunto, par, cmp)
    # configurações derivadas (duas etapas, regra do objeto vazio) e seus pares
    for conjunto, cfgs in (res.get("derivadas") or {}).items():
        for k, m in cfgs.items():
            por_config(conjunto, k, m)
        for par, cmp in (res.get("pares_derivados") or {}).get(conjunto, {}).items():
            por_par(conjunto, par, cmp)
    _macros_complementares(put, res)
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
    # a v2 é de dentro da amostra nas 310; diz-se se isso a tornou otimista ou não (o texto do Cap. 3 discute).
    # Compara-se com a v1 no mesmo conjunto (pareado), e não com o lote, cuja composição (17% de F) é outra.
    base = res["medidas"].get("base", {})
    pares_v = [(v2, v1) for v2, v1 in (("tc2", "tc1"), ("se2", "se1")) if v2 in base and v1 in base]
    if pares_v and all(base[a]["acuracia"] < base[b]["acuracia"] for a, b in pares_v):
        nota_v2 = ("nesse conjunto, o resultado da v2 é de dentro da amostra e, mesmo assim, ficou abaixo do da v1 "
                   "nas duas abordagens.")
    elif pares_v and all(base[a]["acuracia"] > base[b]["acuracia"] for a, b in pares_v):
        nota_v2 = "nesse conjunto, o resultado da v2 é de dentro da amostra e ficou acima do da v1 nas duas abordagens."
    else:
        nota_v2 = "nesse conjunto, o resultado da v2 é de dentro da amostra."
    L += [r"\end{tabular}}",
          r"\fonte{Elaborado pelos autores. Gemma 4 E4B, GPU T4. Acurácia por consulta, com IC de Wilson. "
          r"Recusa F: proporção das consultas fora do domínio sem busca (recall da recusa). Falsa recusa: "
          r"proporção das consultas do domínio (fora das categorias F e E) sem busca. F1 recusa: média harmônica "
          r"da precisão e do recall da recusa. Múltiplas leituras: acurácia nas consultas do domínio com mais de "
          r"uma leitura aceita. Na v1, a Saída Estruturada não tem como recusar. A v2 foi desenhada a partir dos "
          r"erros nas 310 consultas: " + nota_v2 + "}",
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


def tabela_duas_etapas(res: dict[str, Any]) -> str:
    """As duas configurações derivadas (simuladas post hoc) ao lado das quatro rodadas, nos dois conjuntos."""
    rotulos = {**{k: v[1] for k, v in CONFIGS.items()},
               "se1vazio": "SE v1, objeto vazio como não busca", "hib": "Duas etapas (TC v2 decide, SE v1 extrai)"}
    L = [r"\begin{table}[htbp!]", r"\centering",
         r"\caption{Arquitetura em duas etapas e regra do objeto vazio, simuladas com as rodadas do Gemma 4 E4B, "
         r"ao lado das quatro configurações executadas}",
         r"\label{tab:lote_duas_etapas}", r"\footnotesize", r"\ajustartabela{%",
         r"\begin{tabular}{|l|l|c|c|c|c|c|c|c|}", r"\hline",
         r"\textbf{Conjunto} & \textbf{Configuração} & \textbf{Acurácia} & \textbf{IC 95\%} & \textbf{Domínio} & "
         r"\textbf{Recusa F} & \textbf{Precisão da recusa} & \textbf{Falsa recusa} & \textbf{Latência (s)} \\",
         r"\hline"]
    nomes = {"lote": "Lote de validação", "base": "310 consultas"}
    for conjunto in ("lote", "base"):
        cfgs = {**res["medidas"].get(conjunto, {}), **(res.get("derivadas") or {}).get(conjunto, {})}
        ordem = [k for k in (*CONFIGS, "se1vazio", "hib") if k in cfgs]
        if not ordem:
            continue
        n = cfgs[ordem[0]]["n"]
        for j, k in enumerate(ordem):
            m, r = cfgs[k], cfgs[k]["recusa"]
            rotulo = rf"\multirow{{{len(ordem)}}}{{*}}{{\shortstack[l]{{{nomes[conjunto]}\\(n={n})}}}}" if j == 0 else ""
            prec = report._pct(r["precisao"]) if r["tp"] + r["fp"] else "---"
            if k == "se1vazio":
                L.append(r"\cline{2-9}")
            L.append(f"{rotulo} & {rotulos[k]} & {report._pct(m['acuracia'])} & "
                     f"{report._pct(m['ic'][0])}--{report._pct(m['ic'][1])} & {report._pct(m['accdominio'])} & "
                     f"{report._pct(r['recall'])} & {prec} & {report._pct(r['falsa'])} & "
                     f"{report._num((m['latmed'] or 0) / 1000, 2)} \\\\")
        L.append(r"\hline")
    L += [r"\end{tabular}}",
          r"\fonte{Elaborado pelos autores. Gemma 4 E4B, GPU T4. As duas últimas linhas de cada conjunto são "
          r"simulações \textit{post hoc} sobre as rodadas existentes, sem chamada nova ao modelo. Duas etapas: o "
          r"\textit{Tool Calling} v2 decide se busca; quando busca, valem os parâmetros da Saída Estruturada v1 na "
          r"mesma consulta, e a latência é a soma das duas chamadas. Objeto vazio como não busca: a resposta da "
          r"Saída Estruturada v1 sem nenhum campo do \textit{schema} conta como recusa (regra definida depois de "
          r"ver os dados). Acurácia com IC de Wilson. Domínio: acurácia fora das categorias F e E. Recusa F: "
          r"proporção das consultas fora do domínio sem busca. Precisão da recusa: proporção de consultas fora "
          r"do domínio entre as que ficaram sem busca (---: nenhuma ficou). Falsa recusa: proporção das consultas "
          r"do domínio sem busca. Latência: mediana. TC: \textit{Tool Calling}; SE: Saída Estruturada.}",
          r"\end{table}", ""]
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
                "tab_lote_pares.tex": tabela_pares(res), "tab_lote_duas_etapas.tex": tabela_duas_etapas(res)}
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
