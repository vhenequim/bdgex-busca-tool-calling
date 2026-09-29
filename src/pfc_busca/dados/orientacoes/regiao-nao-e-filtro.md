---
tipo: orientacao-pfc
status: ativa
nome: regiao-nao-e-filtro
titulo: Região não é estado nem município
campos: [state, city]
gatilhos:
  - 'nordeste'
  - 'sudeste'
  - '\bnorte\b'
  - '\bsul\b'
  - 'centro oeste'
  - 'amazonia legal'
  - 'litoral'
  - 'semiarido'
  - 'sertao'
  - 'pantanal'
  - '\bregiao\b'
  - 'fronteira'
sempre: false
ciclo: 1
origem: 'a contar'
---
Regiões (Nordeste, Sul, Amazônia Legal, litoral, semiárido, Pantanal) não são estado nem município: não viram state nem city. Se a região for o único critério, busque sem filtros ou peça esclarecimento; se houver outro critério, busque só com ele.
