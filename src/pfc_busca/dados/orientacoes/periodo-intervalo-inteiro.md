---
tipo: orientacao-pfc
status: ativa
nome: periodo-intervalo-inteiro
titulo: Período como intervalo completo
campos: [publicationPeriod, creationPeriod]
gatilhos:
  - '\b(?:19|20)\d{2}\b'
  - '\bano\b'
  - '\bmes\b'
  - '\bsemana\b'
  - '\bhoje\b'
  - 'trimestre'
  - 'semestre'
  - '\bultimos\b'
  - '\bdesde\b'
  - '\bdepois\b'
  - '\bantes\b'
  - '\bapos\b'
sempre: false
ciclo: 1
origem: 'a contar'
---
Período é um intervalo completo resolvido com a data atual: 'este ano' → de 1º de janeiro a 31 de dezembro; 'no ano passado' → o ano anterior inteiro; 'últimos 6 meses' → de 6 meses atrás até hoje; 'desde 2015' → start 2015-01-01 e end hoje; 'em 2008' → 2008-01-01 a 2008-12-31; 'antes de 2010' → só end, 2009-12-31. Verbo de publicação (publicada, lançada) ou nenhum verbo → publicationPeriod; criada, feita, elaborada, produzida → creationPeriod.
