# gemma4:e2b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T12:02:51

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 80.4% |
| Precisão ponderada | 0.916 |
| Recall ponderado | 0.931 |
| F1 ponderado | 0.920 |
| F1 macro | 0.930 |
| Micro P / R / F1 | 0.903 / 0.932 / 0.917 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 255 | 998 | 1242 | 2982 | 5001 | 829 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 215 | 98 | 10 | 0.687 | 0.956 | 0.799 |
| scale | 197 | 163 | 14 | 20 | 0.921 | 0.891 | 0.906 |
| productType | 192 | 178 | 5 | 13 | 0.973 | 0.932 | 0.952 |
| state | 136 | 126 | 8 | 9 | 0.940 | 0.933 | 0.937 |
| city | 103 | 91 | 11 | 12 | 0.892 | 0.883 | 0.888 |
| supplyArea | 175 | 168 | 1 | 7 | 0.994 | 0.960 | 0.977 |
| project | 95 | 89 | 0 | 6 | 1.000 | 0.937 | 0.967 |
| publicationPeriod | 88 | 77 | 1 | 10 | 0.987 | 0.885 | 0.933 |
| creationPeriod | 51 | 45 | 1 | 5 | 0.978 | 0.900 | 0.938 |
| sortField | 99 | 94 | 0 | 5 | 1.000 | 0.949 | 0.974 |
| sortDirection | 99 | 92 | 3 | 4 | 0.968 | 0.958 | 0.963 |
| limit | 52 | 51 | 7 | 1 | 0.879 | 0.981 | 0.927 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 93.2% | 0.960 |
| Compostas | 466 | 72.7% | 0.922 |
| Código MI/INOM | 130 | 92.3% | 0.967 |
| Tempo relativo | 139 | 73.4% | 0.930 |
| Ordenação | 99 | 89.9% | 0.969 |
| Ambíguas/informais | 457 | 73.7% | 0.914 |
| Fora do domínio | 163 | 91.4% | 0.000 |
| Subespecificadas | 65 | 64.6% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 26, 'nao_chamou': 31, 'misto': 13, 'campo_omitido': 11, 'campo_inventado': 90, 'chamou_sem_dever': 14}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 31

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
