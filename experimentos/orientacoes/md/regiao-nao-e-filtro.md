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
origem: 'lote 1, rodadas v1/v2 da T4: 68 execuções erradas com o gatilho e erro em state, city (tc1 8, se1 25, tc2 22, se2 13)'
---
Regiões (Nordeste, Sul, Amazônia Legal, litoral, semiárido, Pantanal) não são estado nem município: não viram state nem city. Se a região for o único critério, busque sem filtros ou peça esclarecimento; se houver outro critério, busque só com ele.
