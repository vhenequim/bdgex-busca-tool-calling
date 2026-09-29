# gemma4:e4b-it-qat — resumo da avaliação

945 execuções · repetições [1] · gerado em 2026-09-29T22:04:55

## Geral (métricas principais)

| Métrica | Valor |
|---|---|
| Consultas | 945 |
| Acurácia por consulta | 58.6% |
| Precisão ponderada | 0.886 |
| Recall ponderado | 0.640 |
| F1 ponderado | 0.731 |
| F1 macro | 0.687 |
| Micro P / R / F1 | 0.885 / 0.642 / 0.744 |

## Latência do LLM (ms)

| n | mín | mediana | média | p95 | máx | desvio |
|---|---|---|---|---|---|---|
| 945 | 347 | 848 | 928 | 1410 | 6773 | 538 |

## Por campo

| Campo | Ocorr. | TP | FP | FN | Precisão | Recall | F1 |
|---|---|---|---|---|---|---|---|
| keyword | 240 | 197 | 31 | 26 | 0.864 | 0.883 | 0.874 |
| scale | 197 | 125 | 4 | 68 | 0.969 | 0.648 | 0.776 |
| productType | 192 | 116 | 46 | 72 | 0.716 | 0.617 | 0.663 |
| state | 138 | 85 | 5 | 52 | 0.944 | 0.620 | 0.749 |
| city | 102 | 46 | 5 | 51 | 0.902 | 0.474 | 0.622 |
| supplyArea | 175 | 138 | 0 | 37 | 1.000 | 0.789 | 0.882 |
| project | 99 | 83 | 4 | 13 | 0.954 | 0.865 | 0.907 |
| publicationPeriod | 102 | 31 | 16 | 57 | 0.660 | 0.352 | 0.459 |
| creationPeriod | 37 | 9 | 4 | 25 | 0.692 | 0.265 | 0.383 |
| sortField | 99 | 42 | 3 | 54 | 0.933 | 0.438 | 0.596 |
| sortDirection | 99 | 45 | 0 | 54 | 1.000 | 0.455 | 0.625 |
| limit | 42 | 25 | 4 | 17 | 0.862 | 0.595 | 0.704 |

## Por categoria

| Categoria | n | Acurácia | F1 ponderado |
|---|---|---|---|
| Simples | 192 | 51.0% | 0.658 |
| Compostas | 466 | 49.1% | 0.776 |
| Código MI/INOM | 130 | 80.8% | 0.940 |
| Tempo relativo | 139 | 22.3% | 0.562 |
| Ordenação | 99 | 27.3% | 0.636 |
| Ambíguas/informais | 457 | 49.2% | 0.769 |
| Fora do domínio | 163 | 100.0% | 0.000 |
| Subespecificadas | 65 | 95.4% | 0.000 |

## Por origem

| Origem | n | Acurácia |
|---|---|---|
| P | 0 | — |
| N | 0 | — |
| G | 0 | — |

## Diagnósticos

- Tipos de erro: {'nao_chamou': 254, 'misto': 23, 'campo_inventado': 44, 'valor_errado': 41, 'campo_omitido': 29}
- Campos fora do schema: {}
- IoU médio de períodos: {'creationPeriod': 0.839, 'publicationPeriod': 1.0}
- Chamadas com erro de infraestrutura: 0 {}
- Respostas do modelo fora do schema da ferramenta: 0 {}
- Não chamou a ferramenta quando devia: 254

## Observacionais (fora das métricas principais)

0 casos · acurácia — · chamou sem dever: 0
