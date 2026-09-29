"""Análise do lote 2: classificação do retorno, primeira decisão e decomposição do acerto (linhas sintéticas)."""

from datetime import date

from pfc_busca import ferramentas as F
from pfc_busca import v3
from pfc_busca.evaluation import lote2

HOJE = date(2026, 9, 24)


def _item(params: dict, consulta: str, trecho: str) -> str:
    erros, avisos = F.validar_parametros(params, consulta, HOJE)
    return next(i for i in erros + avisos if trecho in i)


def _linha(i: str, predito, esperado: dict, extras=None, espera: bool = True, consulta: str = "cartas de Goiás") -> dict:
    lin = {"id": i, "origem": "G", "familia": "VS", "categorias": ["S"] if espera else ["F"], "consulta": consulta,
           "observacional": False, "espera_tool_call": espera, "aceita_nao_chamar": False, "repeticao": 1,
           "hoje": HOJE.isoformat(), "esperado": esperado, "esperado_resolvido": esperado,
           "alternativas_resolvidas": [], "predito": predito, "texto_resposta": None,
           "latencia_llm_ms": 100.0, "erro": None, "classe_erro": None}
    if extras is not None:
        lin["extras"] = extras
    return lin


def _busca(args, resultado: str = "Busca executada.") -> dict:
    return {"ferramenta": "buscar_catalogo", "args": args, "resultado": resultado[:300]}


def test_classificacao_das_mensagens_do_validador():
    c = lote2.classificar_mensagem
    # dá o valor
    assert c(_item({"state": "AM"}, "cartas do AM", "é sigla")) == "valor"
    assert c(_item({"keyword": "MI-2965-2-NE"}, "folha MI-2965-2-NE", "forma canônica")) == "valor"
    assert c(_item({"scale": "1:50000"}, "cartas 1:50000", "não é um valor válido")) == "valor"
    assert c(_item({}, "cartas de Tesouro (MT)", "preencha city=")) == "valor"
    assert c(_item({}, "cartas de Tesouro (MT)", "preencha state=")) == "valor"
    assert c(_item({"publicationPeriod": {"start": "2025-02-01", "end": "2025-12-31"}},
                   "cartas publicadas no ano passado", "corresponde a")) == "valor"
    assert c(_item({"city": "Campinass"}, "cartas de Campinass", "o mais próximo")) == "valor"
    assert c(_item({"keyword": "Goiás"}, "cartas de Goiás", "é uma UF")) == "valor"   # "use state='Goiás' e remova"
    # manda remover
    assert c(_item({"limit": 5}, "cartas de Goiás", "limit=")) == "remover"
    assert c(_item({"keyword": "carta"}, "carta de Goiás", "palavra genérica")) == "remover"
    assert c(_item({"productType": "SCN Carta Topográfica Matricial"}, "cartas de Goiás", "productType=")) == "remover"
    # erros de forma sem valor
    assert c(_item({"productType": "Mapa bonito"}, "cartas de Goiás", "não é um valor válido")) == "forma"
    assert c(_item({"state": "Nordeste"}, "cartas do Nordeste", "não é o nome")) == "forma"
    assert c(_item({"creationPeriod": {"start": "2020-13-01"}}, "cartas criadas em 2020", "ISO")) == "forma"
    assert c("BUSCA NÃO EXECUTADA: chamada malformada. Chame buscar_catalogo de novo.") == "forma"
    assert c("a resposta não é um objeto JSON válido no schema") == "forma"
    # aponta o campo sem o valor
    assert c(_item({}, "cartas 1:50.000 de Goiás", "preencha scale")) == "aponta"
    assert c(_item({"keyword": "Goiânia"}, "cartas de Goiânia", "use city")) == "aponta"
    # recusa contestada
    assert c(F.mensagem_recusa(["a UF Goiás"], v3.CONFIRMAR_RECUSA_TC)) == "contestada"
    assert c("fora_do_escopo contestado") == "contestada"
    assert lote2.categoria_principal({"aponta", "remover", "valor"}) == "valor"
    assert lote2.categoria_principal(set()) == lote2.SEM_MENSAGEM


def test_itens_da_mensagem_e_extras_repr():
    msg = F.mensagem_validacao(["x: parâmetro inexistente; os válidos são a, b."], ["limit=5: ...; remova limit."])
    assert lote2.itens_da_mensagem(msg) == ["x: parâmetro inexistente; os válidos são a, b.", "limit=5: ...; remova limit."]
    assert lote2.itens_da_mensagem("BUSCA NÃO EXECUTADA: chamada malformada.") == ["BUSCA NÃO EXECUTADA: chamada malformada."]
    lin = _linha("A", {}, {}, extras={"traco": repr([_busca({"state": "Goiás"})]), "recusa_contestada": "True",
                                      "chamadas_modelo": "3"})
    assert lote2.extra(lin, "traco")[0]["args"] == {"state": "Goiás"}
    assert lote2.extra(lin, "recusa_contestada") is True and lote2.extra(lin, "chamadas_modelo") == 3
    assert lote2.extra(_linha("B", {}, {}, extras=repr({"perguntas": 2})), "perguntas") == 2   # extras inteiro em repr


