# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3.8 27B (Groq)

### valor_errado (8 casos)

- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-07-01", "end": "2025-09-30"}}`
  - FP ['creationPeriod'] · FN [] · fora do schema []
- **P13** — "todas as cartas em escala maior que 100k do rio grande do sul"
  - esperado: `{"state": "Rio Grande do Sul", "scale": {"$um_de": ["1:25.000", "1:50.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `{"scale": "1:100.000", "state": "Rio Grande do Sul"}`
  - FP ['scale'] · FN [] · fora do schema []
- **GC049** — "produtos do projeto copa das confederacoes no AM"
  - esperado: `{"project": "Copa das Confederações", "state": "Amazonas"}`
  - predito: `{"state": "Amapá", "project": "Copa das Confederações"}`
  - FP ['state'] · FN [] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `{"state": "Pará", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['sortField'] · FN [] · fora do schema []

### campo_inventado (4 casos)

- **GC006** — "cartas de RO em 25k"
  - esperado: `{"state": "Rondônia", "scale": "1:25.000"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rondônia"}`
  - FP ['productType'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "Amazonia Legal", "productType": "SCN Carta Ortoimagem"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **GC024** — "cartas da Paraíba em 25k"
  - esperado: `{"state": "Paraíba", "scale": "1:25.000"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "state": "Paraíba"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "state": "Rio Grande do Sul"}`
  - FP ['state'] · FN [] · fora do schema []

### misto (2 casos)

- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Nordeste", "limit": 10}`
  - FP ['state'] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GA001** — "mapas de pe"
  - esperado: `{"state": "Pernambuco"}`
  - predito: `{"city": "Petrópolis"}`
  - FP ['city'] · FN ['state'] · fora do schema []

### chamou_sem_dever (1 casos)

- **N37** — "quero um mapa bonito"
  - esperado: `{}`
  - predito: `{}`
  - FP [] · FN [] · fora do schema []

## GPT-OSS 20B (Groq)

### valor_errado (13 casos)

- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-18", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N23** — "produtos do trimestre passado do 4º CGEO"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-04-01", "end": "2026-06-30"}}`
  - predito: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-07-01", "end": "2026-09-30"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GS053** — "carta MI 2965"
  - esperado: `{"keyword": "2965"}`
  - predito: `{"keyword": "2965-2-NE"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **GT033** — "produtos do 5 CGEO publicados na semana passada"
  - esperado: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-18", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### campo_omitido (11 casos)

- **GO016** — "as cartas mais recentes publicadas entre 2022 e 2023"
  - esperado: `{"publicationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"publicationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GO017** — "a primeira carta criada na semana passada"
  - esperado: `{"creationPeriod": {"$um_de": [{"start": "2026-09-17", "end": "2026-09-23"}, {"start": "2026-09-17", "end": "2026-09-24"}, {"start": "2026-09-14", "end": "2026-09-20"}]}, "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"creationPeriod": {"start": "2026-09-17", "end": "2026-09-23"}}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GO001** — "a carta mais recente do CE"
  - esperado: `{"state": "Ceará", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `{"state": "Ceará"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []

### campo_inventado (5 casos)

- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "state": "Rio Grande do Sul"}`
  - FP ['state'] · FN [] · fora do schema []
- **GO010** — "cartas do distrito federal em ordem cronológica de publicação"
  - esperado: `{"state": "Distrito Federal", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"state": "Distrito Federal", "city": "Brasília", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - FP ['city'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "state": "Rio de Janeiro", "city": "Rio de Janeiro"}`
  - FP ['city'] · FN [] · fora do schema []

### misto (2 casos)

- **GO011** — "as cartas temáticas mais recentes"
  - esperado: `{"productType": "Cartas Temáticas Não SCN", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"productType": "Cartas Temáticas Não SCN", "publicationPeriod": {"start": "2026-06-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"state": "Rondônia", "city": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - FP ['city', 'state'] · FN ['keyword'] · fora do schema []

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

- **GC033** — "mapas de Fortaleza na escala 1:10000"
  - esperado: `{"city": "Fortaleza", "scale": "1:10.000"}`
  - predito: `{"scale": "1:10.000", "state": "Ceará", "city": "Fortaleza"}`
  - FP ['state'] · FN [] · fora do schema []
- **GC031** — "mapas de Recife na escala 1:50000"
  - esperado: `{"city": "Recife", "scale": "1:50.000"}`
  - predito: `{"scale": "1:50.000", "state": "Pernambuco", "city": "Recife"}`
  - FP ['state'] · FN [] · fora do schema []
- **P18** — "produtos da copa das confederacoes em fortaleza"
  - esperado: `{"project": "Copa das Confederações", "city": "Fortaleza"}`
  - predito: `{"state": "Ceará", "city": "Fortaleza", "project": "Copa das Confederações"}`
  - FP ['state'] · FN [] · fora do schema []
- **GC035** — "mapas de Belém em 250k"
  - esperado: `{"city": "Belém", "scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "state": "Pará", "city": "Belém"}`
  - FP ['state'] · FN [] · fora do schema []

### valor_errado (7 casos)

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
- **GM006** — "folha MI 2965 do distrito federal"
  - esperado: `{"keyword": "2965", "state": "Distrito Federal"}`
  - predito: `{"keyword": "2965-2-NE", "state": "Distrito Federal"}`
  - FP ['keyword'] · FN [] · fora do schema []

### campo_omitido (6 casos)

- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": {"$um_de": ["530", "SF-22"]}, "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-24"}]}}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - FP [] · FN ['keyword'] · fora do schema []
- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-24"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-24"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2021-01-01"}, "limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []

### nao_chamou (6 casos)

- **GC021** — "cartas de SP na escala 1:2000"
  - esperado: `{"state": "São Paulo", "scale": "1:2.000"}`
  - predito: `null`
  - FP [] · FN ['scale', 'state'] · fora do schema []
- **N25** — "10 primeiras ortoimagens do Nordeste"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "limit": 10, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'productType', 'sortDirection', 'sortField'] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []
- **GA019** — "cartas em pequena escala do sul"
  - esperado: `{"scale": "1:250.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []

### misto (3 casos)

- **GT021** — "cartas de roraima elaboradas hoje"
  - esperado: `{"state": "Roraima", "creationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `{"state": "Roraima", "publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
- **GT018** — "cartas do AP produzidas no segundo semestre do ano passado"
  - esperado: `{"state": "Amapá", "creationPeriod": {"start": "2025-07-01", "end": "2025-12-31"}}`
  - predito: `{"state": "Amapá", "publicationPeriod": {"start": "2025-07-01", "end": "2025-12-31"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
- **GT039** — "cartas na escala 1:2.000 elaboradas hoje"
  - esperado: `{"scale": "1:2.000", "creationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - predito: `{"scale": "1:2.000", "publicationPeriod": {"start": "2026-09-24", "end": "2026-09-24"}}`
  - FP ['publicationPeriod'] · FN ['creationPeriod'] · fora do schema []
