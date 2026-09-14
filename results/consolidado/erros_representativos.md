# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3 4B

### misto (17 casos)

- **P10** — "carta Vale do Guaporé do projeto rondonia"
  - esperado: `{"keyword": "Vale do Guaporé", "project": "Base Cartográfica Digital de Rondônia"}`
  - predito: `{"project": "Base Cartográfica Digital de Rondônia", "publicationPeriod": {"start": "2010-01-01", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['keyword'] · fora do schema []
- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"creationPeriod": {"start": "2025-07-01", "end": "2025-09-30"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 50}`
  - FP ['creationPeriod', 'limit', 'sortDirection', 'sortField'] · FN ['supplyArea'] · fora do schema []
- **N13** — "mdt do para em 25k"
  - esperado: `{"productType": "MDT — RAM", "state": "Pará", "scale": "1:25.000"}`
  - predito: `{"productType": "MDT — RAM", "state": "Pará", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - FP ['sortDirection', 'sortField'] · FN ['scale'] · fora do schema []
- **P11** — "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala"
  - esperado: `{"keyword": "2965-2-NE", "supplyArea": "3° Centro de Geoinformação", "scale": "1:25.000"}`
  - predito: `{"keyword": "2965-2-NE", "productType": "SCN Carta Topográfica Matricial", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}}`
  - FP ['productType', 'publicationPeriod'] · FN ['scale'] · fora do schema []

### valor_errado (7 casos)

- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": "530", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - predito: `{"keyword": "530 or SF-22", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2025-09-14", "end": "2026-09-14"}}`
  - FP ['keyword', 'publicationPeriod'] · FN [] · fora do schema []
- **N35** — "sf22yd do dois cgeo"
  - esperado: `{"keyword": "SF-22-Y-D", "supplyArea": "2° Centro de Geoinformação"}`
  - predito: `{"keyword": "sf22yd", "supplyArea": "1° Centro de Geoinformação"}`
  - FP ['keyword', 'supplyArea'] · FN [] · fora do schema []
- **N29** — "três produtos mais antigos deste ano"
  - esperado: `{"limit": 3, "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}, "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "ASC", "limit": 3}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N17** — "produtos publicados nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `{"publicationPeriod": {"start": "2026-06-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### nao_chamou (6 casos)

- **N21** — "qualquer coisa de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **N19** — "atualizações deste mês"
  - esperado: `{"publicationPeriod": {"start": "2026-09-01", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['city', 'sortDirection', 'sortField'] · fora do schema []
- **N03** — "ortoimagens"
  - esperado: `{"productType": "SCN Carta Ortoimagem"}`
  - predito: `null`
  - FP [] · FN ['productType'] · fora do schema []

### campo_inventado (4 casos)

- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"scale": "1:100.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rio de Janeiro"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GO001** — "Mais recente carta de amapa"
  - esperado: `{"state": "Amapá", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"state": "Amapá", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit'] · FN [] · fora do schema []
- **N26** — "mais antigas em rondonia"
  - esperado: `{"state": "Rondônia", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "ASC", "limit": 5}`
  - FP ['limit', 'sortField'] · FN [] · fora do schema []
- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": "1:25.000", "city": "Brasília"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial", "city": "Brasília"}`
  - FP ['productType'] · FN [] · fora do schema []

## Gemma 4 E2B

### misto (2 casos)

- **P05** — "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano"
  - esperado: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "publicationPeriod": {"start": "2026-01-01", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['state'] · fora do schema []
- **P21** — "preciso das 5 cartas mais antigas do tipo ortoimg em escala detalhada do terceiro cgeo em pernambuco publicadas depois de 2020"
  - esperado: `{"limit": 5, "productType": "SCN Carta Ortoimagem", "scale": "1:25.000", "supplyArea": "3° Centro de Geoinformação", "state": "Pernambuco", "publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "creationDate", "sortDirection": "ASC"}`
  - predito: `{"scale": "1:25.000", "productType": "SCN Carta Ortoimagem", "state": "Pernambuco", "supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2020-01-01"}, "limit": 5}`
  - FP ['publicationPeriod'] · FN ['sortDirection', 'sortField'] · fora do schema []

### nao_chamou (2 casos)

- **N17** — "produtos publicados nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GT001** — "produtos publicados esse ano"
  - esperado: `{"publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []

### campo_omitido (2 casos)

- **GO001** — "Mais recente carta de amapa"
  - esperado: `{"state": "Amapá", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"state": "Amapá"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **N24** — "3 cartas mais recentes de Curitiba"
  - esperado: `{"city": "Curitiba", "limit": 3, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"city": "Curitiba", "sortDirection": "DESC", "limit": 3}`
  - FP [] · FN ['sortField'] · fora do schema []

### valor_errado (1 casos)

- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01T00:00:00Z", "end": "2025-12-31T23:59:59Z"}}`
  - FP ['creationPeriod'] · FN [] · fora do schema []

### campo_inventado (1 casos)

- **GC001** — "cartas de Rio Grande do Norte em detalhada"
  - esperado: `{"state": "Rio Grande do Norte", "scale": "1:25.000"}`
  - predito: `{"keyword": "Rio Grande do Norte", "scale": "1:25.000", "state": "Rio Grande do Norte"}`
  - FP ['keyword'] · FN [] · fora do schema []
