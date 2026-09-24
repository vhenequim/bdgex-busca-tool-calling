"""Camadas P (protótipo, 22) e N (autores, 40) do dataset.

O gabarito segue `docs/manual_de_anotacao.md`. Onde a consulta admite mais de uma
leitura razoável, as leituras aceitas estão explícitas (princípio P3):

    um_de(a, b)          valor alternativo
    opcional(v)          campo que pode faltar
    trocas=[(a, b)]      leitura estrutural alternativa (campo a → campo b)

Camada P: a anotação original da equipe do 1º CGEO (`test-cases.ts`) é mantida
como leitura preferencial — o baseline não é reanotado —, e as leituras
alternativas acrescentadas estão justificadas em `notas`. A linha de cada consulta
no arquivo de origem fica em `fonte`.
"""

from __future__ import annotations

from pfc_busca.evaluation.gabarito import opcional, periodo, rel, um_de
from pfc_busca.schema import CENTROS_GEOINFORMACAO, TIPOS_PRODUTO

TOPO, TOPO_VET, ORTO, ORTO_P, ORTO_X, MDT, MDS, CIRC, TEMATICA = TIPOS_PRODUTO
SEM_PISTA = um_de("publicationDate", "creationDate")
SEM_PISTA_PROTOTIPO = um_de("creationDate", "publicationDate")
ESCALAS_GRANDES = um_de("1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000")
PER_SEM_VERBO = ("publicationPeriod", "creationPeriod")
ESTADO_OU_CAPITAL = ("state", "city")
ARQUIVO_P = "prototipo_busca_llm-main/backend/evaluation/test-cases.ts"


def cgeo(n: int) -> str:
    return CENTROS_GEOINFORMACAO[n - 1]


def caso(id_: str, cats: str, consulta: str, esperado: dict, *, trocas=(), fonte: str = "",
         espera_tool_call: bool = True, observacional: bool = False, notas: str = "") -> dict:
    return {
        "id": id_,
        "origem": id_[0],
        "familia": id_[0],
        "categorias": [c.strip() for c in cats.split("·")],
        "consulta": consulta,
        "esperado": esperado,
        "trocas": [list(t) for t in trocas],
        "fonte": fonte or ("autores" if id_[0] == "N" else ""),
        "espera_tool_call": espera_tool_call,
        "observacional": observacional,
        "notas": notas,
    }


def p(id_: str, linha: int, *args, **kwargs) -> dict:
    return caso(id_, *args, fonte=f"{ARQUIVO_P}:{linha}", **kwargs)


# ---------------------------------------------------------------------------
# P01-P22 — protótipo do 1º CGEO
# ---------------------------------------------------------------------------

