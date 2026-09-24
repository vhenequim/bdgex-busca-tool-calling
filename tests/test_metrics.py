"""Exemplos resolvidos à mão (Cap. 4, F5: 'validar o cálculo contra 5-10 exemplos pequenos')."""

import pytest

from pfc_busca.evaluation import metrics as m

TOPO = "SCN Carta Topográfica Matricial"


# --- comparação de campo --------------------------------------------------

@pytest.mark.parametrize("campo, esperado, predito, igual", [
    ("scale", "1:25.000", "1:25.000", True),
    ("scale", "1:25.000", "1:25000", False),            # enum: exato
    ("state", "São Paulo", "sao paulo", True),          # texto livre: normalizado
    ("keyword", "SF-22-Y-D", "sf 22 y d", True),
    ("keyword", "2901", 2901, False),                   # tipo errado
    ("limit", 5, 5, True),
    ("limit", 5, "5", False),
    ("limit", 1, True, False),                          # bool não é inteiro
    ("publicationPeriod", {"start": "2026-01-01", "end": "2026-12-31"},
     {"start": "2026-01-01", "end": "2026-12-31"}, True),
    ("publicationPeriod", {"start": "2026-01-01", "end": "2026-12-31"},
     {"start": "2026-01-01", "end": "2026-09-14"}, False),  # limite exato
    ("creationPeriod", {"end": "2019-12-31"}, {"end": "2019-12-31"}, True),
    ("creationPeriod", {"end": "2019-12-31"}, {"start": "2019-12-31"}, False),
    ("sortDirection", "ASC", "asc", False),
])
def test_campo_igual(campo, esperado, predito, igual):
    assert m.campo_igual(campo, esperado, predito) is igual


def test_iou_periodo():
    a = {"start": "2026-01-01", "end": "2026-12-31"}
    assert m.iou_periodo(a, a) == 1.0
    assert m.iou_periodo(a, {"start": "2026-01-01", "end": "2026-06-30"}) == pytest.approx(181 / 365)
    assert m.iou_periodo(a, {"start": "2027-01-01", "end": "2027-12-31"}) == 0.0
    assert m.iou_periodo(a, {"end": "2026-12-31"}) is None


# --- exemplo 1: tudo certo -------------------------------------------------

def test_caso_totalmente_correto():
    esperado = {"productType": TOPO, "state": "São Paulo"}
    aval = m.avaliar_caso(esperado, {"productType": TOPO, "state": "Sao Paulo"})
    assert aval.correto and aval.tp == {"productType", "state"} and not aval.fp and not aval.fn


# --- exemplo 2: campo inventado (consulta 4 da demo da VC) ----------------

def test_campo_inventado_e_fp_e_derruba_acuracia():
    esperado = {"scale": "1:25.000", "state": "Rio de Janeiro"}
    predito = {"scale": "1:25.000", "state": "Rio de Janeiro", "limit": 10,
               "productType": TOPO, "city": "Rio de Janeiro",
               "sortField": "creationDate", "sortDirection": "ASC"}
    aval = m.avaliar_caso(esperado, predito)
    assert not aval.correto
    assert aval.tp == {"scale", "state"}
    assert aval.fp == {"limit", "productType", "city", "sortField", "sortDirection"}
    assert aval.fn == set()
    assert aval.tipo_erro == "campo_inventado"


# --- exemplo 3: valor errado conta como FP, não FN (definição do Cap. 3) --

def test_valor_errado_e_fp():
    aval = m.avaliar_caso({"state": "São Paulo"}, {"city": "São Paulo"})
    assert aval.fp == {"city"} and aval.fn == {"state"} and aval.tipo_erro == "misto"
    aval2 = m.avaliar_caso({"scale": "1:25.000"}, {"scale": "1:50.000"})
    assert aval2.fp == {"scale"} and aval2.fn == set() and aval2.tipo_erro == "valor_errado"


# --- exemplo 4: omissão ----------------------------------------------------

def test_omissao_e_fn():
    aval = m.avaliar_caso({"productType": TOPO, "state": "São Paulo"}, {"state": "São Paulo"})
    assert aval.fn == {"productType"} and aval.tipo_erro == "campo_omitido"


# --- exemplo 5: não chamou quando devia -----------------------------------

def test_nao_chamou():
    aval = m.avaliar_caso({"state": "Pará"}, None)
    assert not aval.correto and aval.fn == {"state"} and aval.tipo_erro == "nao_chamou"


# --- exemplo 6: fronteira --------------------------------------------------

def test_fronteira_nao_chamar_e_correto():
    assert m.avaliar_caso({}, None, espera_tool_call=False).correto
    aval = m.avaliar_caso({}, {"state": "Brasil"}, espera_tool_call=False)
    assert not aval.correto and aval.fp == {"state"} and aval.tipo_erro == "chamou_sem_dever"


# --- exemplo 7: campo fora do schema --------------------------------------

def test_campo_fora_do_schema():
    aval = m.avaliar_caso({"state": "Pará"}, {"state": "Pará", "regiao": "Norte"})
    assert not aval.correto and aval.fora_do_schema == {"regiao"}
    assert aval.tipo_erro == "campo_fora_do_schema"


# --- precisão / recall / f1 -----------------------------------------------

def test_prf1():
    assert m.precisao_recall_f1(0, 0, 0) == (0.0, 0.0, 0.0)
    p, r, f1 = m.precisao_recall_f1(3, 1, 1)
    assert (p, r) == (0.75, 0.75) and f1 == pytest.approx(0.75)


# --- agregação resolvida à mão --------------------------------------------

