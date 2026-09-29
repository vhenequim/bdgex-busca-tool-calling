# gemma4:e4b-it-qat [saida-estruturada] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T21:08:51

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 61.3% |
| Precisão ponderada | 0.883 |
| Recall ponderado | 0.929 |
| F1 ponderado | 0.895 |
| F1 macro | 0.883 |
| Micro P / R / F1 | 0.867 / 0.928 / 0.897 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 105 | 720 | 731 | 1444 | 2458 | 433 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 213 | 114 | 0 | 0.651 | 1.000 | 0.789 |
| scale | 197 | 177 | 14 | 8 | 0.927 | 0.957 | 0.941 |
| productType | 192 | 175 | 13 | 6 | 0.931 | 0.967 | 0.949 |
| state | 139 | 119 | 13 | 19 | 0.902 | 0.862 | 0.881 |
| city | 100 | 54 | 3 | 43 | 0.947 | 0.557 | 0.701 |
| supplyArea | 175 | 175 | 1 | 0 | 0.994 | 1.000 | 0.997 |
| project | 100 | 96 | 6 | 1 | 0.941 | 0.990 | 0.965 |
| publicationPeriod | 105 | 87 | 31 | 1 | 0.737 | 0.989 | 0.845 |
| creationPeriod | 34 | 16 | 4 | 14 | 0.800 | 0.533 | 0.640 |
| sortField | 99 | 88 | 5 | 6 | 0.946 | 0.936 | 0.941 |
| sortDirection | 99 | 93 | 0 | 6 | 1.000 | 0.939 | 0.969 |
| limit | 57 | 57 | 3 | 0 | 0.950 | 1.000 | 0.974 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 85.4% | 0.894 |
| Compostas | 466 | 70.2% | 0.910 |
| Código MI/INOM | 130 | 80.0% | 0.938 |
| Tempo relativo | 139 | 68.3% | 0.874 |
| Ordenação | 99 | 73.7% | 0.940 |
| Ambíguas/informais | 457 | 71.3% | 0.898 |
| Fora do domínio | 163 | 0.0% | 0.000 |
| Subespecificadas | 65 | 66.2% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 36, 'misto': 67, 'valor_errado': 72, 'campo_omitido': 28, 'chamou_sem_dever': 163}
- Campos fora do schema: {'error': 17}
- IoU médio de períodos: {'publicationPeriod': 0.886, 'creationPeriod': 0.834}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
