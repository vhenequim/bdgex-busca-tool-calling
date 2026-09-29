---
tipo: orientacao-pfc
status: ativa
nome: ordenacao-so-quando-pedida
titulo: Ordenação só quando pedida
campos: [sortField, sortDirection]
gatilhos:
  - 'mais recente'
  - 'mais antig'
  - '\bultim'
  - '\bprimeir'
  - 'recentes'
  - 'antigas'
  - 'ordem'
  - 'cronolog'
  - 'mais nov'
  - 'atualiza'
sempre: false
ciclo: 1
origem: 'a contar'
---
sortField e sortDirection só quando a consulta pede ordem ou posição. 'mais recente(s)', 'últimas', 'mais novas' → DESC; 'mais antiga(s)', 'primeiras', 'ordem cronológica' → ASC. sortField = creationDate se a pista for criação ou atualização ('criadas mais recentemente', 'última atualização'); senão publicationDate.
