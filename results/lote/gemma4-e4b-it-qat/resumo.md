# gemma4:e4b-it-qat — resumo da avaliação

1929 execuções · repetições [1] · gerado em 2026-09-29T01:48:20

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 1929 |
| Acurácia por consulta | 61.5% |
| Precisão ponderada | 0.892 |
| Recall ponderado | 0.682 |
| F1 ponderado | 0.761 |
| F1 macro | 0.732 |
| Micro P / R / F1 | 0.888 / 0.684 / 0.772 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 1929 | 355 | 864 | 969 | 1479 | 10922 | 725 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 492 | 414 | 87 | 38 | 0.826 | 0.916 | 0.869 |
| scale | 415 | 289 | 6 | 120 | 0.980 | 0.707 | 0.821 |
| productType | 386 | 253 | 103 | 125 | 0.711 | 0.669 | 0.689 |
| state | 304 | 201 | 4 | 100 | 0.980 | 0.668 | 0.794 |
| city | 207 | 89 | 2 | 116 | 0.978 | 0.434 | 0.601 |
| supplyArea | 346 | 273 | 0 | 73 | 1.000 | 0.789 | 0.882 |
| project | 176 | 154 | 3 | 22 | 0.981 | 0.875 | 0.925 |
| publicationPeriod | 203 | 55 | 33 | 122 | 0.625 | 0.311 | 0.415 |
| creationPeriod | 75 | 28 | 9 | 39 | 0.757 | 0.418 | 0.538 |
| sortField | 199 | 107 | 11 | 81 | 0.907 | 0.569 | 0.699 |
| sortDirection | 199 | 119 | 0 | 80 | 1.000 | 0.598 | 0.748 |
| limit | 103 | 70 | 2 | 33 | 0.972 | 0.680 | 0.800 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 389 | 53.0% | 0.660 |
| Compostas | 955 | 52.4% | 0.805 |
| Código MI/INOM | 281 | 77.9% | 0.934 |
| Tempo relativo | 278 | 22.7% | 0.575 |
| Ordenação | 199 | 39.2% | 0.756 |
| Ambíguas/informais | 927 | 48.1% | 0.769 |
| Fora do domínio | 336 | 100.0% | 0.000 |
| Subespecificadas | 146 | 97.3% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 464, 'campo_inventado': 83, 'valor_errado': 81, 'misto': 71, 'campo_omitido': 44}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 1.0, 'publicationPeriod': 0.978}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 464

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
