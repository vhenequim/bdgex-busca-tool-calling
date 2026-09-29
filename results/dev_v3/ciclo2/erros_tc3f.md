# Erros de tc3f- no ciclo 2: 5 de 160

Campos: FN:creationPeriod 1, FP:limit 1, FP:scale 1, FP:city 1, FN:scale 1, FN:productType 1

## VA0080 [C,A]
- consulta: cartas topo em escala maior que 100k
- esperado: {'scale': {'$um_de': ['1:50.000', '1:25.000', '1:10.000', '1:5.000', '1:2.000', '1:1.000']}, 'productType': 'SCN Carta Topográfica Matricial'}
- predito: {'scale': '1:250.000', 'productType': 'SCN Carta Topográfica Matricial'}
- FP ['scale'] FN []
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 1; orientações: []

## VA0115 [C,A]
- consulta: cadê a folha Buritirama em escala detalhada? tô precisando
- esperado: {'keyword': 'Buritirama', 'scale': '1:25.000'} | alternativas: [{'scale': '1:25.000', 'city': 'Buritirama'}]
- predito: {'keyword': 'Buritirama', 'scale': '1:25.000', 'city': 'Buritirama'}
- FP ['city'] FN []
- ferramentas: {'identificar_nome': 1, 'normalizar_escala': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 1; orientações: []

## VA0119 [C,A]
- consulta: Estou preparando uma análise de escoamento para um estudo interno e preciso de MDTs em grande escala.
- esperado: {'scale': {'$um_de': ['1:25.000', '1:10.000', '1:5.000', '1:2.000', '1:1.000']}, 'productType': 'MDT — RAM'}
- predito: None
- FP [] FN ['productType', 'scale']
- ferramentas: {'pedir_esclarecimento': 2, 'normalizar_escala': 2}; avisos: 0; perguntas: 4; orientações: []

## VO0013 [C,M,O,A]
- consulta: mi 0084-4 do terceiro cgeo, as mais recentes primeiro
- esperado: {'sortField': {'$um_de': ['publicationDate', 'creationDate']}, 'sortDirection': 'DESC', 'supplyArea': '3° Centro de Geoinformação', 'keyword': '0084-4'}
- predito: {'keyword': '0084-4', 'supplyArea': '3° Centro de Geoinformação', 'sortField': 'publicationDate', 'sortDirection': 'DESC', 'limit': 1}
- FP ['limit'] FN []
- ferramentas: {'normalizar_codigo': 1, 'normalizar_escala': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: []

## VT0053 [T]
- consulta: rola de achar cartas feitas antes de 2010? é pra um trabalho da facul
- esperado: {'creationPeriod': {'end': '2009-12-31'}}
- predito: {}
- FP [] FN ['creationPeriod']
- ferramentas: {'buscar_catalogo': 3}; avisos: 0; perguntas: 0; orientações: []
