# gemma4:e2b-it-qat — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-28T16:10:07

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 918 |
| Acurácia por consulta | 56.5% |
| Precisão ponderada | 0.821 |
| Recall ponderado | 0.760 |
| F1 ponderado | 0.765 |
| F1 macro | 0.744 |
| Micro P / R / F1 | 0.786 / 0.764 / 0.775 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 918 | 224 | 397 | 420 | 703 | 1242 | 147 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 183 | 168 | 135 | 0 | 0.554 | 1.000 | 0.713 |
| scale | 252 | 183 | 24 | 45 | 0.884 | 0.803 | 0.841 |
| productType | 132 | 111 | 12 | 21 | 0.902 | 0.841 | 0.871 |
| state | 387 | 261 | 18 | 117 | 0.935 | 0.690 | 0.795 |
| city | 87 | 87 | 21 | 0 | 0.806 | 1.000 | 0.892 |
| supplyArea | 120 | 108 | 6 | 6 | 0.947 | 0.947 | 0.947 |
| project | 33 | 30 | 3 | 3 | 0.909 | 0.909 | 0.909 |
| publicationPeriod | 153 | 60 | 63 | 36 | 0.488 | 0.625 | 0.548 |
| creationPeriod | 30 | 9 | 15 | 9 | 0.375 | 0.500 | 0.429 |
| sortField | 87 | 30 | 0 | 57 | 1.000 | 0.345 | 0.513 |
| sortDirection | 87 | 42 | 6 | 39 | 0.875 | 0.519 | 0.651 |
| limit | 30 | 21 | 0 | 9 | 1.000 | 0.700 | 0.824 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 300 | 79.0% | 0.844 |
| Compostas | 540 | 47.8% | 0.763 |
| Código MI/INOM | 171 | 78.9% | 0.929 |
| Tempo relativo | 180 | 21.7% | 0.645 |
| Ordenação | 87 | 20.7% | 0.691 |
| Ambíguas/informais | 591 | 51.3% | 0.744 |
| Fora do domínio | 24 | 62.5% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 40.9% |
| N | 111 | 51.4% |
| G | 741 | 58.7% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 42, 'campo_inventado': 24, 'valor_errado': 87, 'misto': 150, 'nao_chamou': 87, 'chamou_sem_dever': 9}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.844, 'creationPeriod': 0.875}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 87

## Observacionais (fora das métricas principais)

12 casos · acurácia 75.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 56.5% | 0.765 | 399 |
| 2 | 56.5% | 0.765 | 397 |
| 3 | 56.5% | 0.765 | 395 |
