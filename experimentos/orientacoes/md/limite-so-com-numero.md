---
tipo: orientacao-pfc
status: ativa
nome: limite-so-com-numero
titulo: limit só com número ou pedido no singular
campos: [limit]
gatilhos:
  - 'mais recente'
  - 'mais antig'
  - '\bultim'
  - '\bprimeir'
  - 'recentes'
  - 'antigas'
  - 'atualiza'
sempre: false
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 125 execuções erradas com o gatilho e erro em limit (tc1 35, se1 8, tc2 59, se2 23)'
---
limit só entra quando a consulta diz quantos resultados quer ('as 5 mais antigas' → 5; 'três cartas' → 3) ou pede UM resultado no singular ('a carta mais recente' → 1). Plural sem número ('as mais recentes', 'as últimas cartas', 'as edições mais novas') → não preencha limit.