def test_primeira_decisao():
    se_recusa = _linha("A", {"state": "Goiás"}, {"state": "Goiás"},
                       extras={"historico": ["fora_do_escopo contestado", {"params": {"state": "Goiás"}}]})
    assert lote2.primeira_decisao(se_recusa) is None
    se_busca = _linha("B", {}, {}, extras={"historico": [{"params": {"limit": 3}}, {"params": {}}]})
    assert lote2.primeira_decisao(se_busca) == {"limit": 3}
    tc_recusa = _linha("C", {}, {}, extras={"traco": [{"ferramenta": "recusar_consulta", "resultado": "RECUSA ..."},
                                                      _busca({})]})
    assert lote2.primeira_decisao(tc_recusa) is None
    tc_malformada = _linha("D", {}, {}, extras={"traco": [_busca("{'state': 1", "BUSCA NÃO EXECUTADA: chamada malformada.")]})
    assert lote2.primeira_decisao(tc_malformada) == {}
    so_auxiliares = _linha("E", {"city": "Goiânia"}, {}, extras={"traco": [{"ferramenta": "identificar_nome"}]})
    assert lote2.primeira_decisao(so_auxiliares) == {"city": "Goiânia"}
    assert lote2.primeira_decisao(_linha("F", {}, {})) is lote2.SEM_TRACO


def test_decomposicao_primeira_decisao_final_e_tipo_de_retorno():
    goias = {"state": "Goiás"}
    aviso = F.mensagem_validacao(*F.validar_parametros({}, "cartas de Goiás", HOJE))
    # mensagem longa (> 300 caracteres): o traço guarda o começo; o item com o valor fica no fim e é refeito
    longo = {"limit": 5, "productType": "SCN Carta Topográfica Matricial", "sortField": "publicationDate",
             "sortDirection": "DESC"}
    msg_longa = F.mensagem_validacao(*F.validar_parametros(longo, "cartas de Goiás", HOJE))
    assert len(msg_longa) > 300 and "preencha state=" not in msg_longa[:300]
    recusa = F.mensagem_recusa(["a UF Goiás"], v3.CONFIRMAR_RECUSA_TC)
    linhas = [
        # A: TC, primeira busca sem o estado; o aviso dá o valor -> consertada (valor)
        _linha("A", goias, goias, {"traco": [_busca({}, aviso), _busca(goias)], "avisos_recebidos": 1}),
        # B: TC, recusa contestada e depois a busca certa -> consertada (contestada)
        _linha("B", goias, goias, {"traco": [{"ferramenta": "recusar_consulta", "args": "x", "resultado": recusa[:300]},
                                             _busca(goias)], "recusa_contestada": True}),
        # C: SE, primeira tentativa com limit, o retorno manda remover -> consertada (remover); extras em repr
        _linha("C", goias, goias, {"historico": repr([
            {"params": {**goias, "limit": 5}, "erros": [], "avisos": [_item({**goias, "limit": 5}, "cartas de Goiás", "limit=")]},
            {"params": goias, "erros": [], "avisos": []}])}),
        # D: TC, primeira certa, o retorno (trecho gravado; os argumentos não o reproduzem) estraga
        _linha("D", {**goias, "limit": 1}, goias, {"traco": [
            _busca(goias, F.mensagem_validacao([], ["sortField/sortDirection: ...; remova a ordenação."])),
            _busca({**goias, "limit": 1})]}),
        # E: sem traço
        _linha("E", goias, goias),
        # F: TC, certa de primeira, sem retorno
        _linha("F", goias, goias, {"traco": [_busca(goias)]}),
        # G: TC, mensagem truncada no traço; refeita pelo validador, traz o valor no fim -> consertada (valor)
        _linha("G", goias, goias, {"traco": [_busca(longo, msg_longa), _busca(goias)], "avisos_recebidos": 1}),
    ]
    d = lote2.decompor(linhas)
    assert (d["n"], d["sem_traco"], d["primeira"], d["final"]) == (6, 1, 2, 5)
    assert (d["consertou"], d["estragou"]) == (4, 1)
    assert d["consertou_valor"] == 2 and d["consertou_contestada"] == 1 and d["consertou_remover"] == 1
    assert d["estragou_remover"] == 1 and "consertou_forma" not in d
    assert d["recebeu_remover"] == 2 and d["recebeu_valor"] == 2   # G recebeu os dois; C só remover
    assert d["contestadas"] == 1 and d["contestada_dominio_certa"] == 1 and d["com_aviso"] == 2
    assert d["refeitas"] == 1 and d["com_retorno"] == 5


