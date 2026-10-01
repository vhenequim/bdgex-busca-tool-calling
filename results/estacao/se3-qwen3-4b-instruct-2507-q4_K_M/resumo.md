# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada-v3] — resumo da avaliação

62 execuções · repetições [1] · gerado em 2026-09-30T21:04:18

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 59 |
| Acurácia por consulta | 86.4% |
| Precisão ponderada | 0.967 |
| Recall ponderado | 0.937 |
| F1 ponderado | 0.950 |
| F1 macro | 0.950 |
| Micro P / R / F1 | 0.967 / 0.937 / 0.952 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 59 | 958 | 3211 | 4362 | 13649 | 16375 | 3619 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 20 | 20 | 1 | 0 | 0.952 | 1.000 | 0.976 |
| scale | 14 | 13 | 1 | 0 | 0.929 | 1.000 | 0.963 |
| productType | 14 | 14 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| state | 15 | 13 | 0 | 2 | 1.000 | 0.867 | 0.929 |
| city | 5 | 4 | 0 | 1 | 1.000 | 0.800 | 0.889 |
| supplyArea | 11 | 11 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 5 | 5 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| publicationPeriod | 14 | 13 | 0 | 1 | 1.000 | 0.929 | 0.963 |
| creationPeriod | 2 | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| sortField | 10 | 8 | 1 | 2 | 0.889 | 0.800 | 0.842 |
| sortDirection | 10 | 8 | 1 | 2 | 0.889 | 0.800 | 0.842 |
| limit | 7 | 7 | 0 | 0 | 1.000 | 1.000 | 1.000 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 11 | 100.0% | 1.000 |
| Compostas | 43 | 86.0% | 0.957 |
| Código MI/INOM | 15 | 100.0% | 1.000 |
| Tempo relativo | 15 | 86.7% | 0.966 |
| Ordenação | 10 | 70.0% | 0.919 |
| Ambíguas/informais | 35 | 80.0% | 0.928 |
| Fora do domínio | 2 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 22 | 86.4% |
| N | 37 | 86.5% |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 1, 'nao_chamou': 2, 'campo_omitido': 3, 'campo_inventado': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 2

## Observacionais (fora das métricas principais)

3 casos · acurácia 33.3% · chamou sem dever: 0
