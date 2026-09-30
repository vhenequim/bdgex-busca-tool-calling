"""API (pfc_busca.api) e pipeline com tradutores falsos: nenhum teste chama o Ollama nem o banco."""

import logging
from datetime import date
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from pfc_busca import abordagens, agent, agent_estruturado, db, ferramentas, tools, v3
from pfc_busca.agent import Traducao
from pfc_busca.api import Configuracao, criar_app
from pfc_busca.pipeline import Pipeline

HOJE = date(2026, 9, 24)


class _LLMFalso:
    """Devolve as respostas programadas, em ordem, e guarda as mensagens recebidas."""

    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.vistas = []

    def invoke(self, mensagens):
        self.vistas.append(list(mensagens))
        resposta = self.respostas.pop(0)
        if isinstance(resposta, Exception):
            raise resposta
        return resposta


class TradutorFalso:
    """Só o contrato da pipeline: traduzir(consulta, hoje) -> Traducao."""

    def __init__(self, modelo, predito=None):
        self.modelo = modelo
        self.predito = {"state": "Amazonas"} if predito is None else predito
        self.consultas = []

    def traduzir(self, consulta, hoje):
        self.consultas.append(consulta)
        return Traducao(modelo=self.modelo, hoje=hoje.isoformat(), consulta=consulta, predito=self.predito,
                        chamou_ferramenta=True, latencia_llm_ms=12.0,
                        tool_calls=[{"name": "buscar_catalogo", "args": self.predito, "id": "c1"}])


def _chamada(nome, args, i="1"):
    return AIMessage(content="", tool_calls=[{"name": nome, "args": args, "id": i, "type": "tool_call"}])


def _tc_v1(respostas, resposta_final="Há cartas do Amazonas no acervo."):
    t = object.__new__(agent.Tradutor)
    t.modelo = "falso"
    t.llm_com_ferramenta = _LLMFalso(respostas)
    t.llm = _LLMFalso([AIMessage(content=resposta_final)])
    return t


def _tc_v3(respostas, abordagem="tool_calling_v3", resposta_final="Há cartas do Amazonas no acervo."):
    t = object.__new__(v3.TradutorV3)
    t.modelo, t.abordagem = "falso", abordagem
    t.auxiliares, t.retorno = v3.VARIANTES[abordagem]
    t.nomes_ferramentas = {f["function"]["name"] for f in v3.ferramentas_da(abordagem)}
    t.llm_com_ferramenta = _LLMFalso(respostas)
    t.llm = _LLMFalso([AIMessage(content=resposta_final)])
    return t


def _se_v3(respostas_json):
    t = object.__new__(v3.TradutorEstruturadoV3)
    t.modelo, t.tag, t.opcoes, t.keep_alive, t.thinking_desativado = "falso", "falso", {}, "1m", False
    respostas = iter(respostas_json)

    def chat(**_):
        return SimpleNamespace(message=SimpleNamespace(content=next(respostas)), prompt_eval_count=1, eval_count=1)

    t.cliente = SimpleNamespace(chat=chat)
    return t


def _cliente(abordagem=abordagens.RECOMENDADA, fabrica=None, modelo="modelo-falso", **config):
    fabricados = []

    def _fabrica(m):
        fabricados.append(m)
        return fabrica(m) if fabrica else TradutorFalso(m)

    config = {"executar_sql": False, "dsn": None, **config}
    app = criar_app(Configuracao(abordagem=abordagem, modelo=modelo, **config), fabrica=_fabrica,
                    versao_ollama=lambda: "0.34.0", banco_disponivel=lambda: False)
    return TestClient(app), fabricados


# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

def test_configuracao_do_ambiente():
    c = Configuracao.do_ambiente({})
    assert (c.abordagem, c.modelo, c.permitir_modelo) == ("tool_calling_v3", "gemma4:e4b-it-qat", False)
    c = Configuracao.do_ambiente({"PFC_ABORDAGEM": "tool_calling", "PFC_MODELO_PADRAO": "qwen3:4b-instruct-2507-q4_K_M",
                                  "PFC_PERMITIR_MODELO": "1", "OLLAMA_BASE_URL": "http://gpu:11434"})
    assert (c.abordagem, c.modelo, c.permitir_modelo, c.base_url) == (
        "tool_calling", "qwen3:4b-instruct-2507-q4_K_M", True, "http://gpu:11434")


def test_abordagem_desconhecida_impede_a_subida():
    with pytest.raises(abordagens.AbordagemDesconhecida, match="válidas"):
        criar_app(Configuracao(abordagem="tool_calling_v9"))


