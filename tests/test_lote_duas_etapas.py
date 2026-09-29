"""Configurações derivadas do lote: arquitetura em duas etapas simulada e regra do objeto vazio."""

from pfc_busca.evaluation import lote


def _linha(i: str, predito, esperado: dict, espera: bool = True, lat: float = 100.0) -> dict:
    return {"id": i, "origem": "G", "familia": "VS", "categorias": ["S"] if espera else ["F"], "consulta": "x",
            "observacional": False, "espera_tool_call": espera, "aceita_nao_chamar": False, "repeticao": 1,
            "hoje": "2026-09-24", "esperado": esperado, "esperado_resolvido": esperado,
            "alternativas_resolvidas": [], "predito": predito, "texto_resposta": None,
            "latencia_llm_ms": lat, "erro": None, "classe_erro": None}


def test_duas_etapas_decide_pela_primeira_e_extrai_pela_segunda():
    decisao = [_linha("A", {"state": "SP"}, {"state": "São Paulo"}, lat=100),   # busca, com a forma errada
               _linha("B", None, {}, espera=False, lat=50),                       # recusa correta (F)
               _linha("C", None, {"state": "Acre"}, lat=70)]                      # falsa recusa
    extracao = [_linha("A", {"state": "São Paulo"}, {"state": "São Paulo"}, lat=200),
                _linha("B", {}, {}, espera=False, lat=30),                        # a SE v1 buscaria em F
                _linha("C", {"state": "Acre"}, {"state": "Acre"}, lat=40)]
    hib = {x["id"]: x for x in lote.duas_etapas(decisao, extracao)}
    assert hib["A"]["predito"] == {"state": "São Paulo"} and hib["A"]["latencia_llm_ms"] == 300
    assert hib["B"]["predito"] is None and hib["B"]["latencia_llm_ms"] == 50
    assert hib["C"]["predito"] is None and hib["C"]["latencia_llm_ms"] == 70
    m = lote.medidas(list(hib.values()), {})
    assert m["acuracia"] == 2 / 3                       # A (parâmetros da extração) e B (recusa da decisão)
    assert (m["recusa"]["tp"], m["recusa"]["fp"], m["recusa"]["fn"]) == (1, 1, 0)
    # as entradas não são alteradas
    assert decisao[0]["predito"] == {"state": "SP"} and extracao[1]["predito"] == {}


def test_regra_do_objeto_vazio_e_ilike_das_siglas():
    linhas = [_linha("A", {}, {}), _linha("B", {"error": "x"}, {}), _linha("C", {"keyword": "a"}, {}),
              _linha("D", None, {})]
    assert [x["predito"] for x in lote.regra_objeto_vazio(linhas)] == [None, None, {"keyword": "a"}, None]
    assert lote._ufs_ilike("SP") == {"Espírito Santo"}          # 'SP' casa só a UF errada
    assert lote._ufs_ilike("PR") == frozenset()                  # 'PR' não casa nenhuma UF
    assert lote._ufs_ilike("Pará") == {"Pará", "Paraíba", "Paraná"}
