# qwen/qwen3.8-27b — resumo da avaliação

251 execuções · repetições [1] · gerado em 2026-09-26T14:50:40

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 248 |
| Acurácia por consulta | 94.8% |
| Precisão ponderada | 0.973 |
| Recall ponderado | 0.995 |
| F1 ponderado | 0.984 |
| F1 macro | 0.978 |
| Micro P / R / F1 | 0.973 / 0.995 / 0.984 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 248 | 512 | 708 | 884 | 1510 | 12717 | 880 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 62 | 1 | 0 | 0.984 | 1.000 | 0.992 |
| scale | 73 | 72 | 1 | 0 | 0.986 | 1.000 | 0.993 |
| productType | 39 | 39 | 2 | 0 | 0.951 | 1.000 | 0.975 |
| state | 98 | 97 | 2 | 0 | 0.980 | 1.000 | 0.990 |
| city | 23 | 23 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 35 | 35 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 48 | 44 | 4 | 0 | 0.917 | 1.000 | 0.957 |
| creationPeriod | 9 | 8 | 1 | 0 | 0.889 | 1.000 | 0.941 |
| sortField | 14 | 12 | 1 | 1 | 0.923 | 0.923 | 0.923 |
| sortDirection | 14 | 13 | 0 | 1 | 1.000 | 0.929 | 0.963 |
| limit | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 72 | 100.0% | 1.000 |
| Compostas | 156 | 92.3% | 0.979 |
| Código MI/INOM | 57 | 100.0% | 1.000 |
| Tempo relativo | 56 | 91.1% | 0.976 |
| Ordenação | 14 | 85.7% | 0.964 |
| Ambíguas/informais | 167 | 94.6% | 0.985 |
| Fora do domínio | 2 | 50.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 86.5% |
| G | 189 | 97.4% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 8, 'misto': 1, 'campo_inventado': 3, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.953, 'creationPeriod': 0.889}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 100.0% · chamou sem dever: 0
