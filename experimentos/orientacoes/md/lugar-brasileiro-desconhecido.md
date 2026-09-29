---
tipo: orientacao-pfc
status: ativa
nome: lugar-brasileiro-desconhecido
titulo: Lugar pouco conhecido também é do acervo
campos: [city, keyword]
gatilhos_originais:
  - '\b(?:de|do|da|em|no|na)\s+[A-ZÀ-Ú][a-zà-ú]+'
sempre: false
ciclo: 2
origem: 'ciclo 1 de desenvolvimento, tc3 nas 160 consultas: 4 execuções erradas com o gatilho e erro em city, keyword (tc3 4)'
---
O acervo cobre todo o território brasileiro, inclusive municípios pequenos e nomes de folha pouco conhecidos. Um nome de lugar que você não reconhece deve ser tratado como município (city) ou nome de folha (keyword, quando vem logo depois de 'carta' ou 'folha'), conforme a posição na frase.
