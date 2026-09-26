# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

225 execuções · repetições [1, 2, 3] · gerado em 2026-09-26T14:38:56

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 213 |
| Acurácia por consulta | 52.1% |
| Precisão ponderada | 0.725 |
| Recall ponderado | 0.756 |
| F1 ponderado | 0.716 |
| F1 macro | 0.645 |
| Micro P / R / F1 | 0.669 / 0.756 / 0.710 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 213 | 64 | 993 | 1119 | 2398 | 4059 | 594 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 60 | 51 | 9 | 3 | 0.850 | 0.944 | 0.895 |
| scale | 51 | 24 | 0 | 27 | 1.000 | 0.471 | 0.640 |
| productType | 42 | 36 | 15 | 6 | 0.706 | 0.857 | 0.774 |
| state | 57 | 42 | 12 | 15 | 0.778 | 0.737 | 0.757 |
| city | 15 | 9 | 0 | 6 | 1.000 | 0.600 | 0.750 |
| supplyArea | 51 | 45 | 3 | 3 | 0.938 | 0.938 | 0.938 |
| project | 15 | 15 | 6 | 0 | 0.714 | 1.000 | 0.833 |
| publicationPeriod | 42 | 24 | 27 | 6 | 0.471 | 0.800 | 0.593 |
| creationPeriod | 6 | 0 | 6 | 3 | 0.000 | 0.000 | 0.000 |
| sortField | 30 | 18 | 24 | 12 | 0.429 | 0.600 | 0.500 |
| sortDirection | 30 | 18 | 24 | 12 | 0.429 | 0.600 | 0.500 |
| limit | 18 | 15 | 21 | 3 | 0.417 | 0.833 | 0.556 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 66 | 77.3% | 0.798 |
| Compostas | 132 | 38.6% | 0.705 |
| Código MI/INOM | 45 | 73.3% | 0.872 |
| Tempo relativo | 45 | 33.3% | 0.718 |
| Ordenação | 30 | 20.0% | 0.740 |
| Ambíguas/informais | 123 | 34.1% | 0.642 |
| Fora do domínio | 6 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 66 | 45.5% |
| N | 111 | 51.4% |
| G | 36 | 66.7% |

## Diagnósticos

- Tipos de erro: {'misto': 51, 'valor_errado': 15, 'campo_inventado': 12, 'nao_chamou': 21, 'campo_omitido': 3}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.742, 'creationPeriod': 0.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 21

## Observacionais (fora das métricas principais)

12 casos · acurácia 0.0% · chamou sem dever: 6

## Por repetição

| Rep. | Acurácia | F1 ponderado | Lat. mediana (ms) |
|---|---|---|---|
| 1 | 52.1% | 0.716 | 883 |
| 2 | 52.1% | 0.716 | 1061 |
| 3 | 52.1% | 0.716 | 1066 |
