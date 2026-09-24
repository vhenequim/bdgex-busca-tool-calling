# qwen/qwen3.8-27b — resumo da avaliação

120 execuções · repetições [1] · gerado em 2026-09-24T10:52:13

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 117 |
| Acurácia por consulta | 93.2% |
| Precisão ponderada | 0.962 |
| Recall ponderado | 0.989 |
| F1 ponderado | 0.974 |
| F1 macro | 0.948 |
| Micro P / R / F1 | 0.962 / 0.989 / 0.975 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 117 | 512 | 708 | 898 | 1618 | 4693 | 591 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 31 | 31 | 1 | 0 | 0.969 | 1.000 | 0.984 |
| scale | 22 | 21 | 1 | 0 | 0.955 | 1.000 | 0.977 |
| productType | 23 | 23 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 30 | 30 | 1 | 0 | 0.968 | 1.000 | 0.984 |
| city | 15 | 15 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 16 | 16 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 14 | 12 | 2 | 0 | 0.857 | 1.000 | 0.923 |
| creationPeriod | 2 | 1 | 1 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 10 | 8 | 1 | 1 | 0.889 | 0.889 | 0.889 |
| sortDirection | 10 | 9 | 0 | 1 | 1.000 | 0.900 | 0.947 |
| limit | 8 | 8 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 69 | 100.0% | 1.000 |
| Compostas | 43 | 83.7% | 0.957 |
| Código MI/INOM | 26 | 100.0% | 1.000 |
| Tempo relativo | 15 | 80.0% | 0.957 |
| Ordenação | 10 | 80.0% | 0.953 |
| Ambíguas/informais | 66 | 90.9% | 0.965 |
| Fora do domínio | 2 | 50.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 86.5% |
| G | 58 | 100.0% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 5, 'misto': 1, 'campo_inventado': 1, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.861, 'creationPeriod': 0.5}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 100.0% · chamou sem dever: 0
