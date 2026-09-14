# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

14 execuções · repetições [1] · gerado em 2026-09-14T11:26:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 13 |
| Acurácia por consulta | 23.1% |
| Precisão ponderada | 0.609 |
| Recall ponderado | 0.531 |
| F1 ponderado | 0.548 |
| F1 macro | 0.564 |
| Micro P / R / F1 | 0.567 / 0.680 / 0.618 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 8 | 1707 | 2241 | 2388 | 3780 | 3780 | 620 |

Latência da ferramenta (SQL): mediana 31.0 ms, máx 32.3 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| scale | 2 | 0 | 0 | 2 | 0.000 | 0.000 | 0.000 |
| productType | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 7 | 4 | 0 | 3 | 1.000 | 0.571 | 0.727 |
| city | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| project | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 4 | 0 | 4 | 0 | 0.000 | 0.000 | 0.000 |
| creationPeriod | 1 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| sortField | 3 | 0 | 4 | 1 | 0.000 | 0.000 | 0.000 |
| sortDirection | 3 | 2 | 2 | 1 | 0.500 | 0.667 | 0.571 |
| limit | 2 | 2 | 2 | 0 | 0.500 | 1.000 | 0.667 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 2 | 0.0% | 0.000 |
| Compostas | 9 | 33.3% | 0.603 |
| Código MI/INOM | 4 | 75.0% | 0.889 |
| Tempo relativo | 5 | 0.0% | 0.444 |
| Ordenação | 3 | 0.0% | 0.582 |
| Ambíguas/informais | 9 | 22.2% | 0.483 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 5 | 40.0% |
| N | 3 | 0.0% |
| G | 5 | 20.0% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 4, 'misto': 3, 'nao_chamou': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {}
- Chamadas com erro de infraestrutura/formato: 5 {'args_invalidos': 5}
- Não chamou a ferramenta quando devia: 3

## Observacionais (fora das métricas principais)

1 casos · acurácia 100.0% · chamou sem dever: 0