def _linha(id_, esperado, predito, cats=("S",), origem="N", obs=False, etc=True, lat=100.0):
    return {"id": id_, "esperado_resolvido": esperado, "predito": predito,
            "espera_tool_call": etc, "observacional": obs, "categorias": list(cats),
            "origem": origem, "latencia_llm_ms": lat, "latencia_tool_ms": 5.0,
            "latencia_total_ms": lat + 5.0, "erro": None}


def test_agregar_exemplo_a_mao():
    linhas = [
        # 1) certo: state
        _linha("a", {"state": "Pará"}, {"state": "Pará"}, lat=100),
        # 2) errado: state omitido, scale certo
        _linha("b", {"state": "Pará", "scale": "1:25.000"}, {"scale": "1:25.000"}, cats=("C",), lat=200),
        # 3) errado: state certo + limit inventado
        _linha("c", {"state": "Pará"}, {"state": "Para", "limit": 3}, lat=300),
        # 4) observacional (fora das métricas principais)
        _linha("d", {}, None, obs=True, etc=False, lat=50),
    ]
    r = m.agregar(linhas)
    assert r["n_consultas"] == 3
    assert r["acuracia"] == pytest.approx(1 / 3)
    # state: tp=2 (a, c), fp=0, fn=1 (b) -> P=1, R=2/3, F1=0.8
    st = r["por_campo"]["state"]
    assert (st["tp"], st["fp"], st["fn"]) == (2, 0, 1)
    assert st["f1"] == pytest.approx(0.8)
    # scale: tp=1 -> F1=1 ; limit: fp=1, ocorrencias=0 -> F1=0 mas peso 0
    assert r["por_campo"]["scale"]["f1"] == 1.0
    assert r["por_campo"]["limit"]["fp"] == 1
    # ponderado: pesos state=3, scale=1 -> (0.8*3 + 1*1)/4 = 0.85
    assert r["f1_ponderado"] == pytest.approx(0.85)
    # micro: tp=3, fp=1, fn=1 -> P=0.75, R=0.75
    assert r["micro"]["tp"] == 3 and r["micro"]["fp"] == 1 and r["micro"]["fn"] == 1
    assert r["por_categoria"]["S"]["n"] == 2 and r["por_categoria"]["C"]["n"] == 1
    assert r["latencia_llm_ms"]["mediana"] == 200 and r["latencia_llm_ms"]["min"] == 100
    assert r["diagnosticos"]["tipos_erro"] == {"campo_omitido": 1, "campo_inventado": 1}
    assert r["observacionais"]["n"] == 1 and r["observacionais"]["acuracia"] == 1.0


# --- leituras múltiplas (manual de anotação, P3) ---------------------------

from pfc_busca.evaluation.gabarito import (  # noqa: E402
    expandir_trocas,
    opcional,
    resolver_gabarito,
    um_de,
)


def test_valor_alternativo_aceita_qualquer_um():
    esperado = {"state": "Ceará", "sortField": um_de("publicationDate", "creationDate"), "sortDirection": "DESC"}
    for campo in ("publicationDate", "creationDate"):
        aval = m.avaliar_caso(esperado, {"state": "Ceará", "sortField": campo, "sortDirection": "DESC"})
        assert aval.correto and aval.tp == {"state", "sortField", "sortDirection"}
    aval = m.avaliar_caso(esperado, {"state": "Ceará", "sortField": "nome", "sortDirection": "DESC"})
    assert not aval.correto and aval.fp == {"sortField"}


def test_campo_opcional():
    esperado = {"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": opcional(1)}
    sem_limite = {"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC"}
    aval = m.avaliar_caso(esperado, sem_limite)
    assert aval.correto and "limit" not in aval.ocorrencias and not aval.fn
    aval = m.avaliar_caso(esperado, {**sem_limite, "limit": 1})
    assert aval.correto and "limit" in aval.tp and "limit" in aval.ocorrencias
    aval = m.avaliar_caso(esperado, {**sem_limite, "limit": 5})
    assert not aval.correto and aval.fp == {"limit"}


def test_leitura_estrutural_alternativa():
    esperado = {"state": "São Paulo"}
    alternativas = expandir_trocas(esperado, [("state", "city")])
    assert alternativas == [{"city": "São Paulo"}]
    aval = m.avaliar_caso(esperado, {"city": "Sao Paulo"}, alternativas=alternativas)
    assert aval.correto and aval.leitura == 1 and aval.tp == {"city"}
    # emitir as duas coisas não é uma leitura aceita
    aval = m.avaliar_caso(esperado, {"city": "São Paulo", "state": "São Paulo"}, alternativas=alternativas)
    assert not aval.correto


def test_periodo_relativo_com_leituras():
    from datetime import date
    esperado = resolver_gabarito({"publicationPeriod": {"rel": "ano_corrente"}}, date(2026, 9, 24))
    for pred in ({"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-24"}):
        assert m.avaliar_caso(esperado, {"publicationPeriod": pred}).correto
    assert not m.avaliar_caso(esperado, {"publicationPeriod": {"start": "2025-09-24", "end": "2026-09-24"}}).correto


def test_nao_chamou_com_opcional_so_conta_obrigatorios():
    aval = m.avaliar_caso({"state": "Pará", "limit": opcional(1)}, None)
    assert aval.fn == {"state"} and aval.ocorrencias == {"state"}


def test_expandir_duas_trocas_gera_tres_alternativas():
    esperado = {"state": "Rio de Janeiro", "publicationPeriod": {"rel": "hoje"}}
    alts = expandir_trocas(esperado, [("state", "city"), ("publicationPeriod", "creationPeriod")])
    assert len(alts) == 3
