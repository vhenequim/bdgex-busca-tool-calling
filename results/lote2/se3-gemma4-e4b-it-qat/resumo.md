# gemma4:e4b-it-qat [saida-estruturada-v3] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T20:42:04

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 87.8% |
| Precisão ponderada | 0.950 |
| Recall ponderado | 0.947 |
| F1 ponderado | 0.946 |
| F1 macro | 0.952 |
| Micro P / R / F1 | 0.947 / 0.947 / 0.947 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 250 | 781 | 939 | 2553 | 4704 | 692 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 213 | 48 | 4 | 0.816 | 0.982 | 0.891 |
| scale | 197 | 169 | 15 | 13 | 0.918 | 0.929 | 0.923 |
| productType | 192 | 177 | 0 | 15 | 1.000 | 0.922 | 0.959 |
| state | 136 | 131 | 8 | 5 | 0.942 | 0.963 | 0.953 |
| city | 103 | 82 | 3 | 19 | 0.965 | 0.812 | 0.882 |
| supplyArea | 175 | 175 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| project | 99 | 93 | 3 | 3 | 0.969 | 0.969 | 0.969 |
| publicationPeriod | 104 | 98 | 1 | 6 | 0.990 | 0.942 | 0.966 |
| creationPeriod | 35 | 32 | 0 | 3 | 1.000 | 0.914 | 0.955 |
| sortField | 99 | 94 | 0 | 5 | 1.000 | 0.949 | 0.974 |
| sortDirection | 99 | 94 | 0 | 5 | 1.000 | 0.949 | 0.974 |
| limit | 61 | 59 | 1 | 2 | 0.983 | 0.967 | 0.975 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 88.0% | 0.931 |
| Compostas | 466 | 82.0% | 0.949 |
| Código MI/INOM | 130 | 84.6% | 0.958 |
| Tempo relativo | 139 | 89.9% | 0.963 |
| Ordenação | 99 | 86.9% | 0.962 |
| Ambíguas/informais | 457 | 81.8% | 0.938 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 95.4% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'valor_errado': 42, 'nao_chamou': 36, 'campo_inventado': 28, 'misto': 7, 'campo_omitido': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 36

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
