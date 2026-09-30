# qwen3:4b-instruct-2507-q4_K_M [saida-estruturada-v3] — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-30T13:54:23

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 88.3% |
| Precisão ponderada | 0.965 |
| Recall ponderado | 0.922 |
| F1 ponderado | 0.941 |
| F1 macro | 0.946 |
| Micro P / R / F1 | 0.965 / 0.922 / 0.943 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 213 | 652 | 902 | 2511 | 4813 | 777 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 241 | 212 | 25 | 21 | 0.895 | 0.910 | 0.902 |
| scale | 197 | 175 | 14 | 8 | 0.926 | 0.956 | 0.941 |
| productType | 192 | 172 | 1 | 19 | 0.994 | 0.901 | 0.945 |
| state | 139 | 122 | 3 | 17 | 0.976 | 0.878 | 0.924 |
| city | 100 | 70 | 3 | 30 | 0.959 | 0.700 | 0.809 |
| supplyArea | 175 | 174 | 0 | 1 | 1.000 | 0.994 | 0.997 |
| project | 94 | 80 | 1 | 13 | 0.988 | 0.860 | 0.920 |
| publicationPeriod | 105 | 103 | 1 | 2 | 0.990 | 0.981 | 0.986 |
| creationPeriod | 34 | 33 | 0 | 1 | 1.000 | 0.971 | 0.985 |
| sortField | 99 | 95 | 1 | 3 | 0.990 | 0.969 | 0.979 |
| sortDirection | 99 | 96 | 0 | 3 | 1.000 | 0.970 | 0.985 |
| limit | 60 | 60 | 2 | 0 | 0.968 | 1.000 | 0.984 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 85.9% | 0.922 |
| Compostas | 466 | 82.4% | 0.940 |
| Código MI/INOM | 130 | 97.7% | 0.994 |
| Tempo relativo | 139 | 92.8% | 0.978 |
| Ordenação | 99 | 88.9% | 0.972 |
| Ambíguas/informais | 457 | 83.4% | 0.933 |
| Fora do domínio | 163 | 98.8% | 0.000 |
| Subespecificadas | 65 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 49, 'valor_errado': 18, 'campo_inventado': 19, 'misto': 10, 'campo_omitido': 13, 'chamou_sem_dever': 2}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 49

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
