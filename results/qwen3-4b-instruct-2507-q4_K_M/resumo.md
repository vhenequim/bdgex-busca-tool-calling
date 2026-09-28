# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-28T14:53:56

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 918 |
| Acurácia por consulta | 54.2% |
| Precisão ponderada | 0.697 |
| Recall ponderado | 0.743 |
| F1 ponderado | 0.666 |
| F1 macro | 0.599 |
| Micro P / R / F1 | 0.579 / 0.740 / 0.649 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 918 | 66 | 828 | 868 | 1403 | 3117 | 348 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 177 | 99 | 3 | 0.641 | 0.983 | 0.776 |
| scale | 252 | 90 | 15 | 147 | 0.857 | 0.380 | 0.526 |
| productType | 132 | 120 | 99 | 12 | 0.548 | 0.909 | 0.684 |
| state | 390 | 303 | 51 | 84 | 0.856 | 0.783 | 0.818 |
| city | 81 | 21 | 0 | 60 | 1.000 | 0.259 | 0.412 |
| supplyArea | 120 | 114 | 9 | 3 | 0.927 | 0.974 | 0.950 |
| project | 33 | 30 | 48 | 3 | 0.385 | 0.909 | 0.541 |
| publicationPeriod | 153 | 105 | 87 | 6 | 0.547 | 0.946 | 0.693 |
| creationPeriod | 30 | 15 | 6 | 12 | 0.714 | 0.556 | 0.625 |
| sortField | 87 | 57 | 141 | 30 | 0.288 | 0.655 | 0.400 |
| sortDirection | 87 | 57 | 141 | 30 | 0.288 | 0.655 | 0.400 |
| limit | 42 | 36 | 123 | 6 | 0.226 | 0.857 | 0.358 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 300 | 74.0% | 0.691 |
| Compostas | 540 | 39.4% | 0.654 |
| Código MI/INOM | 171 | 91.2% | 0.949 |
| Tempo relativo | 180 | 48.3% | 0.725 |
| Ordenação | 87 | 41.4% | 0.775 |
| Ambíguas/informais | 591 | 44.2% | 0.640 |
| Fora do domínio | 24 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 45.5% |
| N | 111 | 51.4% |
| G | 741 | 55.5% |

## Diagnósticos

- Tipos de erro: {'misto': 291, 'valor_errado': 33, 'campo_inventado': 48, 'nao_chamou': 39, 'campo_omitido': 9}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.819, 'creationPeriod': 0.833}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 39

## Observacionais (fora das métricas principais)

12 casos · acurácia 0.0% · chamou sem dever: 6

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 54.2% | 0.666 | 824 |
| 2 | 54.2% | 0.666 | 827 |
| 3 | 54.2% | 0.666 | 828 |
