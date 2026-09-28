# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T14:43:26

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 50.8% |
| Precisão ponderada | 0.583 |
| Recall ponderado | 0.896 |
| F1 ponderado | 0.700 |
| F1 macro | 0.673 |
| Micro P / R / F1 | 0.572 / 0.892 / 0.697 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 805 | 2214 | 2621 | 6106 | 7064 | 1513 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 17 | 9 | 0 | 0.654 | 1.000 | 0.791 |
| scale | 14 | 9 | 6 | 4 | 0.600 | 0.692 | 0.643 |
| productType | 14 | 13 | 11 | 1 | 0.542 | 0.929 | 0.684 |
| state | 15 | 14 | 7 | 0 | 0.667 | 1.000 | 0.800 |
| city | 5 | 4 | 6 | 1 | 0.400 | 0.800 | 0.533 |
| supplyArea | 11 | 10 | 7 | 0 | 0.588 | 1.000 | 0.741 |
| project | 4 | 4 | 6 | 0 | 0.400 | 1.000 | 0.571 |
| publicationPeriod | 14 | 10 | 8 | 0 | 0.556 | 1.000 | 0.714 |
| creationPeriod | 2 | 1 | 1 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 10 | 6 | 4 | 3 | 0.600 | 0.667 | 0.632 |
| sortDirection | 10 | 6 | 4 | 3 | 0.600 | 0.667 | 0.632 |
| limit | 6 | 5 | 5 | 0 | 0.500 | 1.000 | 0.667 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 90.9% | 0.903 |
| Compostas | 43 | 39.5% | 0.731 |
| Código MI/INOM | 15 | 60.0% | 0.866 |
| Tempo relativo | 15 | 53.3% | 0.811 |
| Ordenação | 10 | 20.0% | 0.702 |
| Ambíguas/informais | 35 | 51.4% | 0.752 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 54.5% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 8, 'campo_omitido': 4, 'campo_inventado': 11, 'misto': 4, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.754, 'creationPeriod': 0.5}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
