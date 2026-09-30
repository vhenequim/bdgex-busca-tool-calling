# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T03:10:38

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 49.2% |
| Precisão ponderada | 0.741 |
| Recall ponderado | 0.762 |
| F1 ponderado | 0.733 |
| F1 macro | 0.704 |
| Micro P / R / F1 | 0.689 / 0.758 / 0.722 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 1251 | 2596 | 2857 | 5702 | 8098 | 1375 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 18 | 1 | 1 | 0.947 | 0.947 | 0.947 |
| scale | 14 | 8 | 0 | 6 | 1.000 | 0.571 | 0.727 |
| productType | 14 | 11 | 4 | 3 | 0.733 | 0.786 | 0.759 |
| state | 15 | 11 | 3 | 4 | 0.786 | 0.733 | 0.759 |
| city | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |
| supplyArea | 11 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| project | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |
| publicationPeriod | 14 | 8 | 9 | 2 | 0.471 | 0.800 | 0.593 |
| creationPeriod | 2 | 1 | 1 | 1 | 0.500 | 0.500 | 0.500 |
| sortField | 10 | 6 | 7 | 4 | 0.462 | 0.600 | 0.522 |
| sortDirection | 10 | 6 | 7 | 4 | 0.462 | 0.600 | 0.522 |
| limit | 6 | 5 | 7 | 1 | 0.417 | 0.833 | 0.556 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 81.8% | 0.879 |
| Compostas | 43 | 39.5% | 0.721 |
| Código MI/INOM | 15 | 73.3% | 0.886 |
| Tempo relativo | 15 | 33.3% | 0.760 |
| Ordenação | 10 | 20.0% | 0.740 |
| Ambíguas/informais | 35 | 37.1% | 0.694 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 45.5% |
| N | 37 | 51.4% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 4, 'misto': 15, 'campo_inventado': 4, 'nao_chamou': 6, 'campo_omitido': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.708, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 6

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
