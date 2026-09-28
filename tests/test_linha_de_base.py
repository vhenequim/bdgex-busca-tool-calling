"""Linhas de base com Saída Estruturada (agent_estruturado) e comparação de abordagens."""

from datetime import date

from pfc_busca import agent_estruturado as ae
from pfc_busca import schema
from pfc_busca.evaluation import metrics
from pfc_busca.evaluation.run_evaluation import hash_prompt, slug
from pfc_busca.prototipo_termos import COMMON_TERMS


def test_dicionario_do_prototipo_tem_159_entradas():
    assert len(COMMON_TERMS) == 159
    assert COMMON_TERMS["1cgeo"] == "1° Centro de Geoinformação"


def test_preprocessamento_substitui_termos_como_o_prototipo():
    assert ae.preprocessar_consulta("mdt do para em 25k") == "MDT - RAM do para em 1:25.000"
    assert ae.preprocessar_consulta("cartas do 1 cgeo") == "cartas do 1° Centro de Geoinformação"
    # texto sem termo do dicionário fica como está
    assert ae.preprocessar_consulta("cartas de Marte") == "cartas de Marte"


def test_validacao_zod_aceita_enumerados_do_prototipo_e_rejeita_os_demais():
    ok, erros = ae.validar_zod({"reasoning": "x", "productType": "MDT - RAM", "limit": 5})
    assert not erros and ok == {"productType": "MDT - RAM", "limit": 5}
    _, erros = ae.validar_zod({"reasoning": "x", "productType": "MDT — RAM"})
    assert erros and "productType" in erros[0]
    _, erros = ae.validar_zod({"keyword": "2901"})
    assert erros == ["reasoning: Required"]
    _, erros = ae.validar_zod({"reasoning": "x", "publicationPeriod": {"start": "2020-01-01"}})
    assert erros   # o DateRange do protótipo exige start e end


def test_validacao_pos_extracao_e_vocabulario_do_pfc():
    validados = ae.validar_extraidos({"keyword": "sf-22-y-d", "productType": "SCN Carta Topografica Matricial",
                                      "publicationPeriod": {"start": "2021-01-01", "end": "2020-01-01"},
                                      "limit": 500})
    assert validados == {"keyword": "SF-22-Y-D", "productType": "SCN Carta Topografica Matricial"}
    assert ae.para_vocabulario_pfc(validados)["productType"] == "SCN Carta Topográfica Matricial"
    # INOM incompleto (com cara de INOM, mas inválido) é descartado pelo validador do protótipo
    assert "keyword" not in ae.validar_extraidos({"keyword": "SF-22"})
    assert ae.validar_extraidos({"keyword": "Passo da Seringueira"}) == {"keyword": "Passo da Seringueira"}
    # todo valor do vocabulário do protótipo mapeado é um enumerado do PFC
    for valor in ae.VOCABULARIO_PROTOTIPO["productType"].values():
        assert valor in schema.TIPOS_PRODUTO


def test_fallback_por_regex():
    r = ae.extracao_fallback("5 cartas mais antigas em 25k do 3 cgeo publicadas em 2021", date(2026, 9, 14))
    assert r["scale"] == "1:25.000"
    assert r["supplyArea"] == "3° Centro de Geoinformação"
    assert (r["sortField"], r["sortDirection"], r["limit"]) == ("publicationDate", "ASC", 5)
    assert r["publicationPeriod"] == {"start": "2021-01-01", "end": "2021-12-31"}


def test_saida_estruturada_nao_pode_recusar():
    # a linha de base sempre busca: objeto vazio conta como chamada, e a categoria F erra
    aval = metrics.avaliar_caso({}, {}, espera_tool_call=False)
    assert not aval.correto


def test_prompts_e_diretorios_das_linhas_de_base():
    assert "buscar_catalogo" not in ae.montar_prompt_se(date(2026, 9, 14))
    assert '"keyword"' in ae.montar_prompt_se(date(2026, 9, 14))
    assert "2026-09-14" in ae.montar_prompt_prototipo(date(2026, 9, 14))
    assert len({hash_prompt(), hash_prompt("saida_estruturada"), hash_prompt("prototipo")}) == 3
    assert slug("qwen3:4b", "ollama", "saida_estruturada") == "se-qwen3-4b"
    assert slug("phi4:14b", "ollama", "prototipo") == "prototipo-phi4-14b"
    assert slug("qwen3:4b") == "qwen3-4b"
    assert ae.rotulo_modelo("phi4:14b", "prototipo") == "phi4:14b [prototipo]"


def test_valores_vazios_da_saida_estruturada_contam_como_ausentes():
    assert ae.limpar_vazios({"keyword": "", "state": "Roraima", "limit": 0,
                             "publicationPeriod": {"start": "2025-01-01", "end": ""}, "scale": None}) == {
        "state": "Roraima", "publicationPeriod": {"start": "2025-01-01"}}
