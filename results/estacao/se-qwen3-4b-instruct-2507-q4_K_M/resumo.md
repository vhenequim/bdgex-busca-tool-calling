# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-28T15:07:09

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 50.8% |
| Precisão ponderada | 0.801 |
| Recall ponderado | 0.877 |
| F1 ponderado | 0.815 |
| F1 macro | 0.808 |
| Micro P / R / F1 | 0.773 / 0.868 / 0.818 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 663 | 1975 | 2229 | 5115 | 5661 | 1246 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 17 | 4 | 0 | 0.810 | 1.000 | 0.895 |
| scale | 14 | 9 | 1 | 4 | 0.900 | 0.692 | 0.783 |
| productType | 14 | 13 | 6 | 1 | 0.684 | 0.929 | 0.788 |
| state | 15 | 14 | 4 | 1 | 0.778 | 0.933 | 0.848 |
| city | 5 | 4 | 1 | 1 | 0.800 | 0.800 | 0.800 |
| supplyArea | 11 | 10 | 2 | 0 | 0.833 | 1.000 | 0.909 |
| project | 4 | 4 | 1 | 0 | 0.800 | 1.000 | 0.889 |
| publicationPeriod | 14 | 10 | 8 | 0 | 0.556 | 1.000 | 0.714 |
| creationPeriod | 2 | 1 | 1 | 0 | 0.500 | 1.000 | 0.667 |
| sortField | 10 | 6 | 0 | 4 | 1.000 | 0.600 | 0.750 |
| sortDirection | 10 | 6 | 0 | 4 | 1.000 | 0.600 | 0.750 |
| limit | 5 | 5 | 1 | 0 | 0.833 | 1.000 | 0.909 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 90.9% | 0.903 |
| Compostas | 43 | 39.5% | 0.803 |
| Código MI/INOM | 15 | 60.0% | 0.866 |
| Tempo relativo | 15 | 53.3% | 0.883 |
| Ordenação | 10 | 20.0% | 0.767 |
| Ambíguas/informais | 35 | 51.4% | 0.794 |
| Fora do domínio | 2 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 54.5% |
| N | 37 | 48.6% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 9, 'campo_omitido': 5, 'campo_inventado': 9, 'misto': 4, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.754, 'creationPeriod': 0.5}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 1