def test_medidas_v3_pares_e_melhor_isolada():
    goias = {"state": "Goiás"}
    tc3 = [_linha("A", goias, goias, {"chamadas_modelo": 3, "perguntas": 1, "perguntas_em_texto": 1,
                                      "chamadas_em_texto": 0, "traco": [_busca(goias)]}),
           _linha("B", None, {}, {"chamadas_modelo": "1", "recusa_contestada": "True", "traco": []}, espera=False),
           _linha("C", {}, goias, {"chamadas_modelo": 2, "chamadas_em_texto": 2, "traco": [_busca({})]})]
    se3 = [_linha(i, goias, goias, {"tentativas": 2, "historico": [{"params": goias, "erros": [], "avisos": []}]})
           for i in ("B", "C", "D")]
    m = lote2.medidas_v3("tc3", tc3)
    assert (m["com_pergunta"], m["com_pergunta_em_texto"], m["com_chamada_em_texto"], m["contestadas"]) == (1, 1, 1, 1)
    assert m["contestadas_detalhe"] == {"F_certa": 1}
    assert lote2.chamadas_por_consulta("tc3", tc3) == 2.0 and lote2.chamadas_por_consulta("se3", se3) == 2.0
    assert lote2.chamadas_por_consulta("tc2", se3) == 1.0
    assert lote2.melhor_isolada({"tc1": {"acuracia": 0.5, "f1": 0.9}, "se2": {"acuracia": 0.6, "f1": 0.1},
                                 "tc3": {"acuracia": 0.9, "f1": 0.9}}) == "se2"
    assert lote2.melhor_isolada({"tc2": {"acuracia": 0.6, "f1": 0.8}, "se1": {"acuracia": 0.6, "f1": 0.9}}) == "se1"
    dados = {k: {"linhas": v, "casos": {}, "pasta": k, "descartadas": 0, "n_conjunto": 4, "cobertura": len(v) / 4}
             for k, v in (("tc3", tc3), ("se3", se3))}
    avisos: list[str] = []
    r = lote2.analisar(dados, lote2.GRUPOS_PARES, lote2.DECOMPOSTAS, avisos)
    assert list(r["pares"]) == ["tc3se3", "tc3se3primeira"] and r["pares"]["tc3se3"]["n"] == 2  # só B e C
    assert r["pares"]["tc3se3primeira"]["grupo"] == "exploratorio"
    assert r["melhor_isolada"] is None and any("hib" in a for a in avisos)
    res = {"dir": "results/lote2", "dataset": "data/lote_validacao_2.json", "n_conjunto": 4,
           "presentes": list(dados), "ausentes": [k for k in lote2.CONFIGS if k not in dados], **r, "avisos": avisos}
    tex = lote2.macros(res)
    for chave in ("res@lote2@tc3se3@diff1", "res@lote2@tc3se3@icdiff1", "res@lote2@tc3se3@n",
                  "res@lote2@tc3@chamadas", "res@lote2@se3@consertou", "res@lote2@conjunto@n"):
        assert chave in tex
    assert "SIMULAÇÃO" not in lote2.tabela_degraus(res) and "Sem rodada: Tool Calling v1" in lote2.tabela_degraus(res)
    assert r"TC v3 $\times$ SE v3 & 2 &" in lote2.tabela_pares(res)
    assert "Consertadas pelo retorno" in lote2.tabela_decomposicao(res)
    assert "SIMULAÇÃO" in lote2.relatorio_md({**res, "dataset": "data/lote_validacao.json"})


def test_extras_json_se_fora_do_schema_contestada_em_E_e_erro_de_infra():
    import json

    goias = {"state": "Goiás"}
    # extras gravados como JSON (true/false/null), inteiros ou campo a campo
    lin = _linha("A", goias, goias, extras=json.dumps({"traco": [_busca(goias)], "chamadas_modelo": 2,
                                                       "recusa_contestada": True, "sem_final": False}))
    assert lote2.extra(lin, "chamadas_modelo") == 2 and lote2.extra(lin, "traco")[0]["args"] == goias
    lin2 = _linha("B", goias, goias, extras={"traco": json.dumps([_busca(goias)]), "recusa_contestada": "true"})
    assert lote2.extra(lin2, "traco")[0]["args"] == goias
    assert lote2.medidas_v3("tc3", [lin, lin2])["contestadas"] == 2
    # SE v3: o primeiro objeto fora do schema é uma busca malformada ({}), não uma recusa
    se_f = _linha("C", None, {}, espera=False, extras={"historico": [
        {"params": None, "erros": ["a resposta não é um objeto JSON válido no schema"], "avisos": []},
        "fora_do_escopo"]})
    assert lote2.primeira_decisao(se_f) == {}
    # recusa contestada numa subespecificada (E) não conta como domínio; estragada por erro de infraestrutura
    e = dict(_linha("D", {}, {}, extras={"traco": [{"ferramenta": "recusar_consulta", "resultado": "RECUSA AINDA "
                                                    "NÃO REGISTRADA. ..."}, _busca({})], "recusa_contestada": True}),
             aceita_nao_chamar=True)
    infra = dict(_linha("E", None, goias, extras={"traco": [_busca(goias)], "chamadas_modelo": 1}),
                 erro="tempo esgotado", classe_erro="timeout")
    d = lote2.decompor([se_f, e, infra])
    assert d["contestada_E_certa"] == 1 and "contestada_dominio_certa" not in d
    assert d["consertou"] == 1 and d["consertou_forma"] == 1 == d["consertou_remover_forma"]   # C: {} errada em F
    assert (d["estragou"], d["estragou_erro_infra"], d["erro_infra"]) == (1, 1, 1)
