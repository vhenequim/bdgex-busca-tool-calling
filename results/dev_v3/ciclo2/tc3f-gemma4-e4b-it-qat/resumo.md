# gemma4:e4b-it-qat — resumo da avaliação

160 execuções · repetições [1] · gerado em 2026-09-29T11:18:58

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 160 |
| Acurácia por consulta | 96.9% |
| Precisão ponderada | 0.990 |
| Recall ponderado | 0.990 |
| F1 ponderado | 0.990 |
| F1 macro | 0.987 |
| Micro P / R / F1 | 0.990 / 0.990 / 0.990 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 160 | 1242 | 6404 | 8666 | 17752 | 75946 | 8286 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 49 | 49 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| scale | 37 | 35 | 1 | 1 | 0.972 | 0.972 | 0.972 |
| productType | 34 | 33 | 0 | 1 | 1.000 | 0.971 | 0.985 |
| state | 29 | 29 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| city | 20 | 20 | 1 | 0 | 0.952 | 1.000 | 0.976 |
| supplyArea | 31 | 31 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 15 | 15 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 16 | 16 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| creationPeriod | 11 | 10 | 0 | 1 | 1.000 | 0.909 | 0.952 |
| sortField | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortDirection | 20 | 20 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| limit | 12 | 12 | 1 | 0 | 0.923 | 1.000 | 0.960 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 33 | 100.0% | 1.000 |
| Compostas | 93 | 95.7% | 0.990 |
| Código MI/INOM | 30 | 96.7% | 0.995 |
| Tempo relativo | 27 | 96.3% | 0.990 |
| Ordenação | 20 | 95.0% | 0.994 |
| Ambíguas/informais | 87 | 95.4% | 0.988 |
| Fora do domínio | 15 | 100.0% | 0.000 |
| Subespecificadas | 10 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 1, 'campo_inventado': 2, 'valor_errado': 1, 'nao_chamou': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 1

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
