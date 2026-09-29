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
origem: 'a contar'
---
O campo state leva o nome da UF por extenso, com acentos: AM → Amazonas, PA → Pará, DF → Distrito Federal, ES → Espírito Santo, MS → Mato Grosso do Sul. Nunca escreva a sigla nem 'sigla + nome'.
