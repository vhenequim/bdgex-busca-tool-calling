# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

67 execuções · repetições [1] · gerado em 2026-09-14T11:38:22

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 61 |
| Acurácia por consulta | 44.3% |
| Precisão ponderada | 0.711 |
| Recall ponderado | 0.752 |
| F1 ponderado | 0.706 |
| F1 macro | 0.648 |
| Micro P / R / F1 | 0.648 / 0.754 / 0.697 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 61 | 1439 | 2944 | 3341 | 5962 | 10955 | 1578 |

Latência da ferramenta (SQL): mediana 40.5 ms, máx 62.4 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 21 | 17 | 3 | 1 | 0.850 | 0.944 | 0.895 |
| scale | 15 | 8 | 0 | 7 | 1.000 | 0.533 | 0.696 |
| productType | 13 | 11 | 3 | 2 | 0.786 | 0.846 | 0.815 |
| state | 19 | 15 | 2 | 4 | 0.882 | 0.789 | 0.833 |
| city | 5 | 3 | 0 | 2 | 1.000 | 0.600 | 0.750 |
| supplyArea | 11 | 9 | 1 | 1 | 0.900 | 0.900 | 0.900 |
| project | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |
| publicationPeriod | 14 | 7 | 11 | 2 | 0.389 | 0.778 | 0.519 |
| creationPeriod | 3 | 0 | 2 | 2 | 0.000 | 0.000 | 0.000 |
| sortField | 11 | 5 | 10 | 4 | 0.333 | 0.556 | 0.417 |
| sortDirection | 11 | 7 | 8 | 4 | 0.467 | 0.636 | 0.538 |
| limit | 6 | 5 | 9 | 1 | 0.357 | 0.833 | 0.500 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 12 | 83.3% | 0.889 |
| Compostas | 45 | 35.6% | 0.692 |
| Código MI/INOM | 16 | 68.8% | 0.863 |
| Tempo relativo | 16 | 25.0% | 0.669 |
| Ordenação | 11 | 18.2% | 0.723 |
| Ambíguas/informais | 38 | 31.6% | 0.649 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 40.9% |
| N | 34 | 44.1% |
| G | 5 | 60.0% |

## Diagnósticos

- Tipos de erro: {'misto': 17, 'valor_errado': 7, 'campo_inventado': 4, 'nao_chamou': 6}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.783, 'creationPeriod': 0.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 6

## Observacionais (fora das métricas principais)

6 casos · acurácia 66.7% · chamou sem dever: 0
