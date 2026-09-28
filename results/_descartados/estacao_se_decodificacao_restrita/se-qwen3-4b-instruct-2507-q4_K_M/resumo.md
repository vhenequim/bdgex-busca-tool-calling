# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T14:37:13

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 33.9% |
| Precisão ponderada | 0.463 |
| Recall ponderado | 0.561 |
| F1 ponderado | 0.469 |
| F1 macro | 0.377 |
| Micro P / R / F1 | 0.533 / 0.596 / 0.563 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 741 | 2065 | 2092 | 3331 | 4392 | 812 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 17 | 9 | 0 | 0.654 | 1.000 | 0.791 |
| scale | 14 | 8 | 6 | 5 | 0.571 | 0.615 | 0.593 |
| productType | 14 | 13 | 5 | 1 | 0.722 | 0.929 | 0.813 |
| state | 15 | 12 | 8 | 3 | 0.600 | 0.800 | 0.686 |
| city | 5 | 0 | 0 | 5 | 0.000 | 0.000 | 0.000 |
| supplyArea | 11 | 10 | 16 | 0 | 0.385 | 1.000 | 0.556 |
| project | 4 | 3 | 1 | 1 | 0.750 | 0.750 | 0.750 |
| publicationPeriod | 14 | 0 | 11 | 5 | 0.000 | 0.000 | 0.000 |
| creationPeriod | 2 | 0 | 1 | 1 | 0.000 | 0.000 | 0.000 |
| sortField | 10 | 2 | 0 | 8 | 1.000 | 0.200 | 0.333 |
| sortDirection | 10 | 0 | 0 | 10 | 0.000 | 0.000 | 0.000 |
| limit | 5 | 0 | 0 | 5 | 0.000 | 0.000 | 0.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 90.9% | 0.903 |
| Compostas | 43 | 23.3% | 0.463 |
| Código MI/INOM | 15 | 46.7% | 0.679 |
| Tempo relativo | 15 | 0.0% | 0.376 |
| Ordenação | 10 | 0.0% | 0.247 |
| Ambíguas/informais | 35 | 34.3% | 0.499 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 31.8% |
| N | 37 | 35.1% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 17, 'campo_omitido': 7, 'valor_errado': 11, 'campo_inventado': 2, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 0.0% · chamou sem dever: 1
