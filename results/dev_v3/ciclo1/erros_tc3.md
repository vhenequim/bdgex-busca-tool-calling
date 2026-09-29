# Erros de tc3- no ciclo 1: 20 de 160

Campos: FP:publicationPeriod 9, FN:productType 3, FN:city 3, FN:publicationPeriod 3, FP:keyword 2, FN:creationPeriod 2, FP:creationPeriod 2, FN:state 1, FN:supplyArea 1, FP:sortDirection 1, FN:keyword 1

Regressões (a outra, t4:se-, acertou): 8 — VS0030, VS0220, VT0053, VT0093, VT0159, VT0216, VT0232, VA0019
Ganhos (a outra errou): 37

## VA0019 [C,A] **(regressão)**
- consulta: Venho, por meio desta, pedir a carta Pacaraima entre as cartas topo, para uso da prefeitura.
- esperado: {'keyword': 'Pacaraima', 'productType': 'SCN Carta Topográfica Matricial'} | alternativas: [{'productType': 'SCN Carta Topográfica Matricial', 'city': 'Pacaraima'}]
- predito: None
- FP [] FN ['keyword', 'productType']
- ferramentas: {'recusar_consulta': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'keyword-ou-city', 'tipo-so-quando-nomeado']

## VA0155 [S,A]
- consulta: Vou dar apoio a um levantamento de campo e preciso das cartas topográficas vetoriais da região Sul para montar o material da equipe.
- esperado: {'productType': 'SCN Carta Topográfica Vetorial'}
- predito: None
- FP [] FN ['productType']
- ferramentas: {}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'regiao-nao-e-filtro', 'tipo-so-quando-nomeado']

## VC0101 [C,A]
- consulta: cartas topográficas PB 50k BCD do Amapá
- esperado: {'productType': 'SCN Carta Topográfica Matricial', 'project': 'Base Cartográfica Digital do Amapá', 'state': 'Paraíba', 'scale': '1:50.000'}
- predito: {'keyword': 'PB', 'scale': '1:50.000', 'productType': 'SCN Carta Topográfica Matricial', 'state': 'Paraíba', 'project': 'Base Cartográfica Digital do Amapá'}
- FP ['keyword'] FN []
- ferramentas: {'normalizar_escala': 1, 'normalizar_codigo': 2, 'buscar_catalogo': 2}; avisos: 1; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'projeto-nao-e-estado', 'tipo-so-quando-nomeado', 'uf-por-extenso']

## VC0305 [C,A]
- consulta: Estou procurnado a folha Cajueiro Alto Alegre, de Tesouro (MT), escala 50 mil.
- esperado: {'keyword': 'Cajueiro Alto Alegre', 'city': 'Tesouro', 'state': 'Mato Grosso', 'scale': '1:50.000'}
- predito: {'keyword': 'Cajueiro Alto Alegre, Tesouro', 'scale': '1:50.000', 'state': 'Mato Grosso'}
- FP ['keyword'] FN ['city']
- ferramentas: {'identificar_nome': 1, 'normalizar_escala': 1, 'buscar_catalogo': 2}; avisos: 1; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'keyword-ou-city', 'tipo-so-quando-nomeado', 'uf-por-extenso']

## VO0072 [C,M,O]
- consulta: me mostra as versões mais recentes da carta MI 1906-3-SE de Flexeiras, pela data de atualização
- esperado: {'sortField': 'creationDate', 'sortDirection': 'DESC', 'keyword': '1906-3-SE', 'city': 'Flexeiras'}
- predito: {'keyword': '1906-3-SE', 'sortField': 'creationDate', 'sortDirection': 'DESC'}
- FP [] FN ['city']
- ferramentas: {'normalizar_codigo': 1, 'identificar_nome': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['codigo-sem-prefixo', 'esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado', 'uf-por-extenso']

## VS0030 [S] **(regressão)**
- consulta: Existe algum mapa de Sergipe no acervo?
- esperado: {'state': 'Sergipe'}
- predito: {}
- FP [] FN ['state']
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'municipio-inteiro', 'tipo-so-quando-nomeado']

## VS0220 [S] **(regressão)**
- consulta: me passa umas ortoimagens aí? tô precisando pra uma obra
- esperado: {'productType': 'SCN Carta Ortoimagem'}
- predito: None
- FP [] FN ['productType']
- ferramentas: {'recusar_consulta': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'tipo-so-quando-nomeado']

