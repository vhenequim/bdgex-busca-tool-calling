# gemma4:e4b-it-qat [saida-estruturada-v2] — resumo da avaliação

1929 execuções · repetições [1] · gerado em 2026-09-29T03:05:40

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 1929 |
| Acurácia por consulta | 72.4% |
| Precisão ponderada | 0.909 |
| Recall ponderado | 0.845 |
| F1 ponderado | 0.860 |
| F1 macro | 0.857 |
| Micro P / R / F1 | 0.902 / 0.846 / 0.873 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 1929 | 251 | 608 | 724 | 1478 | 2571 | 418 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 492 | 434 | 152 | 1 | 0.741 | 0.998 | 0.850 |
| scale | 415 | 357 | 6 | 52 | 0.983 | 0.873 | 0.925 |
| productType | 386 | 309 | 9 | 74 | 0.972 | 0.807 | 0.882 |
| state | 300 | 169 | 58 | 81 | 0.744 | 0.676 | 0.709 |
| city | 211 | 59 | 4 | 148 | 0.937 | 0.285 | 0.437 |
| supplyArea | 346 | 332 | 0 | 14 | 1.000 | 0.960 | 0.979 |
| project | 167 | 150 | 1 | 17 | 0.993 | 0.898 | 0.943 |
| publicationPeriod | 211 | 151 | 18 | 44 | 0.893 | 0.774 | 0.830 |
| creationPeriod | 67 | 49 | 5 | 13 | 0.907 | 0.790 | 0.845 |
| sortField | 199 | 191 | 2 | 7 | 0.990 | 0.965 | 0.977 |
| sortDirection | 199 | 192 | 1 | 7 | 0.995 | 0.965 | 0.980 |
| limit | 150 | 146 | 20 | 4 | 0.880 | 0.973 | 0.924 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 389 | 55.5% | 0.634 |
| Compostas | 955 | 65.4% | 0.885 |
| Código MI/INOM | 281 | 76.5% | 0.935 |
| Tempo relativo | 278 | 61.2% | 0.844 |
| Ordenação | 199 | 73.4% | 0.943 |
| Ambíguas/informais | 927 | 61.1% | 0.856 |
| Fora do domínio | 336 | 100.0% | 0.000 |
| Subespecificadas | 146 | 100.0% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 257, 'valor_errado': 117, 'misto': 61, 'campo_omitido': 24, 'campo_inventado': 73}
- Campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.909, 'creationPeriod': 0.904}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 257

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
