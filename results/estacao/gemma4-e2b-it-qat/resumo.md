# gemma4:e2b-it-qat — resumo da avaliação

9 execuções · repetições [1] · gerado em 2026-09-24T09:43:18

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 9 |
| Acurácia por consulta | 44.4% |
| Precisão ponderada | 0.870 |
| Recall ponderado | 0.739 |
| F1 ponderado | 0.788 |
| F1 macro | 0.772 |
| Micro P / R / F1 | 0.944 / 0.773 / 0.850 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 9 | 888 | 7361 | 6517 | 12483 | 12483 | 4041 |

Latência da ferramenta (SQL): mediana 39.6 ms, máx 51.4 ms.

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| scale | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| city | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 3 | 3 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 1 | 1 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 3 | 2 | 0 | 1 | 1.000 | 0.667 | 0.800 |
| creationPeriod | 1 | 0 | 1 | 0 | 0.000 | 0.000 | 0.000 |
| sortField | 2 | 0 | 0 | 2 | 0.000 | 0.000 | 0.000 |
| sortDirection | 2 | 1 | 0 | 1 | 1.000 | 0.500 | 0.667 |
| limit | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 1 | 100.0% | 1.000 |
| Compostas | 6 | 33.3% | 0.794 |
| Código MI/INOM | 3 | 66.7% | 0.857 |
| Tempo relativo | 4 | 0.0% | 0.695 |
| Ordenação | 2 | 0.0% | 0.778 |
| Ambíguas/informais | 5 | 40.0% | 0.738 |
| Fora do domínio | 1 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 5 | 40.0% |
| N | 4 | 50.0% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 3, 'valor_errado': 1, 'nao_chamou': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 1

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
