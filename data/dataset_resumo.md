# Dataset de avaliação — resumo

Gerado em 2026-09-14 11:30. Total: **310** consultas (297 nas métricas principais, 13 observacionais).

## Por origem

| Origem | Casos |
|---|---|
| G | 248 |
| N | 40 |
| P | 22 |

## Por família

| Família | Casos | Observacional |
|---|---|---|
| GA | 24 | 0 |
| GC | 55 | 0 |
| GF | 7 | 7 |
| GM | 28 | 0 |
| GO | 19 | 0 |
| GP | 13 | 0 |
| GS | 61 | 0 |
| GT | 41 | 0 |
| N | 40 | 6 |
| P | 22 | 0 |

## Por categoria (uma consulta pode ter várias) × origem

| Categoria | P | N | G | Total |
|---|---|---|---|---|
| S | 0 | 11 | 79 | 90 |
| C | 22 | 20 | 142 | 184 |
| M | 10 | 5 | 42 | 57 |
| T | 6 | 9 | 46 | 61 |
| O | 4 | 6 | 19 | 29 |
| A | 16 | 18 | 161 | 195 |

## Frequência de cada campo no gabarito (métricas principais)

| Campo | Ocorrências |
|---|---|
| keyword | 62 |
| scale | 83 |
| productType | 43 |
| state | 130 |
| city | 26 |
| supplyArea | 40 |
| project | 11 |
| publicationPeriod | 59 |
| creationPeriod | 3 |
| sortField | 29 |
| sortDirection | 29 |
| limit | 17 |

## Observacionais

| ID | Consulta | Motivo |
|---|---|---|
| N34 | ortos da amazonia legal | gabarito incerto: 'Amazônia Legal' abrange nove estados, não só o Amazonas |
| N36 | cartas fora do brasil | fora do domínio: nenhum parâmetro extraível |
| N37 | quero um mapa bonito | subespecífico: nenhum parâmetro extraível |
| N38 | escala 1:10.000.000 | valor fora do enum de escalas; qualquer scale emitido é falso positivo |
| N39 | cartas topo no oceano atlântico | área não terrestre: state/city emitidos são falso positivo |
| N40 | cartas do futuro (ano 2050) | gabarito determinístico; SQL válida com zero registros esperados |
| GF001 | cartas fora do brasil | nenhum parâmetro extraível (fora do domínio) |
| GF002 | me ajuda | nenhum parâmetro extraível (sem intenção clara) |
| GF003 | quero um mapa bonito | nenhum parâmetro extraível (subespecífico) |
| GF004 | escala 1:10.000.000 | escala fora do enum (erro esperado) |
| GF005 | cartas do futuro (ano 2050) | SQL válida com resultado esperado zero registros |
| GF006 | cartas de Marte | nenhum estado brasileiro; deve devolver zero ou pedir esclarecimento |
| GF007 | cartas do estado 42 | state inválido; erro de normalização detectável |
