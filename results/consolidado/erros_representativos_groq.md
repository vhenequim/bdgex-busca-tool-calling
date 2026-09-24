# Erros representativos (amostra aleatória por tipo, semente 42)

## GPT-OSS 20B (Groq)

### valor_errado (13 casos)

- **GT033** — "produtos do 5 CGEO publicados na semana passada"
  - esperado: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-18", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N23** — "produtos do trimestre passado do 4º CGEO"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-04-01", "end": "2026-06-30"}}`
  - predito: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-07-01", "end": "2026-09-30"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-18", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GC012** — "cartas da paraíba na escala 1:25000"
  - esperado: `{"state": "Paraíba", "scale": "1:25.000"}`
  - predito: `{"scale": "1:250.000", "state": "Paraíba"}`
  - FP ['scale'] · FN [] · fora do schema []

### campo_omitido (11 casos)

- **GO001** — "a carta mais recente do CE"
  - esperado: `{"state": "Ceará", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `{"state": "Ceará"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GO018** — "as 5 cartas mais antigas publicadas nos últimos 5 anos"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2021-09-24", "end": "2026-09-24"}, {"start": "2021-01-01", "end": "2026-09-24"}]}, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC", "limit": 5}`
  - predito: `{"publicationPeriod": {"start": "2021-09-24", "end": "2026-09-24"}, "limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "limit": 10}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P22** — "MI 2901 ou SF-22 do quarto cgeo no sudeste em pequena escala criado entre 2022 e 2023 ordem cronologica"
  - esperado: `{"keyword": {"$um_de": ["2901", "SF-22"]}, "supplyArea": "4° Centro de Geoinformação", "scale": "1:250.000", "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"keyword": "2901", "supplyArea": "4° Centro de Geoinformação", "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": "creationDate", "sortDirection": "ASC"}`
  - FP [] · FN ['scale'] · fora do schema []

### campo_inventado (5 casos)

- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "state": "Rio Grande do Sul"}`
  - FP ['state'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "amazonia legal", "productType": "SCN Carta Ortoimagem", "state": "Pará"}`
  - FP ['keyword', 'state'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "state": "Rio de Janeiro", "city": "Rio de Janeiro"}`
  - FP ['city'] · FN [] · fora do schema []

### misto (2 casos)

- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"state": "Rondônia", "city": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - FP ['city', 'state'] · FN ['keyword'] · fora do schema []
- **GO011** — "as cartas temáticas mais recentes"
  - esperado: `{"productType": "Cartas Temáticas Não SCN", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"productType": "Cartas Temáticas Não SCN", "publicationPeriod": {"start": "2026-06-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['sortDirection', 'sortField'] · fora do schema []

### nao_chamou (2 casos)

- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []
- **GC050** — "produtos do projeto BCD de Rondônia no pará"
  - esperado: `{"project": "Base Cartográfica Digital de Rondônia", "state": "Pará"}`
  - predito: `null`
  - FP [] · FN ['project', 'state'] · fora do schema []

## GPT-OSS 120B (Groq)

### campo_inventado (9 casos)

- **GS047** — "cartas de Recife"
  - esperado: `{"city": "Recife"}`
  - predito: `{"state": "Pernambuco", "city": "Recife"}`
  - FP ['state'] · FN [] · fora do schema []
- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "city": "Brasília"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GC031** — "mapas de Recife na escala 1:50000"
  - esperado: `{"city": "Recife", "scale": "1:50.000"}`
  - predito: `{"scale": "1:50.000", "state": "Pernambuco", "city": "Recife"}`
  - FP ['state'] · FN [] · fora do schema []
- **P18** — "produtos da copa das confederacoes em fortaleza"
  - esperado: `{"project": "Copa das Confederações", "city": "Fortaleza"}`
  - predito: `{"state": "Ceará", "city": "Fortaleza", "project": "Copa das Confederações"}`
  - FP ['state'] · FN [] · fora do schema []

### valor_errado (7 casos)

- **GT040** — "cartas na escala de 100 mil publicadas nesta semana"
  - esperado: `{"scale": "1:100.000", "publicationPeriod": {"$um_de": [{"start": "2026-09-21", "end": "2026-09-24"}, {"start": "2026-09-21", "end": "2026-09-27"}]}}`
  - predito: `{"scale": "1:100.000", "publicationPeriod": {"start": "2026-09-22", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GA020** — "produtos em média escala"
  - esperado: `{"scale": {"$um_de": ["1:50.000", "1:100.000"]}}`
  - predito: `{"scale": "1:25.000"}`
  - FP ['scale'] · FN [] · fora do schema []
- **GM006** — "folha MI 2965 do distrito federal"
  - esperado: `{"keyword": "2965", "state": "Distrito Federal"}`
  - predito: `{"keyword": "2965-2-NE", "state": "Distrito Federal"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "supplyArea": "2° Centro de Geoinformação"}`
  - FP ['keyword'] · FN [] · fora do schema []

### campo_omitido (6 casos)

- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-24"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-24"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2021-01-01"}, "limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": {"$um_de": ["530", "SF-22"]}, "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-24"}]}}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - FP [] · FN ['keyword'] · fora do schema []

### nao_chamou (6 casos)

- **N21** — "qualquer coisa de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GC010** — "cartas de Goiás na escala 1:2000"
  - esperado: `{"state": "Goiás", "scale": "1:2.000"}`
  - predito: `null`
  - FP [] · FN ['scale', 'state'] · fora do schema []
- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'productType', 'sortDirection', 'sortField'] · fora do schema []
- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []

### misto (3 casos)

- **GT018** — "cartas do AP produzidas no segundo semestre do ano passado"
  - esperado: `{"state": "Amapá", "creationPeriod": {"start": "2025-07-01", "end": "2025-12-31"}}`
  - predito: `{"state": "Amapá", "publicationPeriod": {"start": "2025-07-01", "end": "2025-12-31"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
- **GT039** — "cartas na escala 1:2.000 elaboradas hoje"
  - esperado: `{"scale": "1:2.000", "creationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `{"scale": "1:2.000", "publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
- **GT021** — "cartas de roraima elaboradas hoje"
  - esperado: `{"state": "Roraima", "creationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `{"state": "Roraima", "publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
