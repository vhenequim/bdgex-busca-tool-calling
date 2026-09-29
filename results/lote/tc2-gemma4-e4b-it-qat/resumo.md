# gemma4:e4b-it-qat — resumo da avaliação

1929 execuções · repetições [1] · gerado em 2026-09-29T02:42:05

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 1929 |
| Acurácia por consulta | 62.8% |
| Precisão ponderada | 0.774 |
| Recall ponderado | 0.944 |
| F1 ponderado | 0.840 |
| F1 macro | 0.846 |
| Micro P / R / F1 | 0.752 / 0.948 / 0.839 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 1929 | 288 | 937 | 917 | 1452 | 2398 | 324 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 491 | 352 | 234 | 9 | 0.601 | 0.975 | 0.743 |
| scale | 415 | 385 | 11 | 19 | 0.972 | 0.953 | 0.963 |
| productType | 386 | 366 | 249 | 17 | 0.595 | 0.956 | 0.733 |
| state | 301 | 155 | 134 | 32 | 0.536 | 0.829 | 0.651 |
| city | 211 | 161 | 36 | 43 | 0.817 | 0.789 | 0.803 |
| supplyArea | 346 | 345 | 0 | 1 | 1.000 | 0.997 | 0.999 |
| project | 170 | 162 | 4 | 8 | 0.976 | 0.953 | 0.964 |
| publicationPeriod | 172 | 126 | 41 | 11 | 0.754 | 0.920 | 0.829 |
| creationPeriod | 106 | 75 | 24 | 7 | 0.758 | 0.915 | 0.829 |
| sortField | 199 | 199 | 17 | 0 | 0.921 | 1.000 | 0.959 |
| sortDirection | 199 | 199 | 17 | 0 | 0.921 | 1.000 | 0.959 |
| limit | 146 | 146 | 113 | 0 | 0.564 | 1.000 | 0.721 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 389 | 60.2% | 0.749 |
| Compostas | 955 | 49.9% | 0.863 |
| Código MI/INOM | 281 | 50.5% | 0.825 |
| Tempo relativo | 278 | 37.4% | 0.835 |
| Ordenação | 199 | 52.8% | 0.911 |
| Ambíguas/informais | 927 | 50.3% | 0.841 |
| Fora do domínio | 336 | 99.7% | 0.000 |
| Subespecificadas | 146 | 71.9% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 228, 'misto': 91, 'campo_omitido': 37, 'campo_inventado': 347, 'nao_chamou': 13, 'chamou_sem_dever': 1}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.919, 'creationPeriod': 0.87}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 1 {'args_invalidos': 1}
- Não chamou a ferramenta quando devia: 13

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
