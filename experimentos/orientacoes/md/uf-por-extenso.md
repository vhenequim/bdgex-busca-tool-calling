---
tipo: orientacao-pfc
status: ativa
nome: uf-por-extenso
titulo: Estado sempre por extenso
campos: [state]
gatilhos:
  - '\bestado\b'
gatilhos_originais:
  - '\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b'
sempre: false
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 257 execuções erradas com o gatilho e erro em state (tc1 64, se1 39, tc2 89, se2 65)'
---
O campo state leva o nome da UF por extenso, com acentos: AM → Amazonas, PA → Pará, DF → Distrito Federal, ES → Espírito Santo, MS → Mato Grosso do Sul. Nunca escreva a sigla nem 'sigla + nome'.
