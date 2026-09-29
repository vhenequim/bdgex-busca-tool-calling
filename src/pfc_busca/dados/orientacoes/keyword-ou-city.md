---
tipo: orientacao-pfc
status: ativa
nome: keyword-ou-city
titulo: Nome de carta × município
campos: [keyword, city]
gatilhos:
  - '\b(?:carta|folha) (?!(?:de|do|da|dos|das|em|na|no|mi|inom|topo\w*|vetor\w*|orto\w*|tematic\w*|mais|circ|mdt|mds|com|que|para|pra)\b)[a-z]'
sempre: false
ciclo: 1
origem: 'a contar'
---
Nome logo depois de 'carta' ou 'folha' ('carta Rio das Pedras', 'folha Serra Azul') é keyword, copiado como está escrito. 'cartas de X', com X município, é city. Não use keyword para palavras genéricas ('carta', 'folha') nem para o tipo de produto.
