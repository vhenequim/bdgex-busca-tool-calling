# Erros representativos (amostra aleatória por tipo, semente 42)

## Qwen 3 4B

### misto (93 casos)

- **GO018** — "Última carta publicada desta semana"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 1}`
  - predito: `{"publicationPeriod": {"start": "2026-09-07", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **P15** — "cartas criadas no último trimestre do ano passado do segundo cgeo"
  - esperado: `{"supplyArea": "2° Centro de Geoinformação", "creationPeriod": {"start": "2025-10-01", "end": "2025-12-31"}}`
  - predito: `{"creationPeriod": {"start": "2025-07-01", "end": "2025-09-30"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 500}`
  - FP ['creationPeriod', 'limit', 'sortDirection', 'sortField'] · FN ['supplyArea'] · fora do schema []
- **GC010** — "cartas de AL em 10k"
  - esperado: `{"state": "Alagoas", "scale": "1:10.000"}`
  - predito: `{"keyword": "AL", "scale": "1:10.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []

### campo_inventado (29 casos)

- **GS014** — "cartas de para"
  - esperado: `{"state": "Pará"}`
  - predito: `{"keyword": "para", "state": "Pará"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **GS006** — "cartas de ceara"
  - esperado: `{"state": "Ceará"}`
  - predito: `{"keyword": "CEARA", "state": "Ceará"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **GO009** — "10 mais recentes carta de RO"
  - esperado: `{"state": "Rondônia", "sortField": "creationDate", "sortDirection": "DESC", "limit": 10}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Rondônia", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 10}`
  - FP ['productType', 'sortField'] · FN [] · fora do schema []
- **GS004** — "cartas de amazonas"
  - esperado: `{"state": "Amazonas"}`
  - predito: `{"keyword": "amazonas", "state": "Amazonas"}`
  - FP ['keyword'] · FN [] · fora do schema []

### valor_errado (26 casos)

- **GT029** — "produtos do primeiro cgeo últimos 6 meses"
  - esperado: `{"supplyArea": "1° Centro de Geoinformação", "publicationPeriod": {"start": "2026-03-18", "end": "2026-09-14"}}`
  - predito: `{"supplyArea": "1° Centro de Geoinformação", "publicationPeriod": {"start": "2026-03-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GT031** — "produtos do primeiro cgeo mês passado"
  - esperado: `{"supplyArea": "1° Centro de Geoinformação", "publicationPeriod": {"start": "2026-08-01", "end": "2026-08-31"}}`
  - predito: `{"supplyArea": "1° Centro de Geoinformação", "publicationPeriod": {"start": "2026-08-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GT019** — "cartas de SP últimos 6 meses"
  - esperado: `{"state": "São Paulo", "publicationPeriod": {"start": "2026-03-18", "end": "2026-09-14"}}`
  - predito: `{"state": "São Paulo", "publicationPeriod": {"start": "2026-03-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **N17** — "produtos publicados nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `{"publicationPeriod": {"start": "2026-06-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### nao_chamou (16 casos)

- **GT017** — "cartas de gauchos de hoje"
  - esperado: `{"state": "Rio Grande do Sul", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'state'] · fora do schema []
- **P19** — "primeiro mapeamento feito em cuiaba"
  - esperado: `{"city": "Cuiabá", "sortField": "creationDate", "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['city', 'sortDirection', 'sortField'] · fora do schema []
- **GO005** — "Primeira carta de para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "ASC", "limit": 1}`
  - predito: `null`
  - FP [] · FN ['limit', 'sortDirection', 'sortField', 'state'] · fora do schema []
- **P20** — "ultima atualizacao do para"
  - esperado: `{"state": "Pará", "sortField": "creationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['sortDirection', 'sortField', 'state'] · fora do schema []

### campo_omitido (3 casos)

- **GT026** — "produtos do 5 CGEO de hoje"
  - esperado: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"supplyArea": "5° Centro de Geoinformação"}`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GO019** — "Mais recente carta publicada desde 2020"
  - esperado: `{"publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GO015** — "Primeira carta publicada últimos 5 anos"
  - esperado: `{"publicationPeriod": {"start": "2021-09-14", "end": "2026-09-14"}, "sortField": "creationDate", "sortDirection": "ASC", "limit": 1}`
  - predito: `{"publicationPeriod": {"start": "2021-09-14", "end": "2026-09-14"}}`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []

## Gemma 4 E4B

### nao_chamou (57 casos)

- **GT023** — "cartas de PI desta semana"
  - esperado: `{"state": "Piauí", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'state'] · fora do schema []
- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **GO010** — "ortoimg mais antiga"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `null`
  - FP [] · FN ['productType', 'sortDirection', 'sortField'] · fora do schema []
- **GT034** — "cartas em 25k no primeiro trimestre"
  - esperado: `{"scale": "1:25.000", "publicationPeriod": {"start": "2026-01-01", "end": "2026-03-31"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'scale'] · fora do schema []

### valor_errado (31 casos)

- **GT020** — "cartas de acre últimos 3 meses"
  - esperado: `{"state": "Acre", "publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `{"state": "Acre", "publicationPeriod": {"start": "2026-06-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GT005** — "produtos publicados últimos 3 meses"
  - esperado: `{"publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `{"publicationPeriod": {"start": "2026-06-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GM014** — "INOM SF-22-Y-D-II do tipo modelo digital de superficie"
  - esperado: `{"keyword": "SF-22-Y-D-II", "productType": "MDS — RAM"}`
  - predito: `{"keyword": "SF-22-Y-D-II", "productType": "MDT — RAM"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GS030** — "mds"
  - esperado: `{"productType": "MDS — RAM"}`
  - predito: `{"productType": "MDT — RAM"}`
  - FP ['productType'] · FN [] · fora do schema []

### campo_inventado (30 casos)

- **GC021** — "cartas de piaui em 10k"
  - esperado: `{"state": "Piauí", "scale": "1:10.000"}`
  - predito: `{"scale": "1:10.000", "productType": "SCN Carta Topográfica Matricial", "state": "Piauí"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GC025** — "cartas de Rondônia em 1:50000"
  - esperado: `{"state": "Rondônia", "scale": "1:50.000"}`
  - predito: `{"scale": "1:50.000", "productType": "SCN Carta Topográfica Matricial", "state": "Rondônia"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GC009** — "cartas de roraima em 1:2000"
  - esperado: `{"state": "Roraima", "scale": "1:2.000"}`
  - predito: `{"scale": "1:2.000", "productType": "SCN Carta Topográfica Matricial", "state": "Roraima"}`
  - FP ['productType'] · FN [] · fora do schema []
- **GO003** — "Mais recentes carta de tocantins"
  - esperado: `{"state": "Tocantins", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Tocantins", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - FP ['productType'] · FN [] · fora do schema []

### misto (27 casos)

- **P05** — "buscar folha SF-22-Y-D-II-4 do RS publicada esse ano"
  - esperado: `{"keyword": "SF-22-Y-D-II-4", "state": "Rio Grande do Sul", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - predito: `{"keyword": "SF-22-Y-D-II-4", "publicationPeriod": {"start": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN ['state'] · fora do schema []
- **GA007** — "cartas de Sao Paulo"
  - esperado: `{"state": "São Paulo"}`
  - predito: `{"city": "São Paulo"}`
  - FP ['city'] · FN ['state'] · fora do schema []
- **GA013** — "cartas de Amapa"
  - esperado: `{"state": "Amapá"}`
  - predito: `{"project": "Base Cartográfica Digital do Amapá"}`
  - FP ['project'] · FN ['state'] · fora do schema []
- **GS004** — "cartas de amazonas"
  - esperado: `{"state": "Amazonas"}`
  - predito: `{"keyword": "amazonas"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []

### campo_omitido (3 casos)

- **GO007** — "3 mais antigas carta de MS"
  - esperado: `{"state": "Mato Grosso do Sul", "sortField": "creationDate", "sortDirection": "ASC", "limit": 3}`
  - predito: `{"sortField": "creationDate", "sortDirection": "ASC", "limit": 3}`
  - FP [] · FN ['state'] · fora do schema []
- **P11** — "MI 2965-2-NE e SF-22-Y-D do terceiro cgeo em grande escala"
  - esperado: `{"keyword": "2965-2-NE", "supplyArea": "3° Centro de Geoinformação", "scale": "1:25.000"}`
  - predito: `{"keyword": "2965-2-NE", "supplyArea": "3° Centro de Geoinformação"}`
  - FP [] · FN ['scale'] · fora do schema []
- **P08** — "carta topográfica Passo da Seringueira em 1:25.000"
  - esperado: `{"keyword": "Passo da Seringueira", "scale": "1:25.000", "productType": "SCN Carta Topográfica Matricial"}`
  - predito: `{"keyword": "Passo da Seringueira", "scale": "1:25.000"}`
  - FP [] · FN ['productType'] · fora do schema []

## Gemma 4 E2B

### misto (81 casos)

- **GC023** — "cartas de minas gerais em 1:25.000"
  - esperado: `{"state": "Minas Gerais", "scale": "1:25.000"}`
  - predito: `{"keyword": "minas gerais", "scale": "1:25.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **GC005** — "cartas de minas gerais em 2k"
  - esperado: `{"state": "Minas Gerais", "scale": "1:2.000"}`
  - predito: `{"keyword": "minas gerais", "scale": "1:2.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **GC014** — "cartas de Goiás em 250k"
  - esperado: `{"state": "Goiás", "scale": "1:250.000"}`
  - predito: `{"keyword": "Goiás", "scale": "1:250.000"}`
  - FP ['keyword'] · FN ['state'] · fora do schema []
- **GC039** — "SCN Carta Ortoimagem Banda P Pol HH de paraiba"
  - esperado: `{"productType": "SCN Carta Ortoimagem Banda P Pol HH", "state": "Paraíba"}`
  - predito: `{"keyword": "SCN Carta Ortoimagem Banda P Pol HH", "state": "Paraíba"}`
  - FP ['keyword'] · FN ['productType'] · fora do schema []

### nao_chamou (38 casos)

- **N27** — "últimas 5 publicações"
  - esperado: `{"limit": 5, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **N21** — "qualquer coisa de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GT009** — "produtos publicados depois de 2022"
  - esperado: `{"publicationPeriod": {"start": "2022-01-01", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GT007** — "produtos publicados últimos 5 anos"
  - esperado: `{"publicationPeriod": {"start": "2021-09-14", "end": "2026-09-14"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod'] · fora do schema []

### valor_errado (22 casos)

- **GT016** — "cartas de Bahia antes de 2020"
  - esperado: `{"state": "Bahia", "publicationPeriod": {"end": "2019-12-31"}}`
  - predito: `{"state": "Bahia", "publicationPeriod": {"end": "2020-01-01"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []
- **GO010** — "ortoimg mais antiga"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"productType": "SCN Carta Ortoimagem", "sortField": "creationDate", "sortDirection": "DESC"}`
  - FP ['sortDirection', 'sortField'] · FN [] · fora do schema []
- **GM013** — "INOM SF-22-Y-D do tipo MDS"
  - esperado: `{"keyword": "SF-22-Y-D", "productType": "MDS — RAM"}`
  - predito: `{"keyword": "SF-22-Y-D", "productType": "MDT — RAM"}`
  - FP ['productType'] · FN [] · fora do schema []
- **P12** — "cartas do tipo topo com MI 530 ou SF-22 publicadas esse ano"
  - esperado: `{"keyword": "530", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}}`
  - predito: `{"keyword": "530", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### campo_inventado (9 casos)

- **GT035** — "cartas em 1:2.000 últimos 6 meses"
  - esperado: `{"scale": "1:2.000", "publicationPeriod": {"start": "2026-03-18", "end": "2026-09-14"}}`
  - predito: `{"keyword": "1:2.000", "scale": "1:2.000", "productType": "SCN Carta Topográfica Matricial", "publicationPeriod": {"start": "2026-03-14", "end": "2026-09-14"}}`
  - FP ['keyword', 'productType', 'publicationPeriod'] · FN [] · fora do schema []
- **P14** — "mapeamento detalhado (25k ou 50k) de brasilia"
  - esperado: `{"scale": "1:25.000", "city": "Brasília"}`
  - predito: `{"keyword": "mapeamento detalhado", "scale": "1:25.000", "city": "Brasília"}`
  - FP ['keyword'] · FN [] · fora do schema []
- **N32** — "mapas do rio em cem k"
  - esperado: `{"state": "Rio de Janeiro", "scale": "1:100.000"}`
  - predito: `{"keyword": "rio", "scale": "1:10.000", "state": "Rio de Janeiro"}`
  - FP ['keyword', 'scale'] · FN [] · fora do schema []
- **P09** — "folha Porto Velho publicada em 2024"
  - esperado: `{"keyword": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - predito: `{"keyword": "folha", "city": "Porto Velho", "publicationPeriod": {"start": "2024-01-01", "end": "2024-12-31"}}`
  - FP ['city', 'keyword'] · FN [] · fora do schema []

### campo_omitido (7 casos)

- **GO004** — "Mais antigas carta de rio de janeiro"
  - esperado: `{"state": "Rio de Janeiro", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"state": "Rio de Janeiro"}`
  - FP [] · FN ['sortDirection', 'sortField'] · fora do schema []
- **GT026** — "produtos do 5 CGEO de hoje"
  - esperado: `{"supplyArea": "5° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"supplyArea": "5° Centro de Geoinformação"}`
  - FP [] · FN ['publicationPeriod'] · fora do schema []
- **GO013** — "orto primeira"
  - esperado: `{"productType": "SCN Carta Ortoimagem", "sortField": "creationDate", "sortDirection": "ASC", "limit": 1}`
  - predito: `{"productType": "SCN Carta Ortoimagem"}`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **GO006** — "Última carta de alagoas"
  - esperado: `{"state": "Alagoas", "sortField": "creationDate", "sortDirection": "DESC", "limit": 1}`
  - predito: `{"state": "Alagoas"}`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []

## Mistral Nemo 12B

### nao_chamou (167 casos)

- **GO019** — "Mais recente carta publicada desde 2020"
  - esperado: `{"publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'sortDirection', 'sortField'] · fora do schema []
- **GS024** — "topo"
  - esperado: `{"productType": "SCN Carta Topográfica Matricial"}`
  - predito: `null`
  - FP [] · FN ['productType'] · fora do schema []
- **N02** — "produtos em escala 1:50.000"
  - esperado: `{"scale": "1:50.000"}`
  - predito: `null`
  - FP [] · FN ['scale'] · fora do schema []
- **P16** — "produtos da semana passada do terceiro cgeo"
  - esperado: `{"supplyArea": "3° Centro de Geoinformação", "publicationPeriod": {"start": "2026-09-07", "end": "2026-09-13"}}`
  - predito: `null`
  - FP [] · FN ['publicationPeriod', 'supplyArea'] · fora do schema []

### campo_inventado (26 casos)

- **GO001** — "Mais recente carta de amapa"
  - esperado: `{"state": "Amapá", "sortField": "publicationDate", "sortDirection": "DESC"}`
  - predito: `{"state": "Amapá", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit'] · FN [] · fora do schema []
- **GC012** — "cartas de AP em 10k"
  - esperado: `{"state": "Amapá", "scale": "1:10.000"}`
  - predito: `{"scale": "1:10.000", "productType": "SCN Carta Topográfica Matricial", "state": "Acre"}`
  - FP ['productType', 'state'] · FN [] · fora do schema []
- **GA022** — "cartas do Distrito Federal em 50k"
  - esperado: `{"state": "Distrito Federal", "scale": "1:50.000"}`
  - predito: `{"scale": "1:50.000", "state": "Distrito Federal", "limit": 5}`
  - FP ['limit'] · FN [] · fora do schema []
- **GT008** — "produtos publicados desde 2020"
  - esperado: `{"publicationPeriod": {"start": "2020-01-01", "end": "2026-09-14"}}`
  - predito: `{"publicationPeriod": {"start": "2020-01-01"}, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - FP ['publicationPeriod', 'sortDirection', 'sortField'] · FN [] · fora do schema []

### valor_errado (17 casos)

- **N29** — "três produtos mais antigos deste ano"
  - esperado: `{"limit": 3, "publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}, "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"publicationPeriod": {"start": "2026-01-01", "end": "2026-12-31"}, "sortField": "creationDate", "sortDirection": "DESC", "limit": 3}`
  - FP ['sortDirection', 'sortField'] · FN [] · fora do schema []
- **GC054** — "cartas do 4o CGEO em 2k"
  - esperado: `{"supplyArea": "4° Centro de Geoinformação", "scale": "1:2.000"}`
  - predito: `{"scale": "1:25.000", "supplyArea": "4° Centro de Geoinformação"}`
  - FP ['scale'] · FN [] · fora do schema []
- **GO004** — "Mais antigas carta de rio de janeiro"
  - esperado: `{"state": "Rio de Janeiro", "sortField": "publicationDate", "sortDirection": "ASC"}`
  - predito: `{"state": "Rio de Janeiro", "sortField": "creationDate", "sortDirection": "ASC"}`
  - FP ['sortField'] · FN [] · fora do schema []
- **N17** — "produtos publicados nos últimos 3 meses"
  - esperado: `{"publicationPeriod": {"start": "2026-06-16", "end": "2026-09-14"}}`
  - predito: `{"publicationPeriod": {"start": "2026-06-14", "end": "2026-09-14"}}`
  - FP ['publicationPeriod'] · FN [] · fora do schema []

### misto (13 casos)

- **GT017** — "cartas de gauchos de hoje"
  - esperado: `{"state": "Rio Grande do Sul", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"productType": "SCN Carta Topográfica Matricial", "state": "Rio Grande do Sul", "sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit', 'productType', 'sortDirection', 'sortField'] · FN ['publicationPeriod'] · fora do schema []
- **GS040** — "cartas de Brasília"
  - esperado: `{"city": "Brasília"}`
  - predito: `{"state": "Distrito Federal"}`
  - FP ['state'] · FN ['city'] · fora do schema []
- **GT023** — "cartas de PI desta semana"
  - esperado: `{"state": "Piauí", "publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"project": "Olimpíadas Rio 2016", "publicationPeriod": {"start": "2026-09-11", "end": "2026-09-17"}, "sortField": "publicationDate", "sortDirection": "DESC"}`
  - FP ['project', 'publicationPeriod', 'sortDirection', 'sortField'] · FN ['state'] · fora do schema []
- **GT015** — "produtos publicados de hoje"
  - esperado: `{"publicationPeriod": {"start": "2026-09-14", "end": "2026-09-14"}}`
  - predito: `{"sortField": "publicationDate", "sortDirection": "DESC", "limit": 1}`
  - FP ['limit', 'sortDirection', 'sortField'] · FN ['publicationPeriod'] · fora do schema []

### campo_omitido (4 casos)

- **GM014** — "INOM SF-22-Y-D-II do tipo modelo digital de superficie"
  - esperado: `{"keyword": "SF-22-Y-D-II", "productType": "MDS — RAM"}`
  - predito: `{"keyword": "SF-22-Y-D-II"}`
  - FP [] · FN ['productType'] · fora do schema []
- **GO006** — "Última carta de alagoas"
  - esperado: `{"state": "Alagoas", "sortField": "creationDate", "sortDirection": "DESC", "limit": 1}`
  - predito: `{"state": "Alagoas"}`
  - FP [] · FN ['limit', 'sortDirection', 'sortField'] · fora do schema []
- **GM022** — "INOM SF-24-Y-A do tipo temática"
  - esperado: `{"keyword": "SF-24-Y-A", "productType": "Cartas Temáticas Não SCN"}`
  - predito: `{"keyword": "SF-24-Y-A"}`
  - FP [] · FN ['productType'] · fora do schema []
- **P04** — "carta 530 em pequena escala"
  - esperado: `{"keyword": "530", "scale": "1:250.000"}`
  - predito: `{"scale": "1:250.000"}`
  - FP [] · FN ['keyword'] · fora do schema []
