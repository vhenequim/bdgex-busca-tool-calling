# gemma4:e2b-it-qat — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T12:38:36

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 891 |
| Acurácia por consulta | 46.9% |
| Precisão ponderada | 0.720 |
| Recall ponderado | 0.631 |
| F1 ponderado | 0.636 |
| F1 macro | 0.594 |
| Micro P / R / F1 | 0.684 / 0.656 / 0.670 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 891 | 228 | 404 | 430 | 729 | 1284 | 160 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 174 | 198 | 0 | 0.468 | 1.000 | 0.637 |
| scale | 249 | 174 | 21 | 54 | 0.892 | 0.763 | 0.823 |
| productType | 129 | 95 | 29 | 28 | 0.766 | 0.772 | 0.769 |
| state | 390 | 212 | 18 | 172 | 0.922 | 0.552 | 0.691 |
| city | 78 | 72 | 28 | 6 | 0.720 | 0.923 | 0.809 |
| supplyArea | 120 | 114 | 3 | 3 | 0.974 | 0.974 | 0.974 |
| project | 33 | 30 | 9 | 3 | 0.769 | 0.909 | 0.833 |
| publicationPeriod | 177 | 21 | 87 | 78 | 0.194 | 0.212 | 0.203 |
| creationPeriod | 9 | 3 | 12 | 3 | 0.200 | 0.500 | 0.286 |
| sortField | 87 | 12 | 6 | 69 | 0.667 | 0.148 | 0.242 |
| sortDirection | 87 | 18 | 24 | 45 | 0.429 | 0.286 | 0.343 |
| limit | 51 | 18 | 0 | 33 | 1.000 | 0.353 | 0.522 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 270 | 77.0% | 0.806 |
| Compostas | 552 | 38.0% | 0.646 |
| Código MI/INOM | 171 | 84.2% | 0.927 |
| Tempo relativo | 183 | 8.2% | 0.392 |
| Ordenação | 87 | 0.0% | 0.435 |
| Ambíguas/informais | 585 | 40.7% | 0.613 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 40.9% |
| N | 102 | 50.0% |
| G | 723 | 47.0% |

## Diagnósticos

- Tipos de erro: {'misto': 244, 'campo_inventado': 27, 'valor_errado': 66, 'nao_chamou': 115, 'campo_omitido': 21}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.873, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 115

## Observacionais (fora das métricas principais)

39 casos · acurácia 69.2% · chamou sem dever: 3

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 47.1% | 0.637 | 402 |
| 2 | 47.1% | 0.638 | 403 |
| 3 | 46.5% | 0.634 | 408 |
