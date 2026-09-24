"""Invariantes do dataset construído — falham se alguém mexer no gerador ou no gabarito sem querer."""

from collections import Counter
from datetime import date

import pytest

from pfc_busca import schema
from pfc_busca.evaluation import dataset_builder as db_
from pfc_busca.evaluation import gabarito


@pytest.fixture(scope="module")
def casos():
    casos, _, _ = db_.construir()
    return casos


def test_total_e_composicao(casos):
    assert len(casos) == 310
    assert Counter(c["origem"] for c in casos) == {"P": 22, "N": 40, "G": 248}
    assert Counter(c["familia"] for c in casos) == {"P": 22, "N": 40, "GS": 61, "GC": 55, "GM": 28, "GT": 41,
                                                   "GO": 19, "GA": 24, "GP": 13, "GF": 7}


def test_validacao_sem_problemas(casos):
    assert db_.validar(casos) == []


def test_nenhuma_consulta_repetida(casos):
    textos = Counter(db_.normalizar_consulta(c["consulta"]) for c in casos)
    assert [t for t, n in textos.items() if n > 1] == []


def test_observacionais(casos):
    obs = sorted(c["id"] for c in casos if c["observacional"])
    assert obs == ["GF007", "N38", "N39", "N40"]


def test_fora_do_dominio_nas_metricas_principais(casos):
    """P4: fora do domínio tem gabarito determinado ('não chamar') e entra nas métricas (categoria F)."""
    fora = sorted(c["id"] for c in casos if "F" in c["categorias"])
    assert fora == ["GF001", "GF002", "GF003", "GF004", "GF005", "GF006", "N36", "N37"]
    for c in casos:
        if "F" in c["categorias"]:
            assert c["categorias"] == ["F"] and not c["espera_tool_call"] and not c["observacional"]
            assert c["esperado"] == {}


def test_rastreabilidade(casos):
    for c in casos:
        assert c["fonte"], c["id"]
    p01 = next(c for c in casos if c["id"] == "P01")
    assert p01["fonte"].endswith("test-cases.ts:6")


def test_convencoes_do_manual(casos):
    por_id = {c["id"]: c for c in casos}
    # estado x capital
    assert por_id["N01"]["alternativas"] == [{"city": "São Paulo"}]
    # região não vira estado
    assert por_id["N34"]["esperado"] == {"productType": "SCN Carta Ortoimagem"}
    # ordenação sem pista aceita as duas datas; singular deixa limit opcional
    assert gabarito.eh_um_de(por_id["N24"]["esperado"]["sortField"])
    assert gabarito.eh_opcional(por_id["P19"]["esperado"]["limit"])
    # verbo decide o período; sem verbo, as duas leituras
    assert por_id["P15"]["alternativas"] == []
    assert por_id["N18"]["alternativas"] == [{"state": "Roraima", "creationPeriod": {"rel": "ano_anterior"}}]


def test_todo_gabarito_resolve_em_datas_diversas(casos):
    for hoje in (date(2026, 9, 24), date(2026, 1, 1), date(2028, 2, 29)):
        for c in casos:
            for leitura in gabarito.resolver_leituras(c, hoje):
                for campo in schema.CAMPOS_PERIODO:
                    for p in gabarito.valores_aceitos(leitura.get(campo, {"start": "x"})):
                        assert set(p) <= {"start", "end"} and p, (c["id"], p)
