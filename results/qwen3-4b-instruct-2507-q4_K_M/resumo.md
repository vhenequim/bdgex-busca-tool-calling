# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

14 execuções · repetições [1] · gerado em 2026-09-14T11:32:31

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 13 |
| Acurácia por consulta | 61.5% |
| Precisão ponderada | 0.744 |
| Recall ponderado | 0.875 |
| F1 ponderado | 0.779 |
| F1 macro | 0.713 |
| Micro P / R / F1 | 0.722 / 0.897 / 0.800 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 13 | 1439 | 2758 | 2993 | 4371 | 5962 | 1173 |

Latência da ferramenta (SQL): mediana 37.3 ms, máx 54.9 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| scale | 2 | 0 | 0 | 2 | 0.000 | 0.000 | 0.000 |
| productType | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 7 | 7 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| city | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| project | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 4 | 3 | 1 | 0 | 0.750 | 1.000 | 0.857 |
| creationPeriod | 1 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| sortField | 3 | 2 | 3 | 0 | 0.400 | 1.000 | 0.571 |
| sortDirection | 3 | 3 | 2 | 0 | 0.600 | 1.000 | 0.750 |
| limit | 2 | 2 | 3 | 0 | 0.400 | 1.000 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 2 | 100.0% | 1.000 |
| Compostas | 9 | 55.6% | 0.768 |
| Código MI/INOM | 4 | 100.0% | 1.000 |
| Tempo relativo | 5 | 40.0% | 0.673 |
| Ordenação | 3 | 33.3% | 0.867 |
| Ambíguas/informais | 9 | 44.4% | 0.691 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 5 | 60.0% |
| N | 3 | 66.7% |
| G | 5 | 60.0% |

## Diagnósticos

- Tipos de erro: {'misto': 3, 'valor_errado': 1, 'campo_inventado': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.995, 'creationPeriod': 0.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

1 casos · acurácia 100.0% · chamou sem dever: 0