def test_health_informa_abordagem_modelo_e_hash():
    cliente, fabricados = _cliente(modelo=abordagens.MODELO_RECOMENDADO)
    h = cliente.get("/api/health").json()
    assert (h["abordagem"], h["familia"], h["versao"], h["recomendada"]) == ("tool_calling_v3", "TC", "v3", True)
    assert h["modelo"] == h["modelo_padrao"] == abordagens.MODELO_RECOMENDADO
    ident = abordagens.configuracao("tool_calling_v3", abordagens.MODELO_RECOMENDADO)
    assert h["configuracao"]["sha256"] == ident["sha256"]
    assert h["configuracao"]["prompt_sha256"] == abordagens.hash_prompt("tool_calling_v3")
    assert h["configuracao"]["ferramenta_sha256"] == abordagens.hash_ferramenta("tool_calling_v3")
    assert (h["ollama"], h["banco"]) == ("0.34.0", False)
    assert fabricados == []   # o tradutor só é criado na primeira busca
    if (ferramentas.DADOS / "indice_folhas.json").exists():
        assert h["status"] == "ok" and not h["degradada"] and h["avisos"] == []
        assert "results/lote2/tc3-gemma4-e4b-it-qat" in h["configuracao"]["rodadas_com_a_mesma_configuracao"]


# ---------------------------------------------------------------------------
# Busca
# ---------------------------------------------------------------------------

def test_busca_com_tradutor_falso():
    cliente, fabricados = _cliente()
    r = cliente.post("/api/search", json={"query": "cartas do Amazonas"})
    assert r.status_code == 200
    d = r.json()
    assert (d["abordagem"], d["modelo"], d["parametros"]) == ("tool_calling_v3", "modelo-falso", {"state": "Amazonas"})
    assert d["chamou_ferramenta"] and d["produtos"] is None and d["latencias_ms"]["llm_traducao"] == 12.0
    assert "state: Amazonas" in d["resposta"] and "não foi executada" in d["resposta"]   # sem modelo de chat
    cliente.post("/api/search", json={"query": "cartas do Pará"})
    assert fabricados == ["modelo-falso"]   # uma pipeline por modelo, reaproveitada


def test_selecao_de_modelo_por_requisicao():
    cliente, _ = _cliente()
    assert cliente.post("/api/search", json={"query": "cartas", "model": "outro"}).status_code == 403
    cliente, fabricados = _cliente(permitir_modelo=True)
    r = cliente.post("/api/search", json={"query": "cartas", "model": "outro"})
    assert r.status_code == 200 and r.json()["modelo"] == "outro" and fabricados == ["outro"]


def test_modelo_indisponivel_vira_503():
    def fabrica(_):
        raise agent.ModeloIndisponivel("o Ollama está aberto?")

    cliente, _ = _cliente(fabrica=fabrica)
    r = cliente.post("/api/search", json={"query": "cartas do Amazonas"})
    assert r.status_code == 503 and "Ollama" in r.json()["detail"]


def test_busca_com_tool_calling_v1():
    t = _tc_v1([_chamada("buscar_catalogo", {"state": "Amazonas", "scale": "1:25.000"})])
    cliente, _ = _cliente("tool_calling", fabrica=lambda _: t)
    d = cliente.post("/api/search", json={"query": "cartas do Amazonas em 25k"}).json()
    assert d["abordagem"] == "tool_calling" and d["parametros"] == {"state": "Amazonas", "scale": "1:25.000"}
    assert d["resposta"] == "Há cartas do Amazonas no acervo."
    chamada = t.llm.vistas[0][2].tool_calls[0]
    assert chamada["name"] == "buscar_catalogo" and chamada["id"] == "1"


def test_busca_com_tool_calling_v3_usa_os_parametros_aceitos():
    # a 1ª busca (sigla) é devolvida pelo validador; a resposta final vê só a busca aceita
    t = _tc_v3([_chamada("identificar_nome", {"nome": "AM"}), _chamada("buscar_catalogo", {"state": "AM"}, "2"),
                _chamada("buscar_catalogo", {"state": "Amazonas"}, "3")])
    cliente, _ = _cliente("tool_calling_v3", fabrica=lambda _: t)
    d = cliente.post("/api/search", json={"query": "cartas do AM"}).json()
    assert d["parametros"] == {"state": "Amazonas"} and d["resposta"] == "Há cartas do Amazonas no acervo."
    assert [c["name"] for c in d["tool_calls"]] == ["identificar_nome", "buscar_catalogo", "buscar_catalogo"]
    assert d["extras"]["tentativas_busca"] == 2 and d["extras"]["avisos_recebidos"] == 1
    assert t.llm.vistas[0][2].tool_calls[0]["args"] == {"state": "Amazonas"}


def test_busca_com_saida_estruturada_v3():
    t = _se_v3(['{"state": "AM"}', '{"state": "Amazonas"}'])
    cliente, _ = _cliente("saida_estruturada_v3", fabrica=lambda _: t)
    d = cliente.post("/api/search", json={"query": "cartas do AM", "resposta_final": False}).json()
    assert d["abordagem"] == "saida_estruturada_v3" and d["parametros"] == {"state": "Amazonas"}
    assert d["chamou_ferramenta"] and d["tool_calls"] == [] and d["extras"]["tentativas"] == 2


