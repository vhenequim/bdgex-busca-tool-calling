"""Invariantes do dataset construído — falham se alguém mexer no gerador sem querer."""

from collections import Counter
from datetime import date

import pytest

from pfc_busca import schema
from pfc_busca.evaluation import dataset_builder as db_
from pfc_busca.evaluation.relative_time import resolver_gabarito


@pytest.fixture(scope="module")
def casos():
    casos, _, _ = db_.construir()
    return casos


def test_total_e_composicao(casos):
    assert len(casos) == 310
    assert Counter(c["origem"] for c in casos) == {"P": 22, "N": 40, "G": 248}
    familias = Counter(c["familia"] for c in casos)
    assert familias == {"P": 22, "N": 40, "GS": 61, "GC": 55, "GM": 28, "GT": 41,
                        "GO": 19, "GA": 24, "GP": 13, "GF": 7}


def test_sem_problemas_de_validacao(casos):
    assert db_.validar(casos) == []


def test_observacionais_sao_os_esperados(casos):
    obs = sorted(c["id"] for c in casos if c["observacional"])
    assert obs == ["GF001", "GF002", "GF003", "GF004", "GF005", "GF006", "GF007",
                   "N34", "N36", "N37", "N38", "N39", "N40"]


def test_todo_gabarito_resolve_em_qualquer_data(casos):
    for hoje in (date(2026, 9, 14), date(2026, 1, 1), date(2028, 2, 29)):
        for c in casos:
            r = resolver_gabarito(c["esperado"], hoje)
            for campo in schema.CAMPOS_PERIODO:
                if campo in r:
                    assert set(r[campo]) <= {"start", "end"} and r[campo], (c["id"], r[campo])


def test_amostras_do_apendice(casos):
    por_id = {c["id"]: c for c in casos}
    assert por_id["GS001"]["consulta"] == "cartas de AC" and por_id["GS001"]["esperado"] == {"state": "Acre"}
    assert por_id["GC001"]["esperado"] == {"state": "Rio Grande do Norte", "scale": "1:25.000"}
    assert por_id["GT001"]["esperado"] == {"publicationPeriod": {"rel": "ano_corrente"}}
    assert por_id["P05"]["esperado"]["publicationPeriod"] == {"rel": "ano_corrente"}
    assert por_id["N36"]["espera_tool_call"] is False


def test_gabaritos_corrigidos_na_camada_g(casos):
    """Goiânia/Belém eram anotados como estado no gerador original; 'depois de 2022' segue P21."""
    por_consulta = {c["consulta"]: c for c in casos if c["familia"] == "GA"}
    assert por_consulta["cartas de Goiania"]["esperado"] == {"city": "Goiânia"}
    assert por_consulta["cartas de Belem"]["esperado"] == {"city": "Belém"}
    depois = [c for c in casos if "depois de 2022" in c["consulta"]]
    assert depois and all(
        c["esperado"]["publicationPeriod"] == {"rel": "desde_2022"} for c in depois)
