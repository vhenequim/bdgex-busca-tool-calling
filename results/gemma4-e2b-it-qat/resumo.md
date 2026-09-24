# gemma4:e2b-it-qat — resumo da avaliação

225 execuções · repetições [1, 2, 3] · gerado em 2026-09-24T11:04:05

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 213 |
| Acurácia por consulta | 50.7% |
| Precisão ponderada | 0.801 |
| Recall ponderado | 0.730 |
| F1 ponderado | 0.722 |
| F1 macro | 0.696 |
| Micro P / R / F1 | 0.775 / 0.732 / 0.753 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 213 | 237 | 427 | 496 | 956 | 1284 | 214 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 57 | 51 | 36 | 0 | 0.586 | 1.000 | 0.739 |
| scale | 51 | 36 | 6 | 9 | 0.857 | 0.800 | 0.828 |
| productType | 42 | 33 | 6 | 9 | 0.846 | 0.786 | 0.815 |
| state | 57 | 39 | 6 | 18 | 0.867 | 0.684 | 0.765 |
| city | 18 | 18 | 3 | 0 | 0.857 | 1.000 | 0.923 |
| supplyArea | 51 | 51 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 15 | 12 | 3 | 3 | 0.800 | 0.800 | 0.800 |
| publicationPeriod | 42 | 18 | 12 | 12 | 0.600 | 0.600 | 0.600 |
| creationPeriod | 6 | 3 | 3 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 30 | 3 | 0 | 27 | 1.000 | 0.100 | 0.182 |
| sortDirection | 30 | 9 | 6 | 15 | 0.600 | 0.375 | 0.462 |
| limit | 15 | 6 | 0 | 9 | 1.000 | 0.400 | 0.571 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 66 | 77.3% | 0.770 |
| Compostas | 132 | 38.6% | 0.721 |
| Código MI/INOM | 45 | 60.0% | 0.910 |
| Tempo relativo | 45 | 20.0% | 0.714 |
| Ordenação | 30 | 0.0% | 0.566 |
| Ambíguas/informais | 123 | 39.0% | 0.654 |
| Fora do domínio | 6 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 40.9% |
| N | 111 | 51.4% |
| G | 36 | 66.7% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 12, 'campo_inventado': 15, 'valor_errado': 21, 'misto': 30, 'nao_chamou': 27}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.743, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 27

## Observacionais (fora das métricas principais)

12 casos · acurácia 75.0% · chamou sem dever: 0

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 50.7% | 0.722 | 429 |
| 2 | 50.7% | 0.722 | 415 |
| 3 | 50.7% | 0.722 | 429 |