CASOS_P = [
    p("P01", 6, "M · C", "preciso da carta MI 2965-2-NE do segundo cgeo",
      {"keyword": "2965-2-NE", "supplyArea": cgeo(2)}),
    p("P02", 16, "M · C", "folha MI 2866-3 em escala 50k",
      {"keyword": "2866-3", "scale": "1:50.000"}),
    p("P03", 26, "M · C · A", "MI 2901 do projeto olimpiadas",
      {"keyword": "2901", "project": "Olimpíadas Rio 2016"}),
    p("P04", 36, "M · C · A", "carta 530 em pequena escala",
      {"keyword": "530", "scale": "1:250.000"}),
    p("P05", 48, "M · C · T", "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano",
      {"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": rel("ano_corrente")}),
    p("P06", 62, "M · C · A", "carta SF-22-Y-D do tipo ortoimg",
      {"keyword": "SF-22-Y-D", "productType": ORTO}),
    p("P07", 72, "M · C · A", "inom SF-22-Y-D-II-4-SE criado pelo primeiro cgeo",
      {"keyword": "SF-22-Y-D-II-4-SE", "supplyArea": cgeo(1)}),
    p("P08", 84, "C", "carta topográfica Passo da Seringueira em 1:25.000",
      {"keyword": "Passo da Seringueira", "scale": "1:25.000", "productType": TOPO}),
    p("P09", 95, "C", "folha Porto Velho publicada em 2024",
      {"keyword": "Porto Velho", "publicationPeriod": periodo("2024-01-01", "2024-12-31")},
      trocas=[("keyword", "city")],
      notas="nome de carta coincide com município: aceita-se também city"),
    p("P10", 108, "C · A", "carta Vale do Guaporé do projeto rondonia",
      {"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}),
    p("P11", 120, "M · C · A", "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala",
      {"keyword": um_de("2965-2-NE", "SF-22-Y-D"), "supplyArea": cgeo(3), "scale": ESCALAS_GRANDES},
      notas="dois códigos (o schema comporta um): aceita-se qualquer um; 'grande escala' aceita as escalas grandes"),
    p("P12", 131, "M · C · T · A", "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano",
      {"keyword": um_de("530", "SF-22"), "productType": TOPO, "publicationPeriod": rel("ano_corrente")},
      notas="dois códigos: aceita-se qualquer um"),
    p("P13", 147, "C · A", "todas as cartas em escala maior que 100k do rio grande do sul",
      {"state": "Rio Grande do Sul",
       "scale": um_de("1:25.000", "1:50.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000")},
      notas="'maior que 100k' aceita qualquer escala maior que 1:100.000"),
    p("P14", 156, "C · A", "mapeamento detalhado (25k ou 50k) de brasilia",
      {"scale": um_de("1:25.000", "1:50.000"), "city": "Brasília"},
      notas="duas escalas explícitas: aceita-se qualquer uma"),
    p("P15", 167, "T · C · A", "cartas criadas no último trimestre do ano passado do segundo cgeo",
      {"supplyArea": cgeo(2), "creationPeriod": rel("ultimo_trimestre_ano_anterior")}),
    p("P16", 179, "T · C · A", "produtos da semana passada do terceiro cgeo",
      {"supplyArea": cgeo(3), "publicationPeriod": rel("semana_passada")},
      trocas=[PER_SEM_VERBO], notas="sem verbo que decida publicação ou criação"),
    p("P17", 193, "C · A", "cartas do mapeamento sistematico em goias",
      {"project": "Mapeamento Sistemático", "state": "Goiás"}),
    p("P18", 202, "C · A", "produtos da copa das confederacoes em fortaleza",
      {"project": "Copa das Confederações", "city": "Fortaleza"}),
    p("P19", 213, "O · C · A", "primeiro mapeamento feito em cuiaba",
      {"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": opcional(1)},
      notas="singular sem número: limit 1 opcional"),
    p("P20", 223, "O · C · A", "ultima atualizacao do para",
      {"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": opcional(1)},
      notas="singular sem número: limit 1 opcional"),
    p("P21", 235, "O · T · C · A",
      "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo "
      "em pernambuco publicadas depois de 2020",
      {"limit": 5, "productType": ORTO, "scale": "1:25.000", "supplyArea": cgeo(3), "state": "Pernambuco",
       "publicationPeriod": rel("depois_de_2020"), "sortField": SEM_PISTA_PROTOTIPO, "sortDirection": "ASC"},
      notas="'mais antigas' sem pista ligada à ordenação: aceita-se publicationDate além do creationDate original"),
    p("P22", 253, "M · O · T · C",
      "MI 2901 ou SF-22 do quarto cgeo no sudeste em pequena escala criado entre 2022 e 2023 "
      "ordem cronologica",
      {"keyword": um_de("2901", "SF-22"), "supplyArea": cgeo(4), "scale": "1:250.000",
       "creationPeriod": periodo("2022-01-01", "2023-12-31"),
       "sortField": SEM_PISTA_PROTOTIPO, "sortDirection": "ASC"},
      notas="dois códigos; 'sudeste' é região (nada a anotar); ordem cronológica sem pista ligada"),
]

# ---------------------------------------------------------------------------
# N01-N40 — curadoria dos autores
# ---------------------------------------------------------------------------

CASOS_N = [
    # Simples
    caso("N01", "S", "cartas de São Paulo", {"state": "São Paulo"}, trocas=[ESTADO_OU_CAPITAL],
         notas="'São Paulo' sem qualificador: estado ou capital"),
    caso("N02", "S", "produtos em escala 1:50.000", {"scale": "1:50.000"}),
    caso("N03", "S", "ortoimagens", {"productType": ORTO}),
    caso("N04", "S · A", "mapas do rj", {"state": "Rio de Janeiro"}),
    caso("N05", "S · A", "carta 25k", {"scale": "1:25.000"}),
    caso("N06", "S", "folha SF-22-Y-D", {"keyword": "SF-22-Y-D"}),
    caso("N07", "S · A", "modelos digitais de terreno", {"productType": MDT}),
    caso("N08", "S · A", "cartas topográficas", {"productType": TOPO}),
    caso("N09", "S", "produtos do Amazonas", {"state": "Amazonas"}),
    caso("N10", "S · A", "mi 2901", {"keyword": "2901"}),
    # Compostas
    caso("N11", "C", "cartas do 1º CGEO em Minas Gerais", {"supplyArea": cgeo(1), "state": "Minas Gerais"}),
    caso("N12", "C", "ortoimagens de Manaus em 1:50.000",
         {"productType": ORTO, "city": "Manaus", "scale": "1:50.000"}),
    caso("N13", "C · A", "mdt do para em 25k", {"productType": MDT, "state": "Pará", "scale": "1:25.000"}),
    # MI/INOM
    caso("N14", "M · C", "folha 2965-2 do Rio Grande do Sul", {"keyword": "2965-2", "state": "Rio Grande do Sul"}),
    caso("N15", "M · C", "INOM SG-22-X-A", {"keyword": "SG-22-X-A"}),
    caso("N16", "M · C · T", "carta MI 3010 publicada em 2023",
         {"keyword": "3010", "publicationPeriod": periodo("2023-01-01", "2023-12-31")}),
    # Tempo relativo
    caso("N17", "T · A", "produtos publicados nos últimos 3 meses", {"publicationPeriod": rel("ultimos_3_meses")}),
    caso("N18", "T · C", "cartas do ano passado em Roraima",
         {"state": "Roraima", "publicationPeriod": rel("ano_anterior")}, trocas=[PER_SEM_VERBO],
         notas="sem verbo que decida publicação ou criação"),
    caso("N19", "T · A", "atualizações deste mês", {"publicationPeriod": rel("mes_corrente")},
         trocas=[PER_SEM_VERBO], notas="sem verbo que decida publicação ou criação"),
    caso("N20", "T · C · A", "cartas dos últimos 5 anos em escala 100k",
         {"scale": "1:100.000", "publicationPeriod": rel("ultimos_5_anos")}, trocas=[PER_SEM_VERBO],
         notas="sem verbo que decida publicação ou criação"),
    caso("N21", "T · A", "qualquer coisa de hoje", {"publicationPeriod": rel("hoje")}, trocas=[PER_SEM_VERBO],
         notas="sem verbo que decida publicação ou criação"),
    caso("N22", "T · C · A", "ortoimagens de 2 anos atrás",
         {"productType": ORTO, "publicationPeriod": rel("dois_anos_atras")}, trocas=[PER_SEM_VERBO],
         notas="sem verbo que decida publicação ou criação"),
    caso("N23", "T · C · A", "produtos do trimestre passado do 4º CGEO",
         {"supplyArea": cgeo(4), "publicationPeriod": rel("trimestre_anterior")}, trocas=[PER_SEM_VERBO],
         notas="sem verbo que decida publicação ou criação"),
    # Ordenação
    caso("N24", "O · C", "3 cartas mais recentes de Curitiba",
         {"city": "Curitiba", "limit": 3, "sortField": SEM_PISTA, "sortDirection": "DESC"},
         notas="'mais recentes' sem pista: aceita-se publicationDate ou creationDate"),
    caso("N25", "O · C", "10 primeiras ortoimagens do Nordeste",
         {"productType": ORTO, "limit": 10, "sortField": SEM_PISTA, "sortDirection": "ASC"},
         notas="'Nordeste' é região (nada a anotar); 'primeiras' sem pista"),
    caso("N26", "O · C · A", "mais antigas em rondonia",
         {"state": "Rondônia", "sortField": SEM_PISTA, "sortDirection": "ASC"},
         notas="'mais antigas' sem pista"),
    caso("N27", "O · C", "últimas 5 publicações",
         {"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}),
    caso("N28", "O · M · C", "carta MI 2901 mais recente",
         {"keyword": "2901", "sortField": SEM_PISTA, "sortDirection": "DESC", "limit": opcional(1)},
         notas="singular sem número: limit 1 opcional; 'mais recente' sem pista"),
    caso("N29", "O · C · T", "três produtos mais antigos deste ano",
         {"limit": 3, "publicationPeriod": rel("ano_corrente"), "sortField": SEM_PISTA, "sortDirection": "ASC"},
         trocas=[PER_SEM_VERBO], notas="sem verbo que decida o período; 'mais antigos' sem pista"),
    # Ambíguas / informais
    caso("N30", "A · C", "cartas topo do primeiro cgeo", {"productType": TOPO, "supplyArea": cgeo(1)}),
    caso("N31", "A · S", "orto banda p", {"productType": ORTO_P}),
    caso("N32", "A · C", "mapas do rio em cem k", {"state": "Rio de Janeiro", "scale": "1:100.000"},
         trocas=[ESTADO_OU_CAPITAL], notas="'rio' é ambíguo entre o estado e a capital"),
    caso("N33", "A · C", "cartografia sistematica sp",
         {"project": opcional("Mapeamento Sistemático"), "state": "São Paulo"},
         notas="'cartografia sistemática' designa o programa pelo termo distintivo do nome, sem ser nome nem "
               "apelido informado na ferramenta: project é opcional (regra de project; adjudicação)"),
    caso("N34", "A · C", "ortos da amazonia legal", {"productType": ORTO},
         notas="'Amazônia Legal' é região (nove estados), não estado: nada a anotar para ela"),
    caso("N35", "A · M · C", "sf22yd do dois cgeo", {"keyword": "SF-22-Y-D", "supplyArea": cgeo(2)}),
    # Fronteira do domínio: N36-N37 fora do domínio (P4, categoria F); N38-N40 observacionais (P6)
    caso("N36", "F", "cartas fora do brasil", {}, espera_tool_call=False,
         notas="fora do território brasileiro, P4"),
    caso("N37", "F", "quero um mapa bonito", {}, espera_tool_call=False,
         notas="sem critério de busca, P4"),
    caso("N38", "S · A", "escala 1:10.000.000", {}, espera_tool_call=False, observacional=True,
         notas="observacional, P6: escala fora do enumerado da ferramenta"),
    caso("N39", "C · A", "cartas topo no oceano atlântico", {"productType": TOPO}, observacional=True,
         notas="área não terrestre: comportamento esperado discutível"),
    caso("N40", "C · T", "cartas do futuro (ano 2050)",
         {"publicationPeriod": periodo("2050-01-01", "2050-12-31")}, trocas=[PER_SEM_VERBO], observacional=True,
         notas="data futura: comportamento esperado discutível"),
]

CASOS_MANUAIS = CASOS_P + CASOS_N

assert len(CASOS_P) == 22 and len(CASOS_N) == 40
