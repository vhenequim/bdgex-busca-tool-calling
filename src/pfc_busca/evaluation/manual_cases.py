"""Camadas P (protótipo, 22) e N (autores, 40) do dataset, estruturadas.

Transcrição fiel do Apêndice A (`paper_revisado/apendice.tex`), com três
ajustes de representação que o LaTeX não exige mas a máquina exige:

1. `supplyArea` usa o valor do enum ("2° Centro de Geoinformação"), não a
   abreviação "2° CGEO" do apêndice.
2. Períodos relativos viram `{"rel": <regra>}` (ver `relative_time.py`);
   períodos absolutos viram `{"start", "end"}` em ISO.
3. Casos de fronteira (N36-N40) e um caso de gabarito incerto (N34) recebem
   `observacional=True`: entram no relatório, mas fora das métricas
   principais, como o Sumário VE->VC já previa para a família G-F.

Notas marcadas "gabarito herdado do protótipo" preservam a anotação da
equipe do 1º CGEO mesmo onde ela é discutível — a camada P é o baseline e
não se reanota baseline.
"""

from __future__ import annotations

from pfc_busca.schema import (
    CENTROS_GEOINFORMACAO,
    TIPOS_PRODUTO,
)

TOPO, TOPO_VET, ORTO, ORTO_P, ORTO_X, MDT, MDS, CIRC, TEMATICA = TIPOS_PRODUTO


def cgeo(n: int) -> str:
    return CENTROS_GEOINFORMACAO[n - 1]


def periodo(start: str, end: str) -> dict:
    return {"start": start, "end": end}


def rel(regra: str) -> dict:
    return {"rel": regra}


def caso(id_: str, cats: str, consulta: str, esperado: dict, *,
         espera_tool_call: bool = True, observacional: bool = False,
         notas: str = "") -> dict:
    return {
        "id": id_,
        "origem": id_[0],
        "familia": id_[0],
        "categorias": [c.strip() for c in cats.split("·")],
        "consulta": consulta,
        "esperado": esperado,
        "espera_tool_call": espera_tool_call,
        "observacional": observacional,
        "notas": notas,
    }


# ---------------------------------------------------------------------------
# P01-P22 — protótipo do 1º CGEO (backend/evaluation/test-cases.ts)
# ---------------------------------------------------------------------------

