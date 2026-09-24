# mistral-nemo:12b — resumo da avaliação

225 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T10:52:13

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 213 |
| Acurácia por consulta | 22.5% |
| Precisão ponderada | 0.775 |
| Recall ponderado | 0.295 |
| F1 ponderado | 0.406 |
| F1 macro | 0.361 |
| Micro P / R / F1 | 0.709 / 0.295 / 0.417 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 213 | 387 | 3191 | 3912 | 9662 | 20639 | 3247 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 60 | 12 | 0 | 48 | 1.000 | 0.200 | 0.333 |
| scale | 51 | 15 | 3 | 33 | 0.833 | 0.312 | 0.455 |
| productType | 42 | 21 | 3 | 21 | 0.875 | 0.500 | 0.636 |
| state | 54 | 18 | 0 | 36 | 1.000 | 0.333 | 0.500 |
| city | 18 | 6 | 0 | 12 | 1.000 | 0.333 | 0.500 |
| supplyArea | 51 | 9 | 0 | 42 | 1.000 | 0.176 | 0.300 |
| project | 12 | 0 | 0 | 12 | 0.000 | 0.000 | 0.000 |
| publicationPeriod | 42 | 15 | 6 | 21 | 0.714 | 0.417 | 0.526 |
| creationPeriod | 6 | 0 | 0 | 6 | 0.000 | 0.000 | 0.000 |
| sortField | 30 | 9 | 12 | 21 | 0.429 | 0.300 | 0.353 |
| sortDirection | 30 | 3 | 18 | 21 | 0.143 | 0.125 | 0.133 |
| limit | 15 | 9 | 6 | 6 | 0.600 | 0.600 | 0.600 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 66 | 31.8% | 0.442 |
| Compostas | 132 | 13.6% | 0.392 |
| Código MI/INOM | 45 | 13.3% | 0.232 |
| Tempo relativo | 45 | 13.3% | 0.511 |
| Ordenação | 30 | 10.0% | 0.464 |
| Ambíguas/informais | 123 | 14.6% | 0.391 |
| Fora do domínio | 6 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 9.1% |
| N | 111 | 29.7% |
| G | 36 | 25.0% |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 141, 'campo_omitido': 3, 'campo_inventado': 12, 'valor_errado': 6, 'misto': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.825}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 141

## Observacionais (fora das métricas principais)

12 casos · acurácia 50.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 22.5% | 0.406 | 3192 |
| 2 | 22.5% | 0.406 | 3185 |
| 3 | 22.5% | 0.406 | 3172 |
