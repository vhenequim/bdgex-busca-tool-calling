# qwen3:4b — resumo da avaliação

8 execuções · repetições [1] · gerado em 2026-09-14T11:22:26

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 7 |
| Acurácia por consulta | 71.4% |
| Precisão ponderada | 1.000 |
| Recall ponderado | 0.636 |
| F1 ponderado | 0.755 |
| F1 macro | 0.820 |
| Micro P / R / F1 | 1.000 / 0.636 / 0.778 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 7 | 23277 | 45226 | 38280 | 48626 | 48626 | 10388 |

Latência da ferramenta (SQL): mediana 29.1 ms, máx 45.9 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| scale | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| productType | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| state | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| city | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| supplyArea | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 3 | 1 | 0 | 2 | 1.000 | 0.333 | 0.500 |
| creationPeriod | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| sortField | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| sortDirection | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |
| limit | 0 | 0 | 0 | 0 | 0.000 | 0.000 | 0.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 2 | 100.0% | 1.000 |
| Compostas | 3 | 66.7% | 0.629 |
| Código MI/INOM | 3 | 66.7% | 0.629 |
| Tempo relativo | 3 | 33.3% | 0.300 |
| Ordenação | 0 | — | 0.000 |
| Ambíguas/informais | 4 | 75.0% | 0.800 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 3 | 66.7% |
| N | 2 | 50.0% |
| G | 2 | 100.0% |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0}
- Chamadas com erro de infraestrutura/formato: 0 {}
- Não chamou a ferramenta quando devia: 2

## Observacionais (fora das métricas principais)

1 casos · acurácia 100.0% · chamou sem dever: 0
