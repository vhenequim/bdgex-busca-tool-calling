import pytest

from pfc_busca.evaluation import report


def test_wilson_casos_de_borda():
    assert report.wilson(0, 0) == (0.0, 0.0)
    lo, hi = report.wilson(0, 10)
    assert lo == 0.0 and 0.25 < hi < 0.35          # 0/10 -> IC até ~0,28
    lo, hi = report.wilson(10, 10)
    assert 0.65 < lo < 0.75 and hi == 1.0


def test_wilson_valor_conhecido():
    # 80/100: Wilson 95% ≈ [0,711; 0,867]
    lo, hi = report.wilson(80, 100)
    assert lo == pytest.approx(0.7112, abs=1e-3)
    assert hi == pytest.approx(0.8666, abs=1e-3)


def test_mcnemar_exato():
    assert report.mcnemar_exato(0, 0) == 1.0
    assert report.mcnemar_exato(5, 5) == 1.0
    # 10 discordantes todos a favor de um lado: p = 2 * (1/2)^10 ≈ 0,00195
    assert report.mcnemar_exato(10, 0) == pytest.approx(2 / 1024)
    # 8 vs 2: p = 2 * P(X<=2 | n=10) = 2 * 56/1024
    assert report.mcnemar_exato(8, 2) == pytest.approx(2 * 56 / 1024)


def test_rotulo_conhecido_e_desconhecido():
    assert report.rotulo("qwen3:4b-instruct-2507-q4_K_M") == "Qwen 3 4B"
    assert report.rotulo("modelo-x:1b") == "modelo-x:1b"
