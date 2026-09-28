"""Lote de validação: especificação v2, categoria E, regras de tempo parametrizadas e filtros."""

import importlib.util
import json
from datetime import date
from pathlib import Path
from types import SimpleNamespace

from langchain_core.messages import AIMessage

from pfc_busca import schema, v2
from pfc_busca.evaluation import metrics, relative_time
from pfc_busca.evaluation.run_evaluation import hash_ferramenta, hash_prompt, slug

RAIZ = Path(__file__).resolve().parents[1]
HOJE = date(2026, 9, 24)


def _modulo(nome: str):
    spec = importlib.util.spec_from_file_location(nome, RAIZ / "scripts" / "lote_validacao" / f"{nome}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------- especificação v2

def test_v2_muda_so_as_descricoes_e_acrescenta_a_recusa():
    v1 = schema.FERRAMENTA_BUSCAR_CATALOGO["function"]["parameters"]["properties"]
    p2 = v2.PARAMETROS_V2["properties"]
    assert set(p2) == set(v1)
    for campo in v1:   # mesmos tipos e enumerados; só a descrição muda
        assert {k: x for k, x in p2[campo].items() if k != "description"} == \
               {k: x for k, x in v1[campo].items() if k != "description"}
    assert v2.FERRAMENTA_RECUSAR["function"]["name"] == v2.NOME_RECUSA
    assert v2.CAMPO_FORA_DO_ESCOPO in v2.PARAMETROS_SE_V2["properties"]
    # nenhum código de exemplo que o modelo possa copiar (o v1 tinha '2965-2-NE')
    assert "2965" not in json.dumps(v2.FERRAMENTA_BUSCAR_CATALOGO_V2, ensure_ascii=False)
    assert "Nunca peça esclarecimento" in v2.montar_prompt_tc_v2(HOJE)
    assert '{"fora_do_escopo": true}' in v2.montar_prompt_se_v2(HOJE)


def test_v2_identificada_no_manifesto():
    assert len({hash_prompt(), hash_prompt("tool_calling_v2"), hash_prompt("saida_estruturada_v2")}) == 3
    assert hash_ferramenta() != hash_ferramenta("tool_calling_v2") != hash_ferramenta("saida_estruturada_v2")
    assert slug("gemma4:e4b-it-qat", "ollama", "tool_calling_v2") == "tc2-gemma4-e4b-it-qat"
    assert slug("gemma4:e4b-it-qat", "ollama", "saida_estruturada_v2") == "se2-gemma4-e4b-it-qat"


def _tradutor_v2() -> v2.TradutorV2:
    t = object.__new__(v2.TradutorV2)
    t.modelo = "teste"
    return t


def _traducao():
    from pfc_busca.agent import Traducao
    return Traducao(modelo="teste", hoje=HOJE.isoformat(), consulta="x")


def test_tool_calling_v2_recusa_pela_ferramenta_conta_como_nao_buscar():
    r = _traducao()
    _tradutor_v2()._preencher(r, AIMessage(content="", tool_calls=[
        {"name": v2.NOME_RECUSA, "args": {"motivo": "fora do escopo"}, "id": "1"}]))
    assert r.predito is None and not r.chamou_ferramenta and r.classe_erro is None
    assert r.extras["recusou"] and r.texto_resposta == "fora do escopo"
    assert metrics.avaliar_caso({}, r.predito, espera_tool_call=False).correto


def test_tool_calling_v2_busca_prevalece_sobre_a_recusa():
    r = _traducao()
    _tradutor_v2()._preencher(r, AIMessage(content="", tool_calls=[
        {"name": schema.NOME_FERRAMENTA, "args": {"scale": "1:25.000"}, "id": "1"},
        {"name": v2.NOME_RECUSA, "args": {"motivo": "?"}, "id": "2"}]))
    assert r.predito == {"scale": "1:25.000"} and r.chamou_ferramenta
    assert r.extras.get("buscou_e_recusou") and r.classe_erro is None


def _se_v2(conteudo: str) -> v2.TradutorEstruturadoV2:
    t = object.__new__(v2.TradutorEstruturadoV2)
    t.modelo, t.tag, t.opcoes, t.keep_alive, t.thinking_desativado = "teste", "teste", {}, "1m", False
    resp = SimpleNamespace(message=SimpleNamespace(content=conteudo), prompt_eval_count=1, eval_count=1)
    t.cliente = SimpleNamespace(chat=lambda **_: resp)
    return t


def test_saida_estruturada_v2_recusa_pelo_campo_fora_do_escopo():
    r = _se_v2('{"fora_do_escopo": true}').traduzir("previsão do tempo", HOJE)
    assert r.predito is None and not r.chamou_ferramenta and r.extras["recusou"]
    r = _se_v2('{"fora_do_escopo": false, "scale": "1:25.000", "keyword": ""}').traduzir("cartas 25k", HOJE)
    assert r.predito == {"scale": "1:25.000"} and r.chamou_ferramenta and not r.extras["recusou"]


# ---------------------------------------------------------------------------- categoria E

def test_subespecificada_aceita_buscar_sem_filtros_ou_nao_buscar():
    assert metrics.avaliar_caso({}, None, True, aceita_nao_chamar=True).correto
    assert metrics.avaliar_caso({}, {}, True, aceita_nao_chamar=True).correto
    assert not metrics.avaliar_caso({}, {"state": "Bahia"}, True, aceita_nao_chamar=True).correto
    # sem a marca E, não buscar continua erro
    assert not metrics.avaliar_caso({"state": "Bahia"}, None, True).correto


# ---------------------------------------------------------------------------- tempo parametrizado

def test_regras_de_tempo_parametrizadas_seguem_a_tabela_do_manual():
    assert relative_time.leituras("ultimos_12_meses", HOJE) == [
        {"start": "2025-09-29", "end": "2026-09-24"}, {"start": "2025-09-24", "end": "2026-09-24"}]
    assert relative_time.leituras("ultimos_7_dias", HOJE) == [
        {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-18", "end": "2026-09-24"}]
    assert relative_time.leituras("desde_2015", HOJE) == [{"start": "2015-01-01", "end": "2026-09-24"},
                                                         {"start": "2015-01-01"}]
    assert relative_time.leituras("antes_de_2010", HOJE) == [{"end": "2009-12-31"}]
    # as regras nomeadas das 310 não mudam
    assert relative_time.leituras("ultimos_3_meses", HOJE) == relative_time.REGRAS["ultimos_3_meses"](HOJE)
    assert relative_time.texto_regra("ultimos_10_anos") == "últimos 10 anos"
    assert relative_time.existe("depois_de_1998") and not relative_time.existe("ultimos_x_meses")


# ---------------------------------------------------------------------------- filtros do lote

def test_checagens_automaticas_do_lote():
    m = _modulo("montar_lote")
    alvo = {"familia": "VC", "esperado": {"city": "Campinas", "scale": "1:25.000"},
            "superficies": [["Campinas"], ["25k"]], "verbo_periodo": None}
    assert m.checar(alvo, "cartas de campinas em 25k") == []
    assert any("falta" in x for x in m.checar(alvo, "cartas de Campinas na escala 1:25.000"))
    assert any("productType" in x for x in m.checar(alvo, "cartas topográficas de Campinas em 25k"))
    assert any("periodo" in x for x in m.checar(alvo, "cartas de Campinas em 25k de 2019"))
    assert any("sigla" in x for x in m.checar(alvo, "cartas de Campinas, SP, em 25k"))
    # "prefeitura" não é verbo de criação, "Porto" não é "orto", "sistemática" não é "temática"
    assert m.checar({**alvo, "esperado": {"city": "Porto Seguro"}, "superficies": [["Porto Seguro"]]},
                    "sou da prefeitura, preciso de mapas de Porto Seguro") == []
    periodo = {"familia": "VT", "esperado": {"publicationPeriod": {"rel": "ano_anterior"}},
               "superficies": [], "verbo_periodo": "criacao"}
    assert any("verbo" in x for x in m.checar(periodo, "cartas publicadas no ano passado"))
    assert m.checar(periodo, "cartas elaboradas no ano passado") == []


def test_gerador_de_alvos_e_deterministico_e_consistente():
    g = _modulo("gerar_alvos")
    if not (RAIZ / "data" / "lote_validacao" / "bdgex_csw").is_dir():
        return   # coleta bruta do BDGEx fora do repositório: teste só roda onde ela existe
    a1 = g.Gerador().gerar()
    a2 = g.Gerador().gerar()
    assert a1 == a2
    assert len(a1) == sum(g.CONTAGENS.values())
    for a in a1:
        if a["familia"] == "VF":
            assert not a["espera_tool_call"] and a["esperado"] == {} and a["categorias"] == ["F"]
        elif a["familia"] == "VE":
            assert a["aceita_nao_chamar"] and a["esperado"] == {}
        else:
            assert a["esperado"]
            # só período ou ordenação podem vir sem trecho literal exigido (a redação é livre)
            assert a["superficies"] or set(a["esperado"]) <= {"publicationPeriod", "creationPeriod", "sortField",
                                                               "sortDirection", "limit"}, a["id"]
        for campo, valor in a["esperado"].items():
            enum = schema.valores_validos(campo)
            if enum and isinstance(valor, str):
                assert valor in enum, (a["id"], campo, valor)
            if isinstance(valor, dict) and "rel" in valor:
                assert relative_time.existe(valor["rel"]), a["id"]
