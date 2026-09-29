# Erros de tc3- no ciclo 2: 5 de 160

Campos: FP:city 2, FP:keyword 1, FP:publicationPeriod 1, FP:limit 1

## VA0121 [C,A]
- consulta: Tenho que fechar um relatório técnico para a chefia e preciso da folha Santana do Garambeu em 1:50000.
- esperado: {'keyword': 'Santana do Garambeu', 'scale': '1:50.000'} | alternativas: [{'scale': '1:50.000', 'city': 'Santana do Garambeu'}]
- predito: {'keyword': 'Santana do Garambeu', 'scale': '1:50.000', 'city': 'Santana do Garambéu'}
- FP ['city'] FN []
- ferramentas: {'identificar_nome': 1, 'normalizar_escala': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'keyword-ou-city', 'lugar-brasileiro-desconhecido', 'tipo-so-quando-nomeado']

## VC0101 [C,A]
- consulta: cartas topográficas PB 50k BCD do Amapá
- esperado: {'productType': 'SCN Carta Topográfica Matricial', 'project': 'Base Cartográfica Digital do Amapá', 'state': 'Paraíba', 'scale': '1:50.000'}
- predito: {'keyword': 'BCD do Amapá', 'scale': '1:50.000', 'productType': 'SCN Carta Topográfica Matricial', 'state': 'Paraíba', 'project': 'Base Cartográfica Digital do Amapá'}
- FP ['keyword'] FN []
- ferramentas: {'normalizar_escala': 1, 'identificar_nome': 1, 'normalizar_codigo': 1, 'buscar_catalogo': 2}; avisos: 1; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'lugar-brasileiro-desconhecido', 'projeto-nao-e-estado', 'tipo-so-quando-nomeado', 'uf-por-extenso']

## VE0013 [E]
- consulta: Onde eu acho mapas do litoral brasileiro para mostrar aos alunos?
- esperado: {}
- predito: {'city': 'litoral brasileiro'}
- FP ['city'] FN []
- ferramentas: {'buscar_catalogo': 2}; avisos: 1; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'regiao-nao-e-filtro', 'tipo-so-quando-nomeado']

## VO0013 [C,M,O,A]
- consulta: mi 0084-4 do terceiro cgeo, as mais recentes primeiro
- esperado: {'sortField': {'$um_de': ['publicationDate', 'creationDate']}, 'sortDirection': 'DESC', 'supplyArea': '3° Centro de Geoinformação', 'keyword': '0084-4'}
- predito: {'keyword': '0084-4', 'supplyArea': '3° Centro de Geoinformação', 'sortField': 'creationDate', 'sortDirection': 'DESC', 'limit': 1}
- FP ['limit'] FN []
- ferramentas: {'normalizar_codigo': 1, 'buscar_catalogo': 1}; avisos: 0; perguntas: 0; orientações: ['codigo-sem-prefixo', 'esclarecer-so-sem-criterio', 'limite-so-com-numero', 'ordenacao-so-quando-pedida', 'tipo-so-quando-nomeado']

## VT0082 [C,T,A]
- consulta: cartas do segundo cgeo no ano passado
- esperado: {'publicationPeriod': {'start': '2025-01-01', 'end': '2025-12-31'}, 'supplyArea': '2° Centro de Geoinformação'} | alternativas: [{'supplyArea': '2° Centro de Geoinformação', 'creationPeriod': {'start': '2025-01-01', 'end': '2025-12-31'}}]
- predito: {'supplyArea': '2° Centro de Geoinformação', 'publicationPeriod': {'start': '2024-01-01', 'end': '2024-12-31'}}
- FP ['publicationPeriod'] FN []
- ferramentas: {'buscar_catalogo': 3}; avisos: 2; perguntas: 0; orientações: ['esclarecer-so-sem-criterio', 'periodo-intervalo-inteiro', 'tipo-so-quando-nomeado']
