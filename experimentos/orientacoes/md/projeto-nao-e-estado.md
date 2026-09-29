---
tipo: orientacao-pfc
status: ativa
nome: projeto-nao-e-estado
titulo: Nome de projeto não é estado
campos: [project, state]
gatilhos:
  - '\bbcd\b'
  - 'base cartografica digital'
sempre: false
ciclo: 1
origem: 'lote 1, rodadas v1/v2 da T4: 30 execuções erradas com o gatilho e erro em project, state (tc1 12, se1 4, tc2 5, se2 9)'
---
'BCD da Bahia', 'Base Cartográfica Digital de Rondônia' e 'BCD do Amapá' são projetos: preencha project, e não state (o estado faz parte do nome do projeto).
