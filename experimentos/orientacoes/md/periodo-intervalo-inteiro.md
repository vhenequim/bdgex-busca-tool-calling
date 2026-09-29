---
tipo: orientacao-pfc
status: ativa
nome: periodo-intervalo-inteiro
titulo: Período como intervalo completo, num campo só
campos: [publicationPeriod, creationPeriod]
gatilhos:
  - '\b(?:19|20)\d{2}\b'
  - '\bano\b'
  - '\banos\b'
  - '\bmes\b'
  - '\bmeses\b'
  - '\bsemana\b'
  - '\bdias?\b'
  - '\bhoje\b'
  - 'trimestre'
  - 'semestre'
  - '\bultim[oa]s?\b'
  - '\batras\b'
  - '\bpassad[oa]\b'
  - '\bdesde\b'
  - '\bdepois\b'
  - '\bantes\b'
  - '\bapos\b'
sempre: false
ciclo: 1
revisoes:
  - 'ciclo 2: exemplos com data fictícia (os erros do ciclo 1 foram de aritmética), gatilhos para atrás/passado/último, e um campo só'
origem: 'lote 1, rodadas v1/v2 da T4: 427 execuções erradas com o gatilho e erro em publicationPeriod, creationPeriod (tc1 195, se1 77, tc2 77, se2 78)'
---
Período é um intervalo completo resolvido com a data atual. Exemplo, se hoje fosse 2025-03-10: 'últimos 3 anos' → 2022-03-10 a 2025-03-10; 'últimos 2 meses' → 2025-01-09 a 2025-03-10; 'dois anos atrás' → 2023-01-01 a 2023-12-31; 'no ano passado' → 2024-01-01 a 2024-12-31; 'este ano' → 2025-01-01 a 2025-12-31; 'este mês' → 2025-03-01 a 2025-03-10; 'desde 2015' ou 'depois de 2015' → start 2015-01-01 e end hoje; 'em 2008' → 2008-01-01 a 2008-12-31; 'antes de 2010' → só end, 2009-12-31. O verbo decide o campo, e só um dos dois recebe o período: criada, feita, elaborada, produzida → creationPeriod; publicada, lançada ou nenhum verbo → publicationPeriod.
