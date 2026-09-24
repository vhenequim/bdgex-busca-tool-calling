# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3 4B

### misto (15 casos)

- **N20** — "cartas dos últimos 5 anos em escala 100k"
  - esperado: `{"scale": "1:100.000", "publicationPeriod": {"$um_de": [{"start": "2021-09-14", "end": "2026-09-14"}, {"start": "2021-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"publicationPeriod": {"start": "2021-09-14", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "DESC", "limit": 500}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['scale'] · fora do schema []
- **P11** — "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala"
  - esperado: `{"keyword": {"$um_de": ["2965-2-NE", "SF-22-Y-D"]}, "supplyArea": "3° Centro de Geoinformação", "scale": {"$um_de": ["1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `{"keyword": "2965-2-NE", "productType": "SCN Carta Topográfica Matricial", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}}`
  - FP ['productType', 'publicationPeriod'] · FN ['scale'] · fora do schema []
- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"project": "Base Cartográfica Digital de Rondônia", "publicationPeriod": {"start": "2010-01-01", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['keyword'] · fora do schema []
- **N22** — "ortoimagens de 2 anos atrás"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"$um_de": [{"start": "2024-01-01", "end": "2024-12-31"}, {"start": "2024-09-14", "end": "2026-09-14"}]}}`
  - predito: `{"publicationPeriod": {"start": "2024-09-14", "end": "2024-09-14"}}`
  - FP ['publicationPeriod'] · FN ['productType'] · fora do schema []

### nao_chamou (6 casos)

- **N03** — "ortoimagens"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `null`
  - FP [] · FN ['productType'] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []
- **N19** — "atualizações deste mês"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2026-09-01", "end": "2026-09-14"}, {"start": "2026-09-01", "end": "2026-09-30"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['city', 'sortDirection', 'sortField'] · fora do schema []

### valor_errado (4 casos)

- **P05** — "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano"
  - esperado: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"start": "2026-09-14", "end": "2026-12-31"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N29** — "três produtos mais antigos deste ano"
  - esperado: `{"limit": 3, "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}, "sortField": "creationDate", "sortDirection": "ASC", "limit": 3}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "sf22yd", "supplyArea": "1° Centro de Geoinformação"}`
  - FP ['keyword', 'supplyArea'] · FN [] · fora do schema []
- **N23** — "produtos do trimestre passado do 4º CGEO"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-04-01", "end": "2026-06-30"}}`
  - predito: `{"supplyArea": "4° Centro de Geoinformação", "publicationPeriod": {"start": "2026-06-01", "end": "2026-08-31"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### campo_inventado (4 casos)

- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "city": "Brasília"}`
  - FP ['productType'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Amazonas"}`
  - FP ['state'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rio de Janeiro"}`
  - FP ['productType'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit', 'productType'] · FN [] · fora do schema []

### campo_omitido (1 casos)

- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-14"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-14"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "ASC", "limit": 5}`
  - FP [] · FN ['scale'] · fora do schema []

## Gemma 4 E2B

### valor_errado (9 casos)

- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "supplyArea": "2° Centro de Geoinformação"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **P11** — "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala"
  - esperado: `{"keyword": {"$um_de": ["2965-2-NE", "SF-22-Y-D"]}, "supplyArea": "3° Centro de Geoinformação", "scale": {"$um_de": ["1:25.000", "1:10.000", "1:5.000", "1:2.000", "1:1.000"]}}`
  - predito: `{"keyword": "2965-2-NE, SF-22-Y-D", "scale": "1:1.000", "supplyArea": "3° Centro de Geoinformação"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"$um_de": [{"start": "2026-09-07", "end": "2026-09-13"}, {"start": "2026-09-07", "end": "2026-09-14"}]}}`
  - predito: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-07T00:00:00Z"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": {"$um_de": ["530", "SF-22"]}, "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"keyword": "530", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### nao_chamou (8 casos)

- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **N02** — "produtos em escala 1:50.000"
  - esperado: `{"scale": "1:50.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []
- **N17** — "produtos publicados nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2026-06-16", "end": "2026-09-14"}, {"start": "2026-06-14", "end": "2026-09-14"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **N19** — "atualizações deste mês"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2026-09-01", "end": "2026-09-14"}, {"start": "2026-09-01", "end": "2026-09-30"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []

### misto (7 casos)

- **P22** — "MI 2901 ou SF-22 do quarto cgeo no sudeste em pequena escala criado entre 2022 e 2023 ordem cronologica"
  - esperado: `{"keyword": {"$um_de": ["2901", "SF-22"]}, "supplyArea": "4° Centro de Geoinformação", "scale": "1:250.000", "creationPeriod": {"start": "2022-01-01", "end": "2023-12-31"}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"keyword": "2901", "state": "Sudeste", "supplyArea": "4° Centro de Geoinformação", "sortField": "creationDate", "sortDirection": "ASC"}`
  - FP ['state'] · FN ['creationPeriod', 'scale'] · fora do schema []
- **P17** — "cartas do mapeamento sistematico em goias"
  - esperado: `{"project": "Mapeamento Sistemático", "state": "Goiás"}`
  - predito: `{"keyword": "Mapeamento Sistematico", "state": "Goiás"}`
  - FP ['keyword'] · FN ['project'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `{"city": "Cuiabá", "project": "Mapeamento Sistemático"}`
  - FP ['project'] · FN ['sortDirection', 'sortField'] · fora do schema []
- **N11** — "cartas do 1º CGEO em Minas Gerais"
  - esperado: `{"supplyArea": "1° Centro de Geoinformação", "state": "Minas Gerais"}`
  - predito: `{"city": "Minas Gerais", "supplyArea": "1° Centro de Geoinformação"}`
  - FP ['city'] · FN ['state'] · fora do schema []

### campo_omitido (4 casos)

- **N24** — "3 cartas mais recentes de Curitiba"
  - esperado: `{"city": "Curitiba", "limit": 3, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC"}`
  - predito: `{"city": "Curitiba", "sortDirection": "DESC", "limit": 3}`
  - FP [] · FN ['sortField'] · fora do schema []
- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-14"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-14"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01"}, "limit": 5}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **P05** — "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano"
  - esperado: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "publicationPeriod": {"start": "2026-01-01", "end": "2026-09-14"}}`
  - FP [] · FN ['state'] · fora do schema []
- **N28** — "carta MI 2901 mais recente"
  - esperado: `{"keyword": "2901", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "DESC", "limit": {"$opcional": 1}}`
  - predito: `{"keyword": "2901", "sortDirection": "DESC"}`
  - FP [] · FN ['sortField'] · fora do schema []

### campo_inventado (3 casos)

- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"keyword": "rio", "scale": "1:10.000", "state": "Rio de Janeiro"}`
  - FP ['keyword', 'scale'] · FN [] · fora do schema []
- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"keyword": "mapeamento detalhado", "scale": "1:25.000", "city": "Brasília"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"keyword": "amazonia", "productType": "SCN Carta Ortoimagem"}`
  - FP ['keyword'] · FN [] · fora do schema []
