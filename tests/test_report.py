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


def test_relatorio_sem_pasta_de_resultados_avisa_em_vez_de_quebrar(tmp_path, capsys):
    assert report.carregar_modelos(tmp_path / "nao_existe", None) == {}
    assert report.main(["--resultados", str(tmp_path / "nao_existe")]) == 1
    assert "nenhum" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Exportação para o texto (--paper): só o que a execução gerou
# ---------------------------------------------------------------------------

def _rodada_sintetica(raiz, modelo, acerta=True):
    """Pasta de resultados mínima com as 22 consultas P: todas certas ou todas sem chamada."""
    import json
    from datetime import date

    from pfc_busca.evaluation import gabarito
    from pfc_busca.evaluation.dataset_builder import carregar_dataset
    from pfc_busca.evaluation.run_evaluation import slug

    pasta = raiz / slug(modelo, "ollama")
    pasta.mkdir(parents=True)
    hoje = date(2026, 9, 14)
    linhas = []
    for c in (c for c in carregar_dataset() if c["origem"] == "P"):
        leituras = gabarito.resolver_leituras(c, hoje)
        pred = {k: gabarito.valor_preferencial(v) for k, v in leituras[0].items()} if acerta else None
        linhas.append({"id": c["id"], "consulta": c["consulta"], "repeticao": 1, "hoje": hoje.isoformat(),
                       "modelo": modelo, "predito": pred, "chamou_ferramenta": pred is not None,
                       "latencia_llm_ms": 1000.0, "latencia_tool_ms": None, "latencia_total_ms": 1000.0,
                       "tokens_saida": 40, "erro": None, "classe_erro": None})
    (pasta / "execucoes.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in linhas) + "\n",
                                           encoding="utf-8")
    (pasta / "manifesto.json").write_text(json.dumps({"modelo": modelo, "provedor": "ollama", "hoje": "2026-09-14",
                                                      "software": {"ollama_servidor": "0.34.0"}}), encoding="utf-8")


def test_paper_recebe_so_os_arquivos_da_execucao(tmp_path):
    res, paper = tmp_path / "results", tmp_path / "paper"
    _rodada_sintetica(res, "qwen3:4b-instruct-2507-q4_K_M")
    _rodada_sintetica(res, "gemma4:e2b-it-qat", acerta=False)
    (res / "consolidado").mkdir()
    (res / "consolidado" / "tab_comparativo.tex").write_text("LIXO de outra execução", encoding="utf-8")
    assert report.main(["--resultados", str(res), "--sufixo", "_x", "--paper", str(paper)]) == 0
    nomes = {f.name for f in (paper / "tabelas").iterdir()}
    assert "tab_comparativo_x.tex" in nomes and "numeros_x.tex" in nomes
    assert "tab_comparativo.tex" not in nomes          # arquivo alheio não vaza para o texto
    macros = (paper / "tabelas" / "numeros_x.tex").read_text(encoding="utf-8")
    assert r"\csname res@x@qwen@acuracia\endcsname{100,0\%}" in macros
    assert r"\csname res@x@e2b@acuracia\endcsname{0,0\%}" in macros


def test_so_comparacao_nao_gera_tabelas_principais(tmp_path):
    a, b, paper = tmp_path / "a", tmp_path / "b", tmp_path / "paper"
    _rodada_sintetica(a, "qwen3:4b-instruct-2507-q4_K_M")
    _rodada_sintetica(b, "qwen3:4b-instruct-2507-q4_K_M", acerta=False)
    assert report.main(["--resultados", str(a), "--comparar-com", str(b), "--nome-comparacao", "teste",
                        "--so-comparacao", "--paper", str(paper)]) == 0
    assert sorted(f.name for f in (paper / "tabelas").iterdir()) == ["numeros_teste.tex", "tab_concordancia_teste.tex"]
    assert not (a / "consolidado" / "tab_comparativo.tex").exists()
    macros = (paper / "tabelas" / "numeros_teste.tex").read_text(encoding="utf-8")
    assert r"res@teste@qwen@identicas\endcsname{0}" in macros
