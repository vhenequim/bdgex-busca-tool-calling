"""v3: ferramentas auxiliares, validador, orientações e o laço de Tool Calling (com LLM simulado)."""

from datetime import date
from types import SimpleNamespace

from langchain_core.messages import AIMessage

from pfc_busca import ferramentas as F
from pfc_busca import orientacoes, v3
from pfc_busca.evaluation.run_evaluation import hash_prompt, slug

HOJE = date(2026, 9, 24)


def test_identificar_nome():
    assert "state='Amazonas'" in F.identificar_nome("AM")
    assert "city='Campinas' e state='São Paulo'" in F.identificar_nome("Campinas, SP")
    assert "city='Santa Rosa do Piauí'" in F.identificar_nome("santa rosa do piaui")   # nome inteiro, sem partir
    assert "região" in F.identificar_nome("Nordeste")
    assert "ambíguo" in F.identificar_nome("São Paulo")
    assert "Águas Belas" in F.identificar_nome("aguas belas")


def test_codigo_escala_periodo():
    assert F.forma_canonica_codigo("MI 0352-1") == ("0352-1", "MI")
    assert F.forma_canonica_codigo("MI-2392-3-SE") == ("2392-3-SE", "MI")
    assert F.forma_canonica_codigo("sf22yd") == ("SF-22-Y-D", "INOM")
    assert F.forma_canonica_codigo("inom sa21yaiv1") == ("SA-21-Y-A-IV-1", "INOM")
    assert F.forma_canonica_codigo("abc") == (None, None)
    assert F.forma_canonica_escala("1:25000")[0] == "1:25.000"
    assert F.forma_canonica_escala("cem mil")[0] == "1:100.000"
    assert F.forma_canonica_escala("1:10.000.000") == (None, [])
    assert F.forma_canonica_escala("grande escala")[1][0] == "1:25.000"
    assert F.regra_de_tempo("nos últimos dez anos") == ("ultimos_10_anos", None)
    assert F.regra_de_tempo("anteriores a 2011") == ("antes_de_2011", None)
    assert F.regra_de_tempo("entre 2012 e 2010") == (None, {"start": "2010-01-01", "end": "2012-12-31"})
    assert '"start": "2025-01-01", "end": "2025-12-31"' in F.resolver_periodo("no ano passado", HOJE)


def test_validador_erros_de_forma():
    erros, _ = F.validar_parametros({"state": "AM"}, "cartas AM", HOJE)
    assert any("Amazonas" in e for e in erros)
    erros, _ = F.validar_parametros({"keyword": "MI 0352-1"}, "a MI 0352-1", HOJE)
    assert any("0352-1" in e for e in erros)
    erros, _ = F.validar_parametros({"scale": "1:25000"}, "cartas 1:25000", HOJE)
    assert any("1:25.000" in e for e in erros)
    erros, _ = F.validar_parametros({"keyword": "carta"}, "carta", HOJE)
    assert erros


def test_validador_avisos_de_evidencia():
    _, avisos = F.validar_parametros({"productType": "SCN Carta Topográfica Matricial", "scale": "1:100.000"},
                                     "cartas 100k do 4o cgeo", HOJE)
    assert any("productType" in a for a in avisos) and any("supplyArea" in a for a in avisos)
    _, avisos = F.validar_parametros({"limit": 1, "sortField": "publicationDate", "sortDirection": "DESC"},
                                     "as cartas mais recentes da MI 0352-1", HOJE)
    assert any("limit=1" in a for a in avisos) and any("keyword" in a for a in avisos)
    _, avisos = F.validar_parametros({"city": "Santa Rosa", "state": "Piauí"}, "cartas de Santa Rosa do Piauí", HOJE)
    assert any("Santa Rosa do Piauí" in a for a in avisos)
    # consulta completa e correta: nenhum aviso
    assert F.validar_parametros({"city": "Campinas", "state": "São Paulo", "scale": "1:25.000"},
                                "cartas de Campinas, SP em 25k", HOJE) == ([], [])
    # ano dentro do nome de projeto não é período
    assert not any("tempo" in a for a in F.validar_parametros({"project": "Olimpíadas Rio 2016"},
                                                               "projeto rio 2016", HOJE)[1])


def test_orientacoes_so_do_tipo_certo(tmp_path):
    (tmp_path / "a.md").write_text("---\ntipo: orientacao-pfc\nnome: a\ntitulo: A\ngatilhos:\n  - 'cgeo'\n---\nregra A\n",
                                   encoding="utf-8")
    (tmp_path / "b.md").write_text("---\ntipo: outra-coisa\nnome: b\n---\nnão carregar\n", encoding="utf-8")
    (tmp_path / "c.md").write_text("---\ntipo: orientacao-pfc\nstatus: retirada\nnome: c\n---\nretirada\n",
                                   encoding="utf-8")
    carregadas = orientacoes.carregar(str(tmp_path))
    assert [o.nome for o in carregadas] == ["a"]
    assert carregadas[0].aplica("cartas do 3o cgeo") and not carregadas[0].aplica("cartas de Goiás")
    assert all(o.arquivo.endswith(".md") for o in orientacoes.carregar())
    assert len(orientacoes.assinatura()) == 64


