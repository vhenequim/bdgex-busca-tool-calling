# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T17:08:23

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 47.5% |
| Precisão ponderada | 0.724 |
| Recall ponderado | 0.761 |
| F1 ponderado | 0.724 |
| F1 macro | 0.663 |
| Micro P / R / F1 | 0.674 / 0.761 / 0.715 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 1439 | 3019 | 3348 | 5962 | 10955 | 1607 |

Latência da ferramenta (SQL): mediana 41.2 ms, máx 62.4 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 16 | 3 | 1 | 0.842 | 0.941 | 0.889 |
| scale | 14 | 8 | 0 | 6 | 1.000 | 0.571 | 0.727 |
| productType | 14 | 12 | 3 | 2 | 0.800 | 0.857 | 0.828 |
| state | 15 | 11 | 3 | 4 | 0.786 | 0.733 | 0.759 |
| city | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |
| supplyArea | 11 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| project | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |
| publicationPeriod | 14 | 8 | 9 | 2 | 0.471 | 0.800 | 0.593 |
| creationPeriod | 2 | 0 | 2 | 1 | 0.000 | 0.000 | 0.000 |
| sortField | 10 | 6 | 7 | 4 | 0.462 | 0.600 | 0.522 |
| sortDirection | 10 | 6 | 7 | 4 | 0.462 | 0.600 | 0.522 |
| limit | 6 | 5 | 7 | 1 | 0.417 | 0.833 | 0.556 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 81.8% | 0.879 |
| Compostas | 43 | 37.2% | 0.709 |
| Código MI/INOM | 15 | 66.7% | 0.856 |
| Tempo relativo | 15 | 33.3% | 0.729 |
| Ordenação | 10 | 20.0% | 0.749 |
| Ambíguas/informais | 35 | 34.3% | 0.677 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 45.5% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 14, 'campo_omitido': 1, 'valor_errado': 6, 'campo_inventado': 4, 'nao_chamou': 6}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.742, 'creationPeriod': 0.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 6

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
