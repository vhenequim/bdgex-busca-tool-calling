# gemma4:e4b-it-qat — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T00:14:03

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 52.5% |
| Precisão ponderada | 0.859 |
| Recall ponderado | 0.638 |
| F1 ponderado | 0.702 |
| F1 macro | 0.700 |
| Micro P / R / F1 | 0.852 / 0.641 / 0.732 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 1750 | 3420 | 3798 | 6626 | 19253 | 2343 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 14 | 5 | 2 | 0.737 | 0.875 | 0.800 |
| scale | 14 | 11 | 0 | 3 | 1.000 | 0.786 | 0.880 |
| productType | 14 | 10 | 1 | 4 | 0.909 | 0.714 | 0.800 |
| state | 15 | 11 | 0 | 4 | 1.000 | 0.733 | 0.846 |
| city | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |
| supplyArea | 11 | 7 | 1 | 4 | 0.875 | 0.636 | 0.737 |
| project | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |
| publicationPeriod | 14 | 3 | 4 | 7 | 0.429 | 0.300 | 0.353 |
| creationPeriod | 2 | 1 | 0 | 1 | 1.000 | 0.500 | 0.667 |
| sortField | 10 | 3 | 0 | 7 | 1.000 | 0.300 | 0.462 |
| sortDirection | 10 | 3 | 0 | 7 | 1.000 | 0.300 | 0.462 |
| limit | 5 | 2 | 0 | 3 | 1.000 | 0.400 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 90.9% | 0.948 |
| Compostas | 43 | 44.2% | 0.693 |
| Código MI/INOM | 15 | 46.7% | 0.707 |
| Tempo relativo | 15 | 20.0% | 0.530 |
| Ordenação | 10 | 20.0% | 0.510 |
| Ambíguas/informais | 35 | 45.7% | 0.691 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 45.5% |
| N | 37 | 56.8% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 7, 'misto': 3, 'campo_omitido': 1, 'campo_inventado': 3, 'nao_chamou': 14}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 14

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
