# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3 4B

### misto (97 casos)

- **GO006** — "a última carta publicada de GO"
  - esperado: `{"state": "Goiás", "sortField": "publicationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `{"state": "Goiás", "publicationPeriod": {"end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GS002** — "cartas de AL"
  - esperado: `{"state": "Alagoas"}`
  - predito: `{"keyword": "AL"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"creationPeriod": {"start": "2025-07-01", "end": "2025-09-30"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 500}`
  - FP ['creationPeriod', 'limit', 'sortDirection', 'sortField'] · FN ['supplyArea'] · fora do schema []
- **GA022** — "cartas do Tocantins em 50k"
  - esperado: `{"state": "Tocantins", "scale": "1:50.000"}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Tocantins", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - FP ['productType', 'publicationPeriod'] · FN ['scale'] · fora do schema []

### campo_inventado (16 casos)

- **GC036** — "mapas de Porto Alegre na escala 1:5000"
  - esperado: `{"city": "Porto Alegre", "scale": "1:5.000"}`
  - predito: `{"keyword": "Porto Alegre", "scale": "1:50.000", "productType": "SCN Carta Topográfica Matricial", "city": "Porto Alegre"}`
  - FP ['keyword', 'productType', 'scale'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Amazonas"}`
  - FP ['state'] · FN [] · fora do schema []
- **GO003** — "as cartas mais recentes do Ceará"
  - esperado: `{"state": "Ceará", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"state": "Ceará", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rio de Janeiro"}`
  - FP ['productType'] · FN [] · fora do schema []

### nao_chamou (13 casos)

- **GA006** — "mapas do pa"
  - esperado: `{"state": "Pará"}`
  - predito: `null`
  - FP [] · FN ['state'] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []
- **GA002** — "mapas do pr"
  - esperado: `{"state": "Paraná"}`
  - predito: `null`
  - FP [] · FN ['state'] · fora do schema []
- **GO014** — "a primeira carta topográfica vetorial elaborada"
  - esperado: `{"productType": "SCN Carta Topográfica Vetorial", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['productType', 'sortDirection', 'sortField'] · fora do schema []

### valor_errado (11 casos)

- **N22** — "ortoimagens de 2 anos atrás"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"$um_de": [{"start": "2024-01-01", "end": "2024-12-31"}, {"start": "2024-09-14", "end": "2026-09-14"}]}}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"start": "2024-09-14", "end": "2024-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GT020** — "cartas da Paraíba publicadas esse ano"
  - esperado: `{"state": "Paraíba", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"state": "Paraíba", "publicationPeriod": {"start": "2026-09-14", "end": "2026-12-31"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GS020** — "produtos na escala 1:25000"
  - esperado: `{"scale": "1:25.000"}`
  - predito: `{"scale": "1:250.000"}`
  - FP ['scale'] · FN [] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": {"$um_de": ["530", "SF-22"]}, "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"keyword": "530 or SF-22", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2025-09-14", "end": "2026-09-14"}}`
  - FP ['keyword', 'publicationPeriod'] · FN [] · fora do schema []

### campo_omitido (3 casos)

- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-14"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-14"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "ASC", "limit": 5}`
  - FP [] · FN ['scale'] · fora do schema []
- **GM002** — "folha MI 2866-3 do TO"
  - esperado: `{"keyword": "2866-3", "state": "Tocantins"}`
  - predito: `{"keyword": "2866-3"}`
  - FP [] · FN ['state'] · fora do schema []
- **GC046** — "produtos do projeto olimpiadas em PE"
  - esperado: `{"project": "Olimpíadas Rio 2016", "state": "Pernambuco"}`
  - predito: `{"project": "Olimpíadas Rio 2016"}`
  - FP [] · FN ['state'] · fora do schema []

## Gemma 4 E4B

### nao_chamou (54 casos)

- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **GT015** — "cartas publicadas hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GT038** — "cartas na escala de 10 mil publicadas no mês passado"
  - esperado: `{"scale": "1:10.000", "publicationPeriod": {"start": "2026-08-01", "end": "2026-08-31"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'scale'] · fora do schema []
- **P13** — "todas as cartas em escala maior que 100k do rio grande do sul"
  - esperado: `{"state": "Rio Grande do Sul", "scale": {"$um_de": ["1:25.000", "1:50.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `null`
  - FP [] · FN ['scale', 'state'] · fora do schema []

### valor_errado (32 casos)

- **GC034** — "mapas de Cuiabá na escala 1:2000"
  - esperado: `{"city": "Cuiabá", "scale": "1:2.000"}`
  - predito: `{"scale": "1:2000", "city": "Cuiabá"}`
  - FP ['scale'] · FN [] · fora do schema []
- **GT031** — "produtos do terceiro cgeo criados nos últimos 3 meses"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "creationPeriod": {"$um_de": [{"start": "2026-06-16", "end": "2026-09-14"}, {"start": "2026-06-14", "end": "2026-09-14"}]}}`
  - predito: `{"supplyArea": "3° Centro de Geoinformação", "creationPeriod": {"start": "2026-06-14"}}`
  - FP ['creationPeriod'] · FN [] · fora do schema []
- **GC049** — "produtos do projeto copa das confederacoes no AM"
  - esperado: `{"project": "Copa das Confederações", "state": "Amazonas"}`
  - predito: `{"state": "Amapá", "project": "Copa das Confederações"}`
  - FP ['state'] · FN [] · fora do schema []
- **GT040** — "cartas na escala de 100 mil publicadas nesta semana"
  - esperado: `{"scale": "1:100.000", "publicationPeriod": {"$um_de": [{"start": "2026-09-14", "end": "2026-09-14"}, {"start": "2026-09-14", "end": "2026-09-20"}]}}`
  - predito: `{"scale": "1:100.000", "publicationPeriod": {"start": "2026-09-07", "end": "2026-09-13"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### campo_inventado (27 casos)

- **GO004** — "as cartas mais antigas de mato grosso"
  - esperado: `{"state": "Mato Grosso", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Mato Grosso", "sortField": "creationDate", "sortDirection": "ASC", "limit": 1}`
  - FP ['limit'] · FN [] · fora do schema []
- **GC018** — "cartas do Piauí em escala detalhada"
  - esperado: `{"state": "Piauí", "scale": "1:25.000"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "state": "Piauí"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GA024** — "cartas de Pernambuco em 250k"
  - esperado: `{"state": "Pernambuco", "scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000", "productType": "SCN Carta Topográfica Matricial", "state": "Pernambuco"}`
  - FP ['productType'] · FN [] · fora do schema []
- **P09** — "folha Porto Velho publicada em 2024"
  - esperado: `{"keyword": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - predito: `{"keyword": "folha", "city": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - FP ['keyword'] · FN [] · fora do schema []

### misto (7 casos)

- **GA018** — "mapas detalhados do Amazonas"
  - esperado: `{"scale": "1:25.000", "state": "Amazonas"}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Amazonas"}`
  - FP ['productType'] · FN ['scale'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá", "project": "Mapeamento Sistemático"}`
  - FP ['project'] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GM003** — "folha MI 2901 do AP"
  - esperado: `{"keyword": "2901", "state": "Amapá"}`
  - predito: `{"keyword": "2901-2-AP"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "productType": "SCN Carta Topográfica Matricial"}`
  - FP ['productType'] · FN ['state'] · fora do schema []

### campo_omitido (2 casos)

- **GO003** — "as cartas mais recentes do Ceará"
  - esperado: `{"state": "Ceará", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"state": "Ceará"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P08** — "carta topográfica Passo da Seringueira em 1:25.000"
  - esperado: `{"keyword": "Passo da Seringueira", "scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial"}`
  - predito: `{"keyword": "Passo da Seringueira", "scale": "1:25.000"}`
  - FP [] · FN ['productType'] · fora do schema []

## Gemma 4 E2B

### misto (50 casos)

- **GC010** — "cartas de Goiás na escala 1:2000"
  - esperado: `{"state": "Goiás", "scale": "1:2.000"}`
  - predito: `{"keyword": "Goiás", "scale": "1:2.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **GA023** — "cartas de Mato Grosso do Sul em 100k"
  - esperado: `{"state": "Mato Grosso do Sul", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "city": "Mato Grosso do Sul"}`
  - FP ['city'] · FN ['state'] · fora do schema []
- **GC025** — "cartas de Rondônia na escala 1:2.000"
  - esperado: `{"state": "Rondônia", "scale": "1:2.000"}`
  - predito: `{"keyword": "Rondônia", "scale": "1:2.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortDirection": "DESC"}`
  - FP ['sortDirection'] · FN ['sortField'] · fora do schema []

### valor_errado (29 casos)

- **P13** — "todas as cartas em escala maior que 100k do rio grande do sul"
  - esperado: `{"state": "Rio Grande do Sul", "scale": {"$um_de": ["1:25.000", "1:50.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `{"scale": "1:100.000", "state": "Rio Grande do Sul"}`
  - FP ['scale'] · FN [] · fora do schema []
- **GM009** — "folha MI 531-1-NE de minas"
  - esperado: `{"keyword": "531-1-NE", "state": "Minas Gerais"}`
  - predito: `{"keyword": "531-1-NE", "state": "Minas"}`
  - FP ['state'] · FN [] · fora do schema []
- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01T00:00:00", "end": "2025-12-31T23:59:59"}}`
  - FP ['creationPeriod'] · FN [] · fora do schema []
- **GM006** — "folha MI 2965 do distrito federal"
  - esperado: `{"keyword": "2965", "state": "Distrito Federal"}`
  - predito: `{"keyword": "2965-2-NE", "state": "Distrito Federal"}`
  - FP ['keyword'] · FN [] · fora do schema []

### nao_chamou (29 casos)

- **GA004** — "mapas de go"
  - esperado: `{"state": "Goiás"}`
  - predito: `null`
  - FP [] · FN ['state'] · fora do schema []
- **GS018** — "produtos na escala 1:5000"
  - esperado: `{"scale": "1:5.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []
- **GT005** — "cartas publicadas nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2026-06-16", "end": "2026-09-14"}, {"start": "2026-06-14", "end": "2026-09-14"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GS003** — "cartas do AP"
  - esperado: `{"state": "Amapá"}`
  - predito: `null`
  - FP [] · FN ['state'] · fora do schema []

### campo_omitido (14 casos)

- **GO015** — "cartas topográficas da mais nova para a mais antiga"
  - esperado: `{"productType": "SCN Carta Topográfica Matricial", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "sortDirection": "DESC"}`
  - FP [] · FN ['sortField'] · fora do schema []
- **P05** — "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano"
  - esperado: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "publicationPeriod": {"start": "2026-01-01", "end": "2026-09-14"}}`
  - FP [] · FN ['state'] · fora do schema []
- **GO008** — "as 5 publicações mais recentes de MG"
  - esperado: `{"state": "Minas Gerais", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 5}`
  - predito: `{"state": "Minas Gerais", "sortDirection": "DESC", "limit": 5}`
  - FP [] · FN ['sortField'] · fora do schema []
- **GO003** — "as cartas mais recentes do Ceará"
  - esperado: `{"state": "Ceará", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"state": "Ceará"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []

### campo_inventado (8 casos)

- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"keyword": "mapeamento detalhado", "scale": "1:25.000", "city": "Brasília"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"keyword": "rio", "scale": "1:10.000", "state": "Rio de Janeiro"}`
  - FP ['keyword', 'scale'] · FN [] · fora do schema []
- **P09** — "folha Porto Velho publicada em 2024"
  - esperado: `{"keyword": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - predito: `{"keyword": "folha", "city": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "amazonia", "productType": "SCN Carta Ortoimagem"}`
  - FP ['keyword'] · FN [] · fora do schema []

### chamou_sem_dever (3 casos)

- **GF003** — "cartas da Argentina"
  - esperado: `{}`
  - predito: `{"state": "Argentina"}`
  - FP ['state'] · FN [] · fora do schema []
- **GF006** — "mapa do tesouro pirata"
  - esperado: `{}`
  - predito: `{"keyword": "mapa do tesouro pirata"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **GF002** — "cartas de Marte"
  - esperado: `{}`
  - predito: `{"keyword": "Marte"}`
  - FP ['keyword'] · FN [] · fora do schema []

## Mistral Nemo 12B

### nao_chamou (187 casos)

- **GP006** — "todos os produtos do 1° Centro de Geoinformação"
  - esperado: `{"supplyArea": "1° Centro de Geoinformação"}`
  - predito: `null`
  - FP [] · FN ['supplyArea'] · fora do schema []
- **N02** — "produtos em escala 1:50.000"
  - esperado: `{"scale": "1:50.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []
- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-07", "end": "2026-09-13"}, {"start": "2026-09-07", "end": "2026-09-14"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'supplyArea'] · fora do schema []
- **GA007** — "mapas de goias"
  - esperado: `{"state": "Goiás"}`
  - predito: `null`
  - FP [] · FN ['state'] · fora do schema []

### campo_inventado (16 casos)

- **GC026** — "cartas de São Paulo em 50k"
  - esperado: `{"state": "São Paulo", "scale": "1:50.000"}`
  - predito: `{"scale": "1:50.000", "state": "São Paulo", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **GT024** — "cartas do Maranhão criadas nos últimos 3 meses"
  - esperado: `{"state": "Maranhão", "creationPeriod": {"$um_de": [{"start": "2026-06-16", "end": "2026-09-14"}, {"start": "2026-06-14", "end": "2026-09-14"}]}}`
  - predito: `{"state": "Maranhão", "creationPeriod": {"start": "2026-06-01", "end": "2026-08-31"}, "sortField": "creationDate", "sortDirection": "DESC"}`
  - FP ['creationPeriod', 'sortDirection', 'sortField'] · FN [] · fora do schema []
- **GS040** — "cartas de Porto Velho"
  - esperado: `{"city": "Porto Velho"}`
  - predito: `{"state": " Rondônia", "city": "Porto Velho"}`
  - FP ['state'] · FN [] · fora do schema []
- **N20** — "cartas dos últimos 5 anos em escala 100k"
  - esperado: `{"scale": "1:100.000", "publicationPeriod": {"$um_de": [{"start": "2021-09-14", "end": "2026-09-14"}, {"start": "2021-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"scale": "1:100.000", "publicationPeriod": {"start": "2021-01-01", "end": "2026-12-31"}, "sortField": "publicationDate", "sortDirection": "DESC", "limit": 5}`
  - FP ['limit', 'publicationPeriod', 'sortDirection', 'sortField'] · FN [] · fora do schema []

### valor_errado (9 casos)

- **GC012** — "cartas da paraíba na escala 1:25000"
  - esperado: `{"state": "Paraíba", "scale": "1:25.000"}`
  - predito: `{"scale": "1:250.000", "state": "Paraíba"}`
  - FP ['scale'] · FN [] · fora do schema []
- **N29** — "três produtos mais antigos deste ano"
  - esperado: `{"limit": 3, "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 3}`
  - FP ['sortDirection'] · FN [] · fora do schema []
- **GA006** — "mapas do pa"
  - esperado: `{"state": "Pará"}`
  - predito: `{"state": "São Paulo"}`
  - FP ['state'] · FN [] · fora do schema []
- **GS003** — "cartas do AP"
  - esperado: `{"state": "Amapá"}`
  - predito: `{"state": "Acre"}`
  - FP ['state'] · FN [] · fora do schema []

### campo_omitido (6 casos)

- **GM014** — "INOM SF-22-Y-D-II do tipo ortoimagem"
  - esperado: `{"keyword": "SF-22-Y-D-II", "productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "SF-22-Y-D-II"}`
  - FP [] · FN ['productType'] · fora do schema []
- **GM013** — "INOM SF-22-Y-D do tipo temática"
  - esperado: `{"keyword": "SF-22-Y-D", "productType": "Cartas Temáticas Não SCN"}`
  - predito: `{"keyword": "SF-22-Y-D"}`
  - FP [] · FN ['productType'] · fora do schema []
- **GC041** — "cartas temáticas da PB"
  - esperado: `{"productType": "Cartas Temáticas Não SCN", "state": "Paraíba"}`
  - predito: `{"state": "Paraíba"}`
  - FP [] · FN ['productType'] · fora do schema []
- **GO004** — "as cartas mais antigas de mato grosso"
  - esperado: `{"state": "Mato Grosso", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Mato Grosso"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []

### misto (6 casos)

- **GT015** — "cartas publicadas hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['publicationPeriod'] · fora do schema []
- **GS038** — "cartas de Brasília"
  - esperado: `{"city": "Brasília"}`
  - predito: `{"state": "Distrito Federal"}`
  - FP ['state'] · FN ['city'] · fora do schema []
- **GT039** — "cartas na escala 1:2.000 elaboradas hoje"
  - esperado: `{"scale": "1:2.000", "creationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"scale": "1:2.000", "sortField": "creationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['creationPeriod'] · fora do schema []
- **GT021** — "cartas de roraima elaboradas hoje"
  - esperado: `{"state": "Roraima", "creationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"state": "Roraima", "sortField": "creationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['creationPeriod'] · fora do schema []
