# gemma4:e4b-it-qat — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T12:30:46

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 891 |
| Acurácia por consulta | 50.4% |
| Precisão ponderada | 0.775 |
| Recall ponderado | 0.683 |
| F1 ponderado | 0.709 |
| F1 macro | 0.643 |
| Micro P / R / F1 | 0.775 / 0.703 / 0.737 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 891 | 411 | 745 | 848 | 1306 | 5763 | 583 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 151 | 49 | 5 | 0.755 | 0.968 | 0.848 |
| scale | 249 | 197 | 13 | 39 | 0.938 | 0.835 | 0.883 |
| productType | 129 | 93 | 105 | 30 | 0.470 | 0.756 | 0.579 |
| state | 390 | 292 | 10 | 95 | 0.967 | 0.755 | 0.848 |
| city | 78 | 71 | 6 | 7 | 0.922 | 0.910 | 0.916 |
| supplyArea | 120 | 94 | 6 | 26 | 0.940 | 0.783 | 0.855 |
| project | 33 | 30 | 19 | 3 | 0.612 | 0.909 | 0.732 |
| publicationPeriod | 177 | 11 | 60 | 107 | 0.155 | 0.093 | 0.116 |
| creationPeriod | 9 | 3 | 14 | 6 | 0.176 | 0.333 | 0.231 |
| sortField | 87 | 26 | 17 | 44 | 0.605 | 0.371 | 0.460 |
| sortDirection | 87 | 43 | 0 | 44 | 1.000 | 0.494 | 0.662 |
| limit | 51 | 21 | 0 | 30 | 1.000 | 0.412 | 0.583 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 270 | 78.1% | 0.853 |
| Compostas | 552 | 42.4% | 0.723 |
| Código MI/INOM | 171 | 75.4% | 0.865 |
| Tempo relativo | 183 | 6.0% | 0.360 |
| Ordenação | 87 | 6.9% | 0.533 |
| Ambíguas/informais | 585 | 43.8% | 0.695 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 37.9% |
| N | 102 | 54.9% |
| G | 723 | 50.9% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 94, 'misto': 87, 'campo_omitido': 7, 'campo_inventado': 86, 'nao_chamou': 168}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.788, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 168

## Observacionais (fora das métricas principais)

39 casos · acurácia 69.2% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 50.2% | 0.709 | 754 |
| 2 | 50.8% | 0.708 | 745 |
| 3 | 50.2% | 0.709 | 747 |
