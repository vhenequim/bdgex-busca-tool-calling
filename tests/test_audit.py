"""Auditoria do dataset: estatísticas de concordância, adjudicação e anotador por regras."""

import json

import pytest

from pfc_busca.evaluation import audit
from pfc_busca.evaluation import dataset_builder as db_


@pytest.fixture(scope="module")
def casos():
    return db_.carregar_dataset()


def test_kappa_cohen():
    assert audit.kappa_cohen([("a", "a"), ("b", "b")]) == 1.0
    # concordância igual ao acaso -> 0
    assert audit.kappa_cohen([("a", "a"), ("a", "b"), ("b", "a"), ("b", "b")]) == pytest.approx(0.0)
    # exemplo clássico: po = 0,7; pe = 0,5 -> 0,4
    pares = [("s", "s")] * 20 + [("s", "n")] * 5 + [("n", "s")] * 10 + [("n", "n")] * 15
    assert audit.kappa_cohen(pares) == pytest.approx(0.4)
    assert audit.kappa_cohen([]) is None


def test_comparacao_cobre_observacional_em_nao_chamar(casos):
    """Regressão: a divergência de 'observacional' precisa aparecer também em consultas 'não chamar'."""
    n36 = next(c for c in casos if c["id"] == "N36")
    anot = {"chamar_ferramenta": False, "observacional": True, "parametros": {}}
    assert any("observacional" in d for d in audit.comparar_anotacao(n36, anot))
    assert audit.comparar_anotacao(n36, {"chamar_ferramenta": False, "observacional": False, "parametros": {}}) == []


def test_adjudicacao_reconstroi_gabarito_anterior(casos):
    decisoes = audit.carregar_adjudicacao()
    assert decisoes, "data/auditoria/adjudicacao.json ausente"
    antes = {c["id"]: c for c in audit.gabarito_antes_da_adjudicacao(casos, decisoes)}
    assert antes["N36"]["observacional"] is True and antes["N36"]["categorias"] == ["S"]
    assert antes["N33"]["esperado"]["project"] == "Mapeamento Sistemático"
    # casos sem decisão ficam como estão
    assert antes["P01"] == next(c for c in casos if c["id"] == "P01")


def test_toda_divergencia_tem_decisao(casos):
    caminho = audit.DIR_AUDITORIA / "anotacao_independente.json"
    anot = json.loads(caminho.read_text(encoding="utf-8"))
    decididos = {d["id"] for d in audit.carregar_adjudicacao()}
    divergentes = set(audit.concordancia(casos, anot)["ids_divergentes"])
    assert divergentes - decididos == set()


def test_anotador_por_regras_sem_apontamentos(casos):
    for c in casos:
        assert audit.comparar(c, audit.extrair(c["consulta"])) == [], c["id"]


def test_amostra_revisao_humana_estratificada(casos):
    amostra = audit.amostra_revisao_humana(casos)
    assert len(amostra) == sum(audit.TAMANHO_AMOSTRA.values())
    assert len({c["id"] for c in amostra}) == len(amostra)
    for origem, k in audit.TAMANHO_AMOSTRA.items():
        assert sum(c["origem"] == origem for c in amostra) == k
    assert [c["id"] for c in amostra] == [c["id"] for c in audit.amostra_revisao_humana(casos)]
