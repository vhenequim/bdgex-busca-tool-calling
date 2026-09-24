from datetime import date

import pytest

from pfc_busca.evaluation import relative_time as rt

HOJE = date(2026, 9, 14)  # segunda-feira


@pytest.mark.parametrize("regra, leituras", [
    ("ano_corrente", [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]),
    ("ano_anterior", [{"start": "2025-01-01", "end": "2025-12-31"}]),
    ("dois_anos_atras", [{"start": "2024-01-01", "end": "2024-12-31"}, {"start": "2024-09-14", "end": "2026-09-14"}]),
    ("mes_anterior", [{"start": "2026-08-01", "end": "2026-08-31"}]),
    ("mes_corrente", [{"start": "2026-09-01", "end": "2026-09-14"}, {"start": "2026-09-01", "end": "2026-09-30"}]),
    ("semana_passada", [{"start": "2026-09-07", "end": "2026-09-13"}, {"start": "2026-09-07", "end": "2026-09-14"}]),
    ("semana_corrente", [{"start": "2026-09-14", "end": "2026-09-14"}, {"start": "2026-09-14", "end": "2026-09-20"}]),
    ("hoje", [{"start": "2026-09-14", "end": "2026-09-14"}]),
    ("ultimos_3_meses", [{"start": "2026-06-16", "end": "2026-09-14"}, {"start": "2026-06-14", "end": "2026-09-14"}]),
    ("ultimos_6_meses", [{"start": "2026-03-18", "end": "2026-09-14"}, {"start": "2026-03-14", "end": "2026-09-14"}]),
    ("ultimos_5_anos", [{"start": "2021-09-14", "end": "2026-09-14"}, {"start": "2021-01-01", "end": "2026-09-14"}]),
    ("desde_2020", [{"start": "2020-01-01", "end": "2026-09-14"}, {"start": "2020-01-01"}]),
    ("depois_de_2022", [{"start": "2022-01-01", "end": "2026-09-14"}, {"start": "2022-01-01"},
                        {"start": "2023-01-01", "end": "2026-09-14"}, {"start": "2023-01-01"}]),
    ("antes_de_2020", [{"end": "2019-12-31"}]),
    ("primeiro_trimestre_corrente", [{"start": "2026-01-01", "end": "2026-03-31"}]),
    ("segundo_semestre_anterior", [{"start": "2025-07-01", "end": "2025-12-31"}]),
    ("ultimo_trimestre_ano_anterior", [{"start": "2025-10-01", "end": "2025-12-31"}]),
    ("trimestre_anterior", [{"start": "2026-04-01", "end": "2026-06-30"}]),
])
def test_leituras_em_14_set_2026(regra, leituras):
    assert rt.leituras(regra, HOJE) == leituras
    assert rt.resolver(regra, HOJE) == leituras[0]


def test_semana_passada_numa_quarta_inclui_semana_calendario():
    quarta = date(2026, 9, 16)
    assert {"start": "2026-09-07", "end": "2026-09-13"} in rt.leituras("semana_passada", quarta)
    assert rt.leituras("semana_passada", quarta)[0] == {"start": "2026-09-09", "end": "2026-09-15"}


def test_mes_anterior_e_trimestre_em_janeiro_voltam_um_ano():
    assert rt.resolver("mes_anterior", date(2026, 1, 10)) == {"start": "2025-12-01", "end": "2025-12-31"}
    assert rt.resolver("trimestre_anterior", date(2026, 2, 3)) == {"start": "2025-10-01", "end": "2025-12-31"}


def test_datas_de_borda():
    assert rt.resolver("ultimos_5_anos", date(2028, 2, 29)) == {"start": "2023-02-28", "end": "2028-02-29"}
    assert rt.leituras("ultimos_3_meses", date(2026, 5, 31))[1] == {"start": "2026-02-28", "end": "2026-05-31"}


def test_toda_regra_tem_texto():
    assert set(rt.REGRAS) == set(rt.TEXTO_REGRA)


def test_regra_desconhecida_e_erro_claro():
    with pytest.raises(KeyError, match="desconhecida"):
        rt.resolver("semana_retrasada", HOJE)