def test_chamadas_em_texto():
    nomes = {"pedir_esclarecimento", "buscar_catalogo", "recusar_consulta"}
    assert v3.chamadas_em_texto('pedir_esclarecimento(pergunta="Qual estado?")', nomes) == [
        ("pedir_esclarecimento", {"pergunta": "Qual estado?"})]
    assert v3.chamadas_em_texto('{"name": "recusar_consulta", "arguments": {"motivo": "x"}}', nomes) == [
        ("recusar_consulta", {"motivo": "x"})]
    assert v3.chamadas_em_texto("não sei", nomes) == []


class _LLMFalso:
    """Devolve as respostas programadas, em ordem, e guarda as mensagens recebidas."""

    def __init__(self, respostas):
        self.respostas = list(respostas)
        self.vistas = []

    def invoke(self, mensagens):
        self.vistas.append(list(mensagens))
        return self.respostas.pop(0)


def _tradutor(respostas, abordagem="tool_calling_v3"):
    t = object.__new__(v3.TradutorV3)
    t.modelo, t.abordagem = "falso", abordagem
    t.com_ferramentas, t.modo_orientacoes = v3.VARIANTES[abordagem]
    t.nomes_ferramentas = {f["function"]["name"] for f in v3.ferramentas_da(abordagem)}
    t.llm_com_ferramenta = _LLMFalso(respostas)
    return t


def _chamada(nome, args, i="1"):
    return AIMessage(content="", tool_calls=[{"name": nome, "args": args, "id": i, "type": "tool_call"}])


def test_laco_corrige_apos_aviso_da_validacao():
    t = _tradutor([_chamada("buscar_catalogo", {"state": "AM"}),
                   _chamada("buscar_catalogo", {"state": "Amazonas"}, "2")])
    r = t.traduzir("cartas do AM", HOJE)
    assert r.predito == {"state": "Amazonas"} and r.chamou_ferramenta
    assert r.extras["tentativas_busca"] == 2 and r.extras["avisos_recebidos"] == 1


def test_laco_aceita_mesmos_parametros_depois_de_aviso():
    t = _tradutor([_chamada("buscar_catalogo", {"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial"}),
                   _chamada("buscar_catalogo", {"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial"},
                            "2")])
    r = t.traduzir("cartas 25k", HOJE)   # aviso de evidência: o modelo insiste, a busca é aceita
    assert r.predito == {"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial"}


def test_laco_ferramenta_auxiliar_pergunta_e_recusa():
    t = _tradutor([_chamada("identificar_nome", {"nome": "Campinas, SP"}),
                   _chamada("buscar_catalogo", {"city": "Campinas", "state": "São Paulo"}, "2")])
    r = t.traduzir("cartas de Campinas, SP", HOJE)
    assert r.predito == {"city": "Campinas", "state": "São Paulo"} and r.extras["ferramentas_usadas"]["identificar_nome"]
    t = _tradutor([_chamada("pedir_esclarecimento", {"pergunta": "Qual lugar?"}),
                   _chamada("buscar_catalogo", {}, "2")])
    r = t.traduzir("quero ver cartas", HOJE)
    assert r.predito == {} and r.extras["perguntas"] == 1
    t = _tradutor([AIMessage(content='recusar_consulta(motivo="fora do escopo")')])
    r = t.traduzir("previsão do tempo", HOJE)
    assert r.predito is None and r.extras["recusou"] and r.extras["chamadas_em_texto"] == 1


def test_se3_valida_e_pede_nova_tentativa():
    t = object.__new__(v3.TradutorEstruturadoV3)
    t.modelo, t.tag, t.opcoes, t.keep_alive, t.thinking_desativado = "falso", "falso", {}, "1m", False
    respostas = iter(['{"state": "AM"}', '{"state": "Amazonas"}'])

    def chat(**_):
        return SimpleNamespace(message=SimpleNamespace(content=next(respostas)), prompt_eval_count=1, eval_count=1)

    t.cliente = SimpleNamespace(chat=chat)
    r = t.traduzir("cartas do AM", HOJE)
    assert r.predito == {"state": "Amazonas"} and r.extras["tentativas"] == 2


def test_v3_no_manifesto():
    assert slug("gemma4:e4b-it-qat", "ollama", "tool_calling_v3") == "tc3-gemma4-e4b-it-qat"
    assert slug("gemma4:e4b-it-qat", "ollama", "saida_estruturada_v3") == "se3-gemma4-e4b-it-qat"
    assert len({hash_prompt(a) for a in v3.ABORDAGENS_V3}) == len(v3.ABORDAGENS_V3)
