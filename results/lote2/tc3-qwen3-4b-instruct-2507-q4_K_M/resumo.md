# qwen3:4b-instruct-2507-q4_K_M — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T13:40:01

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 73.5% |
| Precisão ponderada | 0.812 |
| Recall ponderado | 0.804 |
| F1 ponderado | 0.789 |
| F1 macro | 0.775 |
| Micro P / R / F1 | 0.743 / 0.802 / 0.771 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 528 | 3150 | 4436 | 11629 | 37325 | 3939 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 234 | 208 | 9 | 21 | 0.959 | 0.908 | 0.933 |
| scale | 197 | 115 | 25 | 82 | 0.821 | 0.584 | 0.682 |
| productType | 192 | 129 | 13 | 63 | 0.908 | 0.672 | 0.772 |
| state | 139 | 109 | 6 | 30 | 0.948 | 0.784 | 0.858 |
| city | 107 | 99 | 3 | 8 | 0.971 | 0.925 | 0.947 |
| supplyArea | 175 | 139 | 16 | 36 | 0.897 | 0.794 | 0.842 |
| project | 93 | 80 | 36 | 13 | 0.690 | 0.860 | 0.766 |
| publicationPeriod | 105 | 102 | 19 | 1 | 0.843 | 0.990 | 0.911 |
| creationPeriod | 34 | 31 | 1 | 3 | 0.969 | 0.912 | 0.939 |
| sortField | 99 | 76 | 119 | 20 | 0.390 | 0.792 | 0.522 |
| sortDirection | 99 | 79 | 116 | 20 | 0.405 | 0.798 | 0.537 |
| limit | 50 | 38 | 54 | 0 | 0.413 | 1.000 | 0.585 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 84.9% | 0.931 |
| Compostas | 466 | 56.9% | 0.783 |
| Código MI/INOM | 130 | 87.7% | 0.950 |
| Tempo relativo | 139 | 83.5% | 0.937 |
| Ordenação | 99 | 67.7% | 0.892 |
| Ambíguas/informais | 457 | 59.7% | 0.766 |
| Fora do domínio | 163 | 97.5% | 0.000 |
| Subespecificadas | 65 | 83.1% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'campo_inventado': 41, 'nao_chamou': 46, 'misto': 133, 'campo_omitido': 20, 'valor_errado': 6, 'chamou_sem_dever': 4}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.977, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 46

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
