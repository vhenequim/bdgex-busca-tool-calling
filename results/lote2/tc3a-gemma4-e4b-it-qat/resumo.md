# gemma4:e4b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T21:35:02

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 83.1% |
| Precisão ponderada | 0.945 |
| Recall ponderado | 0.918 |
| F1 ponderado | 0.929 |
| F1 macro | 0.923 |
| Micro P / R / F1 | 0.944 / 0.918 / 0.931 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 221 | 1365 | 1628 | 3354 | 12397 | 1099 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 236 | 223 | 24 | 6 | 0.903 | 0.974 | 0.937 |
| scale | 197 | 187 | 1 | 9 | 0.995 | 0.954 | 0.974 |
| productType | 192 | 161 | 4 | 30 | 0.976 | 0.843 | 0.904 |
| state | 134 | 94 | 7 | 40 | 0.931 | 0.701 | 0.800 |
| city | 110 | 100 | 5 | 10 | 0.952 | 0.909 | 0.930 |
| supplyArea | 175 | 173 | 0 | 2 | 1.000 | 0.989 | 0.994 |
| project | 99 | 91 | 6 | 5 | 0.938 | 0.948 | 0.943 |
| publicationPeriod | 101 | 78 | 12 | 14 | 0.867 | 0.848 | 0.857 |
| creationPeriod | 38 | 32 | 5 | 4 | 0.865 | 0.889 | 0.877 |
| sortField | 99 | 96 | 5 | 2 | 0.950 | 0.980 | 0.965 |
| sortDirection | 99 | 97 | 4 | 2 | 0.960 | 0.980 | 0.970 |
| limit | 58 | 58 | 9 | 0 | 0.866 | 1.000 | 0.928 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 88.5% | 0.934 |
| Compostas | 466 | 75.3% | 0.930 |
| Código MI/INOM | 130 | 90.0% | 0.963 |
| Tempo relativo | 139 | 74.1% | 0.901 |
| Ordenação | 99 | 84.8% | 0.969 |
| Ambíguas/informais | 457 | 77.0% | 0.923 |
| Fora do domínio | 163 | 96.3% | 0.000 |
| Subespecificadas | 65 | 86.2% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 16, 'nao_chamou': 13, 'campo_omitido': 70, 'campo_inventado': 33, 'misto': 22, 'chamou_sem_dever': 6}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.979, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 13

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