CASOS_P = [
    caso("P01", "M · C", "preciso da carta MI 2965-2-NE do segundo cgeo",
         {"keyword": "2965-2-NE", "supplyArea": cgeo(2)}),
    caso("P02", "M · C", "folha MI 2866-3 em escala 50k",
         {"keyword": "2866-3", "scale": "1:50.000"}),
    caso("P03", "M · C · A", "MI 2901 do projeto olimpiadas",
         {"keyword": "2901", "project": "Olimpíadas Rio 2016"}),
    caso("P04", "M · C · A", "carta 530 em pequena escala",
         {"keyword": "530", "scale": "1:250.000"}),
    caso("P05", "M · C · T", "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano",
         {"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul",
          "publicationPeriod": rel("ano_corrente")}),
    caso("P06", "M · C · A", "carta SF-22-Y-D do tipo ortoimg",
         {"keyword": "SF-22-Y-D", "productType": ORTO}),
    caso("P07", "M · C · A", "inom SF-22-Y-D-II-4-SE criado pelo primeiro cgeo",
         {"keyword": "SF-22-Y-D-II-4-SE", "supplyArea": cgeo(1)}),
    caso("P08", "C", "carta topográfica Passo da Seringueira em 1:25.000",
         {"keyword": "Passo da Seringueira", "scale": "1:25.000", "productType": TOPO}),
    caso("P09", "C", "folha Porto Velho publicada em 2024",
         {"keyword": "Porto Velho", "publicationPeriod": periodo("2024-01-01", "2024-12-31")}),
    caso("P10", "C · A", "carta Vale do Guaporé do projeto rondonia",
         {"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}),
    caso("P11", "M · C · A", "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala",
         {"keyword": "2965-2-NE", "supplyArea": cgeo(3), "scale": "1:25.000"},
         notas="gabarito herdado do protótipo: dois códigos, fica o primeiro; 'grande escala' → 1:25.000"),
    caso("P12", "M · C · T · A", "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano",
         {"keyword": "530", "productType": TOPO, "publicationPeriod": rel("ano_corrente")},
         notas="gabarito herdado do protótipo: dois códigos, fica o primeiro"),
    caso("P13", "C · A", "todas as cartas em escala maior que 100k do rio grande do sul",
         {"state": "Rio Grande do Sul", "scale": "1:25.000"},
         notas="gabarito herdado do protótipo: 'maior que 100k' → 1:25.000"),
    caso("P14", "C · A", "mapeamento detalhado (25k ou 50k) de brasilia",
         {"scale": "1:25.000", "city": "Brasília"},
         notas="gabarito herdado do protótipo: duas escalas, fica a mais detalhada"),
    caso("P15", "T · C · A", "cartas criadas no último trimestre do ano passado do segundo cgeo",
         {"supplyArea": cgeo(2), "creationPeriod": rel("ultimo_trimestre_ano_anterior")}),
    caso("P16", "T · C · A", "produtos da semana passada do terceiro cgeo",
         {"supplyArea": cgeo(3), "publicationPeriod": rel("semana_passada")}),
    caso("P17", "C · A", "cartas do mapeamento sistematico em goias",
         {"project": "Mapeamento Sistemático", "state": "Goiás"}),
    caso("P18", "C · A", "produtos da copa das confederacoes em fortaleza",
         {"project": "Copa das Confederações", "city": "Fortaleza"}),
    caso("P19", "O · C · A", "primeiro mapeamento feito em cuiaba",
         {"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC"}),
    caso("P20", "O · C · A", "ultima atualizacao do para",
         {"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC"}),
    caso("P21", "O · T · C · A",
         "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo "
         "em pernambuco publicadas depois de 2020",
         {"limit": 5, "productType": ORTO, "scale": "1:25.000", "supplyArea": cgeo(3),
          "state": "Pernambuco", "publicationPeriod": rel("desde_2020"),
          "sortField": "creationDate", "sortDirection": "ASC"}),
    caso("P22", "M · O · T · C",
         "MI 2901 ou SF-22 do quarto cgeo no sudeste em pequena escala criado entre 2022 e 2023 "
         "ordem cronologica",
         {"keyword": "2901", "supplyArea": cgeo(4), "scale": "1:250.000",
          "creationPeriod": periodo("2022-01-01", "2023-12-31"),
          "sortField": "creationDate", "sortDirection": "ASC"},
         notas="gabarito herdado do protótipo: 'sudeste' não vira parâmetro"),
]

# ---------------------------------------------------------------------------
# N01-N40 — curadoria dos autores
# ---------------------------------------------------------------------------

CASOS_N = [
    # Simples
    caso("N01", "S", "cartas de São Paulo", {"state": "São Paulo"}),
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
    caso("N11", "C", "cartas do 1º CGEO em Minas Gerais",
         {"supplyArea": cgeo(1), "state": "Minas Gerais"}),
    caso("N12", "C", "ortoimagens de Manaus em 1:50.000",
         {"productType": ORTO, "city": "Manaus", "scale": "1:50.000"}),
    caso("N13", "C · A", "mdt do para em 25k",
         {"productType": MDT, "state": "Pará", "scale": "1:25.000"}),
    # MI/INOM
    caso("N14", "M · C", "folha 2965-2 do Rio Grande do Sul",
         {"keyword": "2965-2", "state": "Rio Grande do Sul"}),
    caso("N15", "M · C", "INOM SG-22-X-A", {"keyword": "SG-22-X-A"}),
    caso("N16", "M · C · T", "carta MI 3010 publicada em 2023",
         {"keyword": "3010", "publicationPeriod": periodo("2023-01-01", "2023-12-31")}),
    # Tempo relativo
    caso("N17", "T · A", "produtos publicados nos últimos 3 meses",
         {"publicationPeriod": rel("ultimos_90_dias")}),
    caso("N18", "T · C", "cartas do ano passado em Roraima",
         {"state": "Roraima", "publicationPeriod": rel("ano_anterior")}),
    caso("N19", "T · A", "atualizações deste mês", {"publicationPeriod": rel("mes_corrente")}),
    caso("N20", "T · C · A", "cartas dos últimos 5 anos em escala 100k",
         {"scale": "1:100.000", "publicationPeriod": rel("ultimos_5_anos")}),
    caso("N21", "T · A", "qualquer coisa de hoje", {"publicationPeriod": rel("hoje")}),
    caso("N22", "T · C · A", "ortoimagens de 2 anos atrás",
         {"productType": ORTO, "publicationPeriod": rel("dois_anos_atras")}),
    caso("N23", "T · C · A", "produtos do trimestre passado do 4º CGEO",
         {"supplyArea": cgeo(4), "creationPeriod": rel("trimestre_anterior")}),
    # Ordenação
    caso("N24", "O · C", "3 cartas mais recentes de Curitiba",
         {"city": "Curitiba", "limit": 3, "sortField": "publicationDate", "sortDirection": "DESC"},
         notas="gabarito harmonizado com a camada G: 'mais recente(s)/antiga(s)' → publicationDate; 'feito/criado' → creationDate"),
    caso("N25", "O · C", "10 primeiras ortoimagens do Nordeste",
         {"productType": ORTO, "limit": 10, "sortField": "creationDate", "sortDirection": "ASC"},
         notas="'Nordeste' não mapeia a um único estado; gabarito não inclui state"),
    caso("N26", "O · C · A", "mais antigas em rondonia",
         {"state": "Rondônia", "sortField": "publicationDate", "sortDirection": "ASC"},
         notas="gabarito harmonizado com a camada G (ver N24)"),
    caso("N27", "O · C", "últimas 5 publicações",
         {"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}),
    caso("N28", "O · M · C", "carta MI 2901 mais recente",
         {"keyword": "2901", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}),
    caso("N29", "O · C · T", "três produtos mais antigos deste ano",
         {"limit": 3, "publicationPeriod": rel("ano_corrente"),
          "sortField": "publicationDate", "sortDirection": "ASC"}),
    # Ambíguas / informais
    caso("N30", "A · C", "cartas topo do primeiro cgeo", {"productType": TOPO, "supplyArea": cgeo(1)}),
    caso("N31", "A · S", "orto banda p", {"productType": ORTO_P}),
    caso("N32", "A · C", "mapas do rio em cem k", {"state": "Rio de Janeiro", "scale": "1:100.000"}),
    caso("N33", "A · C", "cartografia sistematica sp",
         {"project": "Mapeamento Sistemático", "state": "São Paulo"}),
    caso("N34", "A · C", "ortos da amazonia legal", {"productType": ORTO, "state": "Amazonas"},
         observacional=True,
         notas="gabarito incerto: 'Amazônia Legal' abrange nove estados, não só o Amazonas"),
    caso("N35", "A · M · C", "sf22yd do dois cgeo", {"keyword": "SF-22-Y-D", "supplyArea": cgeo(2)}),
    # Fronteira (observacionais)
    caso("N36", "S", "cartas fora do brasil", {}, espera_tool_call=False, observacional=True,
         notas="fora do domínio: nenhum parâmetro extraível"),
    caso("N37", "A", "quero um mapa bonito", {}, espera_tool_call=False, observacional=True,
         notas="subespecífico: nenhum parâmetro extraível"),
    caso("N38", "S · A", "escala 1:10.000.000", {}, espera_tool_call=False, observacional=True,
         notas="valor fora do enum de escalas; qualquer scale emitido é falso positivo"),
    caso("N39", "C · A", "cartas topo no oceano atlântico", {"productType": TOPO},
         observacional=True, notas="área não terrestre: state/city emitidos são falso positivo"),
    caso("N40", "C · T", "cartas do futuro (ano 2050)",
         {"publicationPeriod": periodo("2050-01-01", "2050-12-31")}, observacional=True,
         notas="gabarito determinístico; SQL válida com zero registros esperados"),
]

CASOS_MANUAIS = CASOS_P + CASOS_N

assert len(CASOS_P) == 22 and len(CASOS_N) == 40
