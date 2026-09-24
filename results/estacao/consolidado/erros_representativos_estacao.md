# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3 4B

### misto (14 casos)

- **N20** — "cartas dos últimos 5 anos em escala 100k"
  - esperado: `{"scale": "1:100.000", "publicationPeriod": {"$um_de": [{"start": "2021-09-14", "end": "2026-09-14"}, {"start": "2021-01-01", "end": "2026-09-14"}]}}`
  - predito: `{"publicationPeriod": {"start": "2021-09-14", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "DESC", "limit": 500}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['scale'] · fora do schema []
- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"project": "Base Cartográfica Digital de Rondônia", "publicationPeriod": {"start": "2010-01-01", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['keyword'] · fora do schema []
- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"creationPeriod": {"start": "2025-07-01", "end": "2025-09-30"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 50}`
  - FP ['creationPeriod', 'limit', 'sortDirection', 'sortField'] · FN ['supplyArea'] · fora do schema []
- **P17** — "cartas do mapeamento sistematico em goias"
  - esperado: `{"project": "Mapeamento Sistemático", "state": "Goiás"}`
  - predito: `{"project": "Mapeamento Sistemático", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 10}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['state'] · fora do schema []

### valor_errado (6 casos)

- **N14** — "folha 2965-2 do Rio Grande do Sul"
  - esperado: `{"keyword": "2965-2", "state": "Rio Grande do Sul"}`
  - predito: `{"keyword": "2965-2-NE", "state": "Rio Grande do Sul"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "sf22yd", "supplyArea": "1° Centro de Geoinformação"}`
  - FP ['keyword', 'supplyArea'] · FN [] · fora do schema []
- **N29** — "três produtos mais antigos deste ano"
  - esperado: `{"limit": 3, "publicationPeriod": {"$um_de": [{"start": "2026-01-01", "end": "2026-12-31"}, {"start": "2026-01-01", "end": "2026-09-14"}]}, "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "ASC", "limit": 3}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N22** — "ortoimagens de 2 anos atrás"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"$um_de": [{"start": "2024-01-01", "end": "2024-12-31"}, {"start": "2024-09-14", "end": "2026-09-14"}]}}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "publicationPeriod": {"start": "2024-09-14", "end": "2024-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### nao_chamou (6 casos)

- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC", "limit": {"$opcional": 1}}`
  - predito: `null`
  - FP [] · FN ['city', 'sortDirection', 'sortField'] · fora do schema []
- **N19** — "atualizações deste mês"
  - esperado: `{"publicationPeriod": {"$um_de": [{"start": "2026-09-01", "end": "2026-09-14"}, {"start": "2026-09-01", "end": "2026-09-30"}]}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **N21** — "qualquer coisa de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **N03** — "ortoimagens"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `null`
  - FP [] · FN ['productType'] · fora do schema []

### campo_inventado (4 casos)

- **N34** — "ortos da amazonia legal"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Amazonas"}`
  - FP ['state'] · FN [] · fora do schema []
- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": {"$um_de": ["1:25.000", "1:50.000"]}, "city": "Brasília"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "city": "Brasília"}`
  - FP ['productType'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rio de Janeiro"}`
  - FP ['productType'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": {"$um_de": ["publicationDate", "creationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []

### campo_omitido (1 casos)

- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"$um_de": [{"start": "2020-01-01", "end": "2026-09-14"}, {"start": "2020-01-01"}, {"start": "2021-01-01", "end": "2026-09-14"}, {"start": "2021-01-01"}]}, "sortField": {"$um_de": ["creationDate", "publicationDate"]}, "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "ASC", "limit": 5}`
  - FP [] · FN ['scale'] · fora do schema []
