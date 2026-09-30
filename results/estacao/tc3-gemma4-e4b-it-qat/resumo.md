# gemma4:e4b-it-qat — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T00:26:12

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 98.3% |
| Precisão ponderada | 0.992 |
| Recall ponderado | 0.992 |
| F1 ponderado | 0.992 |
| F1 macro | 0.995 |
| Micro P / R / F1 | 0.992 / 0.992 / 0.992 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 1645 | 5630 | 7126 | 15432 | 24158 | 4643 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 19 | 19 | 1 | 0 | 0.950 | 1.000 | 0.974 |
| scale | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| productType | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 15 | 14 | 0 | 1 | 1.000 | 0.933 | 0.966 |
| city | 6 | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 12 | 12 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| creationPeriod | 4 | 4 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| limit | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 100.0% | 1.000 |
| Compostas | 43 | 97.7% | 0.991 |
| Código MI/INOM | 15 | 100.0% | 1.000 |
| Tempo relativo | 15 | 100.0% | 1.000 |
| Ordenação | 10 | 100.0% | 1.000 |
| Ambíguas/informais | 35 | 97.1% | 0.986 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 100.0% |
| N | 37 | 97.3% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
