# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T12:15:34

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 891 |
| Acurácia por consulta | 43.8% |
| Precisão ponderada | 0.645 |
| Recall ponderado | 0.711 |
| F1 ponderado | 0.623 |
| F1 macro | 0.521 |
| Micro P / R / F1 | 0.541 / 0.710 / 0.614 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 891 | 64 | 1044 | 1080 | 1824 | 4059 | 474 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 174 | 132 | 3 | 0.569 | 0.983 | 0.720 |
| scale | 249 | 108 | 12 | 129 | 0.900 | 0.456 | 0.605 |
| productType | 129 | 102 | 144 | 24 | 0.415 | 0.810 | 0.548 |
| state | 390 | 294 | 63 | 90 | 0.824 | 0.766 | 0.794 |
| city | 78 | 21 | 0 | 57 | 1.000 | 0.269 | 0.424 |
| supplyArea | 120 | 114 | 3 | 3 | 0.974 | 0.974 | 0.974 |
| project | 33 | 30 | 21 | 3 | 0.588 | 0.909 | 0.714 |
| publicationPeriod | 177 | 66 | 153 | 15 | 0.301 | 0.815 | 0.440 |
| creationPeriod | 9 | 0 | 6 | 6 | 0.000 | 0.000 | 0.000 |
| sortField | 87 | 27 | 129 | 33 | 0.173 | 0.450 | 0.250 |
| sortDirection | 87 | 54 | 102 | 33 | 0.346 | 0.621 | 0.444 |
| limit | 51 | 30 | 99 | 21 | 0.233 | 0.588 | 0.333 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 270 | 66.7% | 0.650 |
| Compostas | 552 | 34.2% | 0.623 |
| Código MI/INOM | 171 | 87.7% | 0.934 |
| Tempo relativo | 183 | 24.6% | 0.555 |
| Ordenação | 87 | 10.3% | 0.631 |
| Ambíguas/informais | 585 | 33.8% | 0.589 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 40.9% |
| N | 102 | 47.1% |
| G | 723 | 43.6% |

## Diagnósticos

- Tipos de erro: {'misto': 279, 'valor_errado': 78, 'campo_inventado': 87, 'nao_chamou': 48, 'campo_omitido': 9}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.736, 'creationPeriod': 0.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 48

## Observacionais (fora das métricas principais)

39 casos · acurácia 53.8% · chamou sem dever: 9

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 43.8% | 0.623 | 989 |
| 2 | 43.8% | 0.623 | 1061 |
| 3 | 43.8% | 0.623 | 1065 |
