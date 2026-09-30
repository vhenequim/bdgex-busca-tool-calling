# qwen/qwen3.8-27b [saida-estruturada] — resumo da avaliação

310 execuções · repetições [1] · gerado em 2026-09-30T03:10:37

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 306 |
| Acurácia por consulta | 92.8% |
| Precisão ponderada | 0.970 |
| Recall ponderado | 0.991 |
| F1 ponderado | 0.979 |
| F1 macro | 0.971 |
| Micro P / R / F1 | 0.969 / 0.991 / 0.980 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 306 | 344 | 482 | 642 | 1109 | 7025 | 619 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 62 | 62 | 4 | 0 | 0.939 | 1.000 | 0.969 |
| scale | 84 | 82 | 1 | 1 | 0.988 | 0.988 | 0.988 |
| productType | 44 | 44 | 1 | 0 | 0.978 | 1.000 | 0.989 |
| state | 130 | 130 | 1 | 0 | 0.992 | 1.000 | 0.996 |
| city | 27 | 27 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| supplyArea | 40 | 40 | 1 | 0 | 0.976 | 1.000 | 0.988 |
| project | 11 | 11 | 1 | 0 | 0.917 | 1.000 | 0.957 |
| publicationPeriod | 51 | 46 | 7 | 0 | 0.868 | 1.000 | 0.929 |
| creationPeriod | 10 | 8 | 0 | 2 | 1.000 | 0.800 | 0.889 |
| sortField | 29 | 27 | 1 | 1 | 0.964 | 0.964 | 0.964 |
| sortDirection | 29 | 28 | 0 | 1 | 1.000 | 0.966 | 0.982 |
| limit | 21 | 21 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 100 | 98.0% | 0.990 |
| Compostas | 180 | 93.3% | 0.981 |
| Código MI/INOM | 57 | 100.0% | 1.000 |
| Tempo relativo | 60 | 88.3% | 0.962 |
| Ordenação | 29 | 89.7% | 0.986 |
| Ambíguas/informais | 197 | 94.9% | 0.985 |
| Fora do domínio | 8 | 0.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 83.8% |
| G | 247 | 94.7% |

## Diagnósticos

- Tipos de erro: {'campo_omitido': 2, 'campo_inventado': 3, 'valor_errado': 7, 'chamou_sem_dever': 8, 'misto': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.956, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

4 casos · acurácia 25.0% · chamou sem dever: 2