def test_recusa_nao_busca_nem_responde():
    t = _tc_v3([_chamada("recusar_consulta", {"motivo": "fora do domínio"})])
    cliente, _ = _cliente("tool_calling_v3", fabrica=lambda _: t)
    d = cliente.post("/api/search", json={"query": "quanto vale cada carta do baralho no truco?"}).json()
    assert d["parametros"] is None and not d["chamou_ferramenta"] and d["resposta"] == "fora do domínio"
    assert t.llm.vistas == []


def test_busca_sem_resultados_no_banco(monkeypatch):
    monkeypatch.setattr(db, "disponivel", lambda dsn=None: True)
    monkeypatch.setattr(tools, "buscar_catalogo", lambda params, dsn=None: tools.ResultadoBusca(
        executado=True, total=0, latencia_ms=3.0))
    cliente, _ = _cliente(executar_sql=True, dsn="postgresql://falso")
    d = cliente.post("/api/search", json={"query": "cartas do Amazonas"}).json()
    assert d["produtos"] == {"executado": True, "total": 0, "itens": [], "erro": None}
    assert d["resposta"].startswith("Nenhum produto do acervo") and d["latencias_ms"]["ferramenta_sql"] == 3.0


def test_v3_sem_indice_de_folhas_sobe_degradada(sem_indice, caplog):
    caplog.set_level(logging.INFO, logger="pfc_busca.api")
    t = _tc_v3([_chamada("normalizar_codigo", {"codigo": "MI 2965-2-NE"}),
                _chamada("buscar_catalogo", {"keyword": "2965-2-NE"}, "2")], resposta_final="Achei a folha.")
    cliente, _ = _cliente("tool_calling_v3", fabrica=lambda _: t, modelo=abordagens.MODELO_RECOMENDADO)
    avisos_no_log = [r.getMessage() for r in caplog.records if r.levelno == logging.WARNING]
    assert avisos_no_log and "modo degradado" in avisos_no_log[0] and "indice_folhas.json" in avisos_no_log[0]

    h = cliente.get("/api/health").json()
    assert h["status"] == "degradada" and h["degradada"] and "indice_folhas.json" in h["avisos"][0]
    assert h["dados_ferramentas"] == {"municipios_ibge.json": True, "indice_folhas.json": False}
    # o hash é outro (o arquivo entra nele): não corresponde a nenhuma rodada avaliada
    assert h["configuracao"]["rodadas_com_a_mesma_configuracao"] == []

    r = cliente.post("/api/search", json={"query": "carta MI 2965-2-NE"})
    assert r.status_code == 200
    d = r.json()
    assert d["parametros"] == {"keyword": "2965-2-NE"} and d["resposta"] == "Achei a folha."
    resultado_codigo = d["extras"]["traco"][0]["resultado"]
    assert "keyword='2965-2-NE'" in resultado_codigo and "acervo" not in resultado_codigo
    assert any("indice_folhas.json" in a for a in d["avisos"])


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def test_falha_na_resposta_final_vira_aviso():
    t = TradutorFalso("falso")
    t.llm = _LLMFalso([TimeoutError("demorou")])
    e = Pipeline(t, executar_sql=False).buscar("cartas do Amazonas", HOJE, resposta_final=True)
    assert e.traducao.predito == {"state": "Amazonas"} and e.resposta_final is None
    assert any("resposta final indisponível" in a and "tempo esgotado" in a for a in e.avisos)


def test_ferramenta_inexistente_na_v1_nao_derruba_a_resposta_final():
    # antes: StopIteration ao procurar buscar_catalogo entre as chamadas
    t = _tc_v1([_chamada("buscar_mapas", {"state": "Amazonas"})], resposta_final="Não entendi o pedido.")
    e = Pipeline(t, executar_sql=False).buscar("cartas do Amazonas", HOJE, resposta_final=True)
    assert e.traducao.classe_erro == "ferramenta_inexistente" and e.resposta_final == "Não entendi o pedido."


def test_saida_estruturada_do_ollama_responde_com_a_mesma_tag():
    t = object.__new__(agent_estruturado.TradutorEstruturado)
    t.modelo, t.tag, t.base_url = "gemma4:e4b-it-qat [saida-estruturada]", "gemma4:e4b-it-qat", "http://gpu:11434"
    t.keep_alive, t.thinking_desativado = "1m", True
    llm = Pipeline(t, executar_sql=False).modelo_de_resposta()
    assert (llm.model, llm.base_url, llm.reasoning) == ("gemma4:e4b-it-qat", "http://gpu:11434", False)
    assert Pipeline(TradutorFalso("x"), executar_sql=False).modelo_de_resposta() is None
