# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 59 | 49.2% | 36.8–61.6% | 0.741 | 0.762 | 0.733 | 0.704 | 2596 | 5702 | 0 |
| Gemma 4 E2B | 59 | 47.5% | 35.3–60.0% | 0.795 | 0.722 | 0.719 | 0.666 | 709 | 1198 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| Simples | 0.879 | 0.887 |
| Compostas | 0.721 | 0.716 |
| Com código MI/INOM | 0.886 | 0.867 |
| Com referência temporal relativa | 0.760 | 0.655 |
| Com ordenação | 0.740 | 0.541 |
| Ambíguas / variações ortográficas | 0.694 | 0.693 |

## Acurácia por categoria

| Categoria | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| Simples | 81.8% | 81.8% |
| Compostas | 39.5% | 39.5% |
| Com código MI/INOM | 73.3% | 60.0% |
| Com referência temporal relativa | 33.3% | 13.3% |
| Com ordenação | 20.0% | 0.0% |
| Ambíguas / variações ortográficas | 37.1% | 40.0% |
| Fora do domínio (recusa) | 100.0% | 100.0% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|---|
| `keyword` | 20 | 0.947 | 0.810 |
| `scale` | 14 | 0.727 | 0.833 |
| `productType` | 14 | 0.759 | 0.923 |
| `state` | 15 | 0.759 | 0.786 |
| `city` | 5 | 0.750 | 0.923 |
| `supplyArea` | 11 | 0.900 | 1.000 |
| `project` | 5 | 0.909 | 0.800 |
| `publicationPeriod` | 14 | 0.593 | 0.526 |
| `creationPeriod` | 2 | 0.500 | 0.000 |
| `sortField` | 10 | 0.522 | 0.182 |
| `sortDirection` | 10 | 0.522 | 0.462 |
| `limit` | 6 | 0.556 | 0.750 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| P | 45.5% | 45.5% |
| N | 51.4% | 48.6% |
| G | — | — |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'valor_errado': 4, 'misto': 15, 'campo_inventado': 4, 'nao_chamou': 6, 'campo_omitido': 1}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.708, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 6
- observacionais: 3 casos, acurácia 33.3%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

### Gemma 4 E2B

- tipos de erro: {'campo_omitido': 4, 'valor_errado': 9, 'campo_inventado': 3, 'misto': 7, 'nao_chamou': 8}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.671}
- chamadas com erro: 0 {}
- não chamou quando devia: 8
- observacionais: 3 casos, acurácia 66.7%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