## VT0004 [C,T]
- consulta: consegue me mostrar as cartas de Cromínia publicadas este mês?
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2026-09-01', 'end': '2026-09-24'}, {'start': '2026-09-01', 'end': '2026-09-30'}]}, 'city': 'Cromínia'}
- predito: None
- FP [] FN ['city', 'publicationPeriod']
- ferramentas: {'recusar_consulta': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'municipio-inteiro', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0005 [C,T,A]
- consulta: cartas do primeiro cgeo publicadas nos últimos 3 anos
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2023-09-24', 'end': '2026-09-24'}, {'start': '2023-01-01', 'end': '2026-09-24'}]}, 'supplyArea': '1° Centro de Geoinformação'}
- predito: {'supplyArea': '1° Centro de Geoinformação', 'publicationPeriod': {'start': '2024-09-24', 'end': '2026-09-24'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0053 [T] **(regressão)**
- consulta: rola de achar cartas feitas antes de 2010? é pra um trabalho da facul
- esperado: {'creationPeriod': {'end': '2009-12-31'}}
- predito: {'publicationPeriod': {'end': '2009-12-31'}, 'creationPeriod': {'end': '2009-12-31'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'pedir_esclarecimento': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 1; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0082 [C,T,A]
- consulta: cartas do segundo cgeo no ano passado
- esperado: {'publicationPeriod': {'start': '2025-01-01', 'end': '2025-12-31'}, 'supplyArea': '2° Centro de Geoinformação'} | alternativas: [{'supplyArea': '2° Centro de Geoinformação', 'creationPeriod': {'start': '2025-01-01', 'end': '2025-12-31'}}]
- predito: None
- FP [] FN ['publicationPeriod', 'supplyArea']
- ferramentas: {}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0093 [T] **(regressão)**
- consulta: Quais cartas foram criadas desde 2010? Vocês têm isso no acervo?
- esperado: {'creationPeriod': {'$um_de': [{'start': '2010-01-01', 'end': '2026-09-24'}, {'start': '2010-01-01'}]}}
- predito: {'publicationPeriod': {'start': '2010-01-01'}, 'creationPeriod': {'start': '2010-01-01'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0117 [C,T,A]
- consulta: ortoimg elaboradas no ano de 2010
- esperado: {'creationPeriod': {'start': '2010-01-01', 'end': '2010-12-31'}, 'productType': 'SCN Carta Ortoimagem'}
- predito: {'productType': 'SCN Carta Ortoimagem', 'publicationPeriod': {'start': '2010-01-01', 'end': '2010-12-31'}}
- FP ['publicationPeriod'] FN ['creationPeriod']
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0118 [C,T,A]
- consulta: Vocês têm MDT de Cáceres publicado dentro dos últimos 5 anos?
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2021-09-24', 'end': '2026-09-24'}, {'start': '2021-01-01', 'end': '2026-09-24'}]}, 'city': 'Cáceres', 'productType': 'MDT — RAM'}
- predito: {'productType': 'MDT — RAM', 'city': 'Cáceres', 'publicationPeriod': {'start': '2021-09-24'}, 'sortDirection': 'DESC'}
- FP ['publicationPeriod', 'sortDirection'] FN []
- ferramentas: {'identificar_nome': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0159 [T,A] **(regressão)**
- consulta: lista de cartas nos últimos três meses
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2026-06-26', 'end': '2026-09-24'}, {'start': '2026-06-24', 'end': '2026-09-24'}]}} | alternativas: [{'creationPeriod': {'$um_de': [{'start': '2026-06-26', 'end': '2026-09-24'}, {'start': '2026-06-24', 'end': '2026-09-24'}]}}]
- predito: {'publicationPeriod': {'start': '2026-06-25', 'end': '2026-09-24'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0184 [T]
- consulta: Gostaria de solicitar a relação das cartas publicadas dois anos atrás, para análise da nossa equipe técnica.
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2024-01-01', 'end': '2024-12-31'}, {'start': '2024-09-24', 'end': '2026-09-24'}]}}
- predito: {'publicationPeriod': {'start': '2022-09-24', 'end': '2024-09-24'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'pedir_esclarecimento': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 1; orientações: ['esclarecer-so-sem-criterio', 'tipo-so-quando-nomeado']

## VT0216 [C,T,A] **(regressão)**
- consulta: cartas temáticas do terceiro cgeo publicadas nos últimos 2 meses
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2026-07-26', 'end': '2026-09-24'}, {'start': '2026-07-24', 'end': '2026-09-24'}]}, 'productType': 'Cartas Temáticas Não SCN', 'supplyArea': '3° Centro de Geoinformação'}
- predito: {'productType': 'Cartas Temáticas Não SCN', 'supplyArea': '3° Centro de Geoinformação', 'publicationPeriod': {'start': '2026-07-25', 'end': '2026-09-24'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0218 [C,T,A]
- consulta: Tem cartas de 50 mil feitas depois de 2019? Separa pra mim.
- esperado: {'creationPeriod': {'$um_de': [{'start': '2019-01-01', 'end': '2026-09-24'}, {'start': '2019-01-01'}, {'start': '2020-01-01', 'end': '2026-09-24'}, {'start': '2020-01-01'}]}, 'scale': '1:50.000'}
- predito: {'scale': '1:50.000', 'publicationPeriod': {'start': '2020-01-01', 'end': '2026-09-24'}}
- FP ['publicationPeriod'] FN ['creationPeriod']
- ferramentas: {'normalizar_escala': 1, 'resolver_periodo': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'municipio-inteiro', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0228 [C,T]
- consulta: Existem modelos digitais de superfície publicados após 2020?
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2020-01-01', 'end': '2026-09-24'}, {'start': '2020-01-01'}, {'start': '2021-01-01', 'end': '2026-09-24'}, {'start': '2021-01-01'}]}, 'productType': 'MDS — RAM'}
- predito: {'productType': 'MDS — RAM', 'creationPeriod': {'start': '2021-01-01'}}
- FP ['creationPeriod'] FN ['publicationPeriod']
- ferramentas: {'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']

## VT0232 [C,T,A] **(regressão)**
- consulta: modelos digitais de superfície do segundo cgeo, dois anos atrás
- esperado: {'publicationPeriod': {'$um_de': [{'start': '2024-01-01', 'end': '2024-12-31'}, {'start': '2024-09-24', 'end': '2026-09-24'}]}, 'productType': 'MDS — RAM', 'supplyArea': '2° Centro de Geoinformação'} | alternativas: [{'productType': 'MDS — RAM', 'supplyArea': '2° Centro de Geoinformação', 'creationPeriod': {'$um_de': [{'start': '2024-01-01', 'end': '2024-12-31'}, {'start': '2024-09-24', 'end': '2026-09-24'}]}}]
- predito: {'productType': 'MDS — RAM', 'supplyArea': '2° Centro de Geoinformação', 'creationPeriod': {'start': '2022-09-24', 'end': '2024-09-24'}}
- FP ['creationPeriod'] FN []
- ferramentas: {'normalizar_escala': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'tipo-so-quando-nomeado']
