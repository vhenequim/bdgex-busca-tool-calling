# gemma4:e4b-it-qat [saida-estruturada] — resumo da avaliação

1929 execuções · repetições [1] · gerado em 2026-09-29T02:12:05

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 1929 |
| Acurácia por consulta | 62.2% |
| Precisão ponderada | 0.883 |
| Recall ponderado | 0.927 |
| F1 ponderado | 0.892 |
| F1 macro | 0.872 |
| Micro P / R / F1 | 0.865 / 0.927 / 0.895 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 1929 | 103 | 722 | 727 | 1448 | 2303 | 429 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 492 | 437 | 257 | 0 | 0.630 | 1.000 | 0.773 |
| scale | 415 | 390 | 14 | 11 | 0.965 | 0.973 | 0.969 |
| productType | 386 | 364 | 18 | 11 | 0.953 | 0.971 | 0.962 |
| state | 307 | 254 | 31 | 48 | 0.891 | 0.841 | 0.865 |
| city | 204 | 99 | 8 | 99 | 0.925 | 0.500 | 0.649 |
| supplyArea | 346 | 346 | 1 | 0 | 0.997 | 1.000 | 0.999 |
| project | 181 | 181 | 8 | 0 | 0.958 | 1.000 | 0.978 |
| publicationPeriod | 214 | 177 | 67 | 1 | 0.725 | 0.994 | 0.839 |
| creationPeriod | 64 | 24 | 9 | 31 | 0.727 | 0.436 | 0.545 |
| sortField | 199 | 177 | 13 | 9 | 0.932 | 0.952 | 0.941 |
| sortDirection | 199 | 190 | 0 | 9 | 1.000 | 0.955 | 0.977 |
| limit | 138 | 138 | 8 | 0 | 0.945 | 1.000 | 0.972 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 389 | 79.2% | 0.822 |
| Compostas | 955 | 73.7% | 0.919 |
| Código MI/INOM | 281 | 78.3% | 0.936 |
| Tempo relativo | 278 | 65.8% | 0.852 |
| Ordenação | 199 | 77.4% | 0.956 |
| Ambíguas/informais | 927 | 72.9% | 0.902 |
| Fora do domínio | 336 | 0.0% | 0.000 |
| Subespecificadas | 146 | 74.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'misto': 146, 'valor_errado': 125, 'campo_omitido': 55, 'campo_inventado': 67, 'chamou_sem_dever': 336}
- Campos fora do schema: {'error': 33}
- IoU médio de períodos: {'publicationPeriod': 0.874, 'creationPeriod': 0.729}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 0

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
