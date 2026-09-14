# gemma4:e2b-it-qat — resumo da avaliação

14 execuções · repetições [1] · gerado em 2026-09-14T11:56:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 13 |
| Acurácia por consulta | 38.5% |
| Precisão ponderada | 0.725 |
| Recall ponderado | 0.656 |
| F1 ponderado | 0.672 |
| F1 macro | 0.693 |
| Micro P / R / F1 | 0.840 / 0.724 / 0.778 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 13 | 888 | 5037 | 5793 | 11540 | 12483 | 3704 |

Latência da ferramenta (SQL): mediana 46.1 ms, máx 57.0 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 4 | 4 | 1 | 0 | 0.800 | 1.000 | 0.889 |
| scale | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 7 | 6 | 0 | 1 | 1.000 | 0.857 | 0.923 |
| city | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 4 | 0 | 2 | 2 | 0.000 | 0.000 | 0.000 |
| creationPeriod | 1 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| sortField | 3 | 0 | 0 | 3 | 0.000 | 0.000 | 0.000 |
| sortDirection | 3 | 1 | 0 | 2 | 1.000 | 0.333 | 0.500 |
| limit | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 2 | 100.0% | 1.000 |
| Compostas | 9 | 33.3% | 0.696 |
| Código MI/INOM | 4 | 75.0% | 0.815 |
| Tempo relativo | 5 | 0.0% | 0.489 |
| Ordenação | 3 | 0.0% | 0.633 |
| Ambíguas/informais | 9 | 44.4% | 0.664 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 5 | 40.0% |
| N | 3 | 33.3% |
| G | 5 | 40.0% |

## Diagnósticos

- Tipos de erro: {'misto': 2, 'valor_errado': 1, 'nao_chamou': 2, 'campo_omitido': 2, 'campo_inventado': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.704}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 2

## Observacionais (fora das métricas principais)

1 casos · acurácia 100.0% · chamou sem dever: 0
