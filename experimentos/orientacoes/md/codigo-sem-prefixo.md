---
tipo: orientacao-pfc
status: ativa
nome: codigo-sem-prefixo
titulo: Código MI/INOM sem prefixo
campos: [keyword]
gatilhos:
  - '\bmi\b'
  - '\binom\b'
  - '\b[ns][a-h] ?\d{2}'
  - '\bfolha \d'
sempre: false
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 244 execuções erradas com o gatilho e erro em keyword (tc1 37, se1 45, tc2 118, se2 44)'
---
keyword leva só o código, como escrito: 'MI 1234-5' → '1234-5'; 'folha MI-1234-5-NO' → '1234-5-NO'; INOM em maiúsculas e com hífens: 'sb20xa' → 'SB-20-X-A'. Não acrescente nem remova sufixos e não escreva 'MI', 'INOM', 'folha' ou 'carta' dentro de keyword.
