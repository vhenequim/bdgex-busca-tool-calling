# mistral-nemo:12b — resumo da avaliação

930 execuções · repetições [1, 2, 3] · gerado em 2026-09-28T14:53:56

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 918 |
| Acurácia por consulta | 26.8% |
| Precisão ponderada | 0.804 |
| Recall ponderado | 0.326 |
| F1 ponderado | 0.451 |
| F1 macro | 0.420 |
| Micro P / R / F1 | 0.736 / 0.326 / 0.452 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 918 | 316 | 2391 | 2651 | 5860 | 16085 | 1787 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 186 | 51 | 0 | 135 | 1.000 | 0.274 | 0.430 |
| scale | 252 | 66 | 12 | 174 | 0.846 | 0.275 | 0.415 |
| productType | 132 | 54 | 9 | 78 | 0.857 | 0.409 | 0.554 |
| state | 387 | 129 | 21 | 249 | 0.860 | 0.341 | 0.489 |
| city | 84 | 42 | 0 | 42 | 1.000 | 0.500 | 0.667 |
| supplyArea | 120 | 33 | 0 | 87 | 1.000 | 0.275 | 0.431 |
| project | 30 | 0 | 0 | 30 | 0.000 | 0.000 | 0.000 |
| publicationPeriod | 153 | 45 | 12 | 96 | 0.789 | 0.319 | 0.455 |
| creationPeriod | 30 | 9 | 3 | 18 | 0.750 | 0.333 | 0.462 |
| sortField | 87 | 30 | 42 | 57 | 0.417 | 0.345 | 0.377 |
| sortDirection | 87 | 24 | 48 | 57 | 0.333 | 0.296 | 0.314 |
| limit | 30 | 18 | 33 | 12 | 0.353 | 0.600 | 0.444 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 300 | 32.0% | 0.443 |
| Compostas | 540 | 20.0% | 0.431 |
| Código MI/INOM | 171 | 21.1% | 0.362 |
| Tempo relativo | 180 | 16.7% | 0.450 |
| Ordenação | 87 | 24.1% | 0.530 |
| Ambíguas/informais | 591 | 19.8% | 0.429 |
| Fora do domínio | 24 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 9.1% |
| N | 111 | 29.7% |
| G | 741 | 27.9% |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 561, 'campo_omitido': 18, 'campo_inventado': 48, 'valor_errado': 27, 'misto': 18}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.897, 'creationPeriod': 0.936}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 561

## Observacionais (fora das métricas principais)

12 casos · acurácia 50.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 26.8% | 0.451 | 2397 |
| 2 | 26.8% | 0.451 | 2391 |
| 3 | 26.8% | 0.451 | 2380 |
