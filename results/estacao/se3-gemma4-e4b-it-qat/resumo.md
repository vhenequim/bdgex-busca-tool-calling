# gemma4:e4b-it-qat [saida-estruturada-v3] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T03:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 84.7% |
| Precisão ponderada | 0.970 |
| Recall ponderado | 0.913 |
| F1 ponderado | 0.937 |
| F1 macro | 0.946 |
| Micro P / R / F1 | 0.966 / 0.911 / 0.938 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 1253 | 3379 | 4791 | 13084 | 19282 | 3839 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 18 | 3 | 0 | 0.857 | 1.000 | 0.923 |
| scale | 14 | 13 | 1 | 0 | 0.929 | 1.000 | 0.963 |
| productType | 14 | 12 | 0 | 2 | 1.000 | 0.857 | 0.923 |
| state | 15 | 13 | 0 | 2 | 1.000 | 0.867 | 0.929 |
| city | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 12 | 10 | 0 | 2 | 1.000 | 0.833 | 0.909 |
| creationPeriod | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 8 | 0 | 2 | 1.000 | 0.800 | 0.889 |
| sortDirection | 10 | 8 | 0 | 2 | 1.000 | 0.800 | 0.889 |
| limit | 7 | 6 | 0 | 1 | 1.000 | 0.857 | 0.923 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 90.9% | 0.939 |
| Compostas | 43 | 86.0% | 0.943 |
| Código MI/INOM | 15 | 86.7% | 0.971 |
| Tempo relativo | 15 | 86.7% | 0.973 |
| Ordenação | 10 | 80.0% | 0.906 |
| Ambíguas/informais | 35 | 80.0% | 0.925 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 90.9% |
| N | 37 | 81.1% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 3, 'nao_chamou': 5, 'misto': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 5

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
