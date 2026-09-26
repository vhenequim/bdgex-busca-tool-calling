# qwen/qwen3.8-27b — resumo da avaliação

199 execuções · repetições [1] · gerado em 2026-09-26T14:38:56

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 196 |
| Acurácia por consulta | 94.4% |
| Precisão ponderada | 0.971 |
| Recall ponderado | 0.994 |
| F1 ponderado | 0.981 |
| F1 macro | 0.948 |
| Micro P / R / F1 | 0.971 / 0.994 / 0.982 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 196 | 512 | 697 | 916 | 1618 | 12717 | 986 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 55 | 55 | 1 | 0 | 0.982 | 1.000 | 0.991 |
| scale | 65 | 64 | 1 | 0 | 0.985 | 1.000 | 0.992 |
| productType | 38 | 38 | 2 | 0 | 0.950 | 1.000 | 0.974 |
| state | 84 | 83 | 2 | 0 | 0.976 | 1.000 | 0.988 |
| city | 23 | 23 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 21 | 21 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 14 | 12 | 2 | 0 | 0.857 | 1.000 | 0.923 |
| creationPeriod | 2 | 1 | 1 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 10 | 8 | 1 | 1 | 0.889 | 0.889 | 0.889 |
| sortDirection | 10 | 9 | 0 | 1 | 1.000 | 0.900 | 0.947 |
| limit | 8 | 8 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 72 | 100.0% | 1.000 |
| Compostas | 119 | 91.6% | 0.976 |
| Código MI/INOM | 50 | 100.0% | 1.000 |
| Tempo relativo | 15 | 80.0% | 0.957 |
| Ordenação | 10 | 80.0% | 0.953 |
| Ambíguas/informais | 136 | 93.4% | 0.979 |
| Fora do domínio | 2 | 50.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 86.5% |
| G | 137 | 97.8% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 6, 'misto': 1, 'campo_inventado': 3, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.861, 'creationPeriod': 0.5}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 100.0% · chamou sem dever: 0
