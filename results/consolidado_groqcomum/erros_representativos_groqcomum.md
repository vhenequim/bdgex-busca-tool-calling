# Erros representativos (amostra aleatória por tipo, semente 42)

## GPT-OSS 20B (Groq)

### valor_errado (4 casos)

- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-18", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GA020** — "produtos em média escala"
  - esperado: `{"scale": {"$um_de": ["1:50.000", "1:100.000"]}}`
  - predito: `{"scale": "1:25.000"}`
  - FP ['scale'] · FN [] · fora do schema []
- **N23** — "produtos do trimestre passado do 4º CGEO"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-04-01", "end": "2026-06-30"}}`
  - predito: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-07-01", "end": "2026-09-30"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "supplyArea": "2° Centro de Geoinformação"}`
  - FP ['keyword'] · FN [] · fora do schema []

### campo_inventado (4 casos)

- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "state": "Rio de Janeiro", "city": "Rio de Janeiro"}`
  - FP ['city'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "amazonia legal", "productType": "SCN Carta Ortoimagem", "state": "Pará"}`
  - FP ['keyword', 'state'] · FN [] · fora do schema []
- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "state": "Rio Grande do Sul"}`
  - FP ['state'] · FN [] · fora do schema []

### campo_omitido (3 casos)

- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "limit": 10}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P22** — "MI 2901 ou SF-22 do quarto cgeo no sudeste em pequena escala criado entre 2022 e 2023 ordem cronologica"
  - esperado: `{"keyword": {"$um_de": ["2901", "SF-22"]}, "supplyArea": "4° Centro de Geoinformação", "scale": "1:250.000", "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"keyword": "2901", "supplyArea": "4° Centro de Geoinformação", "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": "creationDate", "sortDirection": "ASC"}`
  - FP [] · FN ['scale'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []

### misto (1 casos)

- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"state": "Rondônia", "city": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - FP ['city', 'state'] · FN ['keyword'] · fora do schema []

### nao_chamou (1 casos)

- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []

## GPT-OSS 120B (Groq)

### valor_errado (5 casos)

- **N22** — "ortoimagens de 2 anos atrás"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"$um_de": [{"start": "2024-01-01", "end": "2024-12-31"}, {"start": "2024-09-24", "end": "2026-09-24"}]}}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"start": "2024-09-24", "end": "2024-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GA020** — "produtos em média escala"
  - esperado: `{"scale": {"$um_de": ["1:50.000", "1:100.000"]}}`
  - predito: `{"scale": "1:25.000"}`
  - FP ['scale'] · FN [] · fora do schema []
- **N23** — "produtos do trimestre passado do 4º CGEO"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-04-01", "end": "2026-06-30"}}`
  - predito: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-06-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **P13** — "todas as cartas em escala maior que 100k do rio grande do sul"
  - esperado: `{"state": "Rio Grande do Sul", "scale": {"$um_de": ["1:25.000", "1:50.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `{"scale": "1:250.000", "state": "Rio Grande do Sul"}`
  - FP ['scale'] · FN [] · fora do schema []

### campo_omitido (4 casos)

- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-24"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-24"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2021-01-01"}, "limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": {"$um_de": ["530", "SF-22"]}, "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-24"}]}}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - FP [] · FN ['keyword'] · fora do schema []

### nao_chamou (4 casos)

- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []
- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'productType', 'sortDirection', 'sortField'] · fora do schema []
- **N21** — "qualquer coisa de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []

### campo_inventado (3 casos)

- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "city": "Brasília"}`
  - FP ['productType'] · FN [] · fora do schema []
- **P18** — "produtos da copa das confederacoes em fortaleza"
  - esperado: `{"project": "Copa das Confederações", "city": "Fortaleza"}`
  - predito: `{"state": "Ceará", "city": "Fortaleza", "project": "Copa das Confederações"}`
  - FP ['state'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "Amazônia Legal", "productType": "SCN Carta Ortoimagem"}`
  - FP ['keyword'] · FN [] · fora do schema []
