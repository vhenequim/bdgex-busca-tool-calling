# mistral-nemo:12b — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T13:29:43

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 891 |
| Acurácia por consulta | 23.6% |
| Precisão ponderada | 0.696 |
| Recall ponderado | 0.351 |
| F1 ponderado | 0.448 |
| F1 macro | 0.370 |
| Micro P / R / F1 | 0.602 / 0.354 / 0.446 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 891 | 387 | 2739 | 3296 | 7433 | 20639 | 2654 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 63 | 0 | 123 | 1.000 | 0.339 | 0.506 |
| scale | 249 | 69 | 24 | 156 | 0.742 | 0.307 | 0.434 |
| productType | 129 | 51 | 33 | 78 | 0.607 | 0.395 | 0.479 |
| state | 390 | 150 | 18 | 237 | 0.893 | 0.388 | 0.541 |
| city | 78 | 39 | 3 | 39 | 0.929 | 0.500 | 0.650 |
| supplyArea | 120 | 39 | 3 | 81 | 0.929 | 0.325 | 0.481 |
| project | 33 | 0 | 9 | 33 | 0.000 | 0.000 | 0.000 |
| publicationPeriod | 177 | 36 | 57 | 84 | 0.387 | 0.300 | 0.338 |
| creationPeriod | 9 | 0 | 3 | 9 | 0.000 | 0.000 | 0.000 |
| sortField | 87 | 18 | 81 | 45 | 0.182 | 0.286 | 0.222 |
| sortDirection | 87 | 30 | 69 | 45 | 0.303 | 0.400 | 0.345 |
| limit | 51 | 27 | 45 | 21 | 0.375 | 0.562 | 0.450 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 270 | 40.0% | 0.534 |
| Compostas | 552 | 17.4% | 0.436 |
| Código MI/INOM | 171 | 29.8% | 0.390 |
| Tempo relativo | 183 | 8.2% | 0.415 |
| Ordenação | 87 | 10.3% | 0.492 |
| Ambíguas/informais | 585 | 18.5% | 0.449 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 9.1% |
| N | 102 | 23.5% |
| G | 723 | 24.9% |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 501, 'campo_omitido': 12, 'campo_inventado': 78, 'valor_errado': 51, 'misto': 39}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.784}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 501

## Observacionais (fora das métricas principais)

39 casos · acurácia 69.2% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 23.6% | 0.448 | 2785 |
| 2 | 23.6% | 0.448 | 2734 |
| 3 | 23.6% | 0.448 | 2724 |
