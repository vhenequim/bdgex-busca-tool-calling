# gemma4:e4b-it-qat — resumo da avaliação

160 execuções · repetições [1] · gerado em 2026-09-29T10:39:42

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 160 |
| Acurácia por consulta | 96.9% |
| Precisão ponderada | 0.984 |
| Recall ponderado | 1.000 |
| F1 ponderado | 0.992 |
| F1 macro | 0.989 |
| Micro P / R / F1 | 0.983 / 1.000 / 0.991 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 160 | 1187 | 7624 | 9579 | 19880 | 69205 | 8418 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 49 | 49 | 1 | 0 | 0.980 | 1.000 | 0.990 |
| scale | 37 | 37 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 34 | 34 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 30 | 30 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| city | 19 | 19 | 2 | 0 | 0.905 | 1.000 | 0.950 |
| supplyArea | 31 | 31 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 17 | 16 | 1 | 0 | 0.941 | 1.000 | 0.970 |
| creationPeriod | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| limit | 11 | 11 | 1 | 0 | 0.917 | 1.000 | 0.957 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 33 | 100.0% | 1.000 |
| Compostas | 93 | 95.7% | 0.992 |
| Código MI/INOM | 30 | 96.7% | 0.995 |
| Tempo relativo | 27 | 96.3% | 0.991 |
| Ordenação | 20 | 95.0% | 0.994 |
| Ambíguas/informais | 87 | 95.4% | 0.990 |
| Fora do domínio | 15 | 100.0% | 0.000 |
| Subespecificadas | 10 | 90.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 4, 'valor_errado': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.938, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
