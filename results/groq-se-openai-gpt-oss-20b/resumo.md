# openai/gpt-oss-20b [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-28T17:08:27

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 77.5% |
| Precisão ponderada | 0.932 |
| Recall ponderado | 0.915 |
| F1 ponderado | 0.919 |
| F1 macro | 0.918 |
| Micro P / R / F1 | 0.928 / 0.914 / 0.921 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 265 | 462 | 574 | 1156 | 3476 | 366 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 59 | 6 | 0 | 0.908 | 1.000 | 0.952 |
| scale | 84 | 69 | 6 | 9 | 0.920 | 0.885 | 0.902 |
| productType | 44 | 38 | 2 | 6 | 0.950 | 0.864 | 0.905 |
| state | 130 | 121 | 12 | 6 | 0.910 | 0.953 | 0.931 |
| city | 27 | 24 | 0 | 3 | 1.000 | 0.889 | 0.941 |
| supplyArea | 40 | 38 | 2 | 0 | 0.950 | 1.000 | 0.974 |
| project | 10 | 10 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 51 | 46 | 7 | 0 | 0.868 | 1.000 | 0.929 |
| creationPeriod | 10 | 8 | 0 | 2 | 1.000 | 0.800 | 0.889 |
| sortField | 29 | 20 | 0 | 9 | 1.000 | 0.690 | 0.816 |
| sortDirection | 29 | 20 | 0 | 9 | 1.000 | 0.690 | 0.816 |
| limit | 12 | 12 | 1 | 0 | 0.923 | 1.000 | 0.960 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 92.0% | 0.957 |
| Compostas | 180 | 71.1% | 0.910 |
| Código MI/INOM | 57 | 86.0% | 0.954 |
| Tempo relativo | 60 | 85.0% | 0.942 |
| Ordenação | 29 | 58.6% | 0.877 |
| Ambíguas/informais | 197 | 75.1% | 0.907 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 63.6% |
| N | 37 | 75.7% |
| G | 247 | 78.9% |

## Diagnósticos

- Tipos de erro: {'valor_errado': 18, 'campo_inventado': 11, 'campo_omitido': 29, 'misto': 3, 'chamou_sem_dever': 8}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.943, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
