from datetime import date

import pytest

from pfc_busca.evaluation import relative_time as rt

# segunda-feira, para as regras de semana serem inequívocas
HOJE = date(2026, 9, 14)


@pytest.mark.parametrize("regra, esperado", [
    ("ano_corrente", {"start": "2026-01-01", "end": "2026-12-31"}),
    ("ano_anterior", {"start": "2025-01-01", "end": "2025-12-31"}),
    ("dois_anos_atras", {"start": "2024-01-01", "end": "2024-12-31"}),
    ("mes_anterior", {"start": "2026-08-01", "end": "2026-08-31"}),
    ("mes_corrente", {"start": "2026-09-01", "end": "2026-09-14"}),
    ("semana_passada", {"start": "2026-09-07", "end": "2026-09-13"}),
    ("semana_corrente", {"start": "2026-09-14", "end": "2026-09-14"}),
    ("hoje", {"start": "2026-09-14", "end": "2026-09-14"}),
    ("ultimos_90_dias", {"start": "2026-06-16", "end": "2026-09-14"}),
    ("ultimos_180_dias", {"start": "2026-03-18", "end": "2026-09-14"}),
    ("ultimos_5_anos", {"start": "2021-09-14", "end": "2026-09-14"}),
    ("desde_2020", {"start": "2020-01-01", "end": "2026-09-14"}),
    ("desde_2022", {"start": "2022-01-01", "end": "2026-09-14"}),
    ("antes_de_2020", {"end": "2019-12-31"}),
    ("primeiro_trimestre_corrente", {"start": "2026-01-01", "end": "2026-03-31"}),
    ("segundo_semestre_anterior", {"start": "2025-07-01", "end": "2025-12-31"}),
    ("ultimo_trimestre_ano_anterior", {"start": "2025-10-01", "end": "2025-12-31"}),
    ("trimestre_anterior", {"start": "2026-04-01", "end": "2026-06-30"}),
])
def test_regras_em_14_set_2026(regra, esperado):
    assert rt.resolver(regra, HOJE) == esperado


def test_mes_anterior_em_janeiro_volta_um_ano():
    assert rt.resolver("mes_anterior", date(2026, 1, 10)) == {"start": "2025-12-01", "end": "2025-12-31"}


def test_trimestre_anterior_em_janeiro_volta_um_ano():
    assert rt.resolver("trimestre_anterior", date(2026, 2, 3)) == {"start": "2025-10-01", "end": "2025-12-31"}


def test_ultimos_5_anos_em_29_fev():
    assert rt.resolver("ultimos_5_anos", date(2028, 2, 29)) == {"start": "2023-02-28", "end": "2028-02-29"}


def test_toda_regra_do_apendice_existe():
    for descricao, regra in rt.DESCRICAO_PARA_REGRA.items():
        assert regra in rt.REGRAS, (descricao, regra)


def test_regra_de_descricao_tolera_espacos():
    assert rt.regra_de_descricao("  ano corrente   da execução, integral ") == "ano_corrente"
    assert rt.regra_de_descricao("coisa inexistente") is None


def test_resolver_gabarito_substitui_apenas_rel():
    esperado = {"state": "Pará", "publicationPeriod": {"rel": "ano_corrente"},
                "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}}
    assert rt.resolver_gabarito(esperado, HOJE) == {
        "state": "Pará",
        "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"},
        "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"},
    }


def test_regra_desconhecida_e_erro_claro():
    with pytest.raises(KeyError, match="desconhecida"):
        rt.resolver("semana_retrasada", HOJE)
