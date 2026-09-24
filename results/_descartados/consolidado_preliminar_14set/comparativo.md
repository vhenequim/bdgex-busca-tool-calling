# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 61 | 44.3% | 32.5–56.7% | 0.711 | 0.752 | 0.706 | 0.648 | 2944 | 5962 | 0 |
| Gemma 4 E2B | 13 | 38.5% | 17.7–64.5% | 0.725 | 0.656 | 0.672 | 0.693 | 5037 | 11540 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| Simples | 0.889 | 1.000 |
| Compostas | 0.692 | 0.696 |
| Com código MI/INOM | 0.863 | 0.815 |
| Com referência temporal relativa | 0.669 | 0.489 |
| Com ordenação | 0.723 | 0.633 |
| Ambíguas / variações ortográficas | 0.649 | 0.664 |

## Acurácia por categoria

| Categoria | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| Simples | 83.3% | 100.0% |
| Compostas | 35.6% | 33.3% |
| Com código MI/INOM | 68.8% | 75.0% |
| Com referência temporal relativa | 25.0% | 0.0% |
| Com ordenação | 18.2% | 0.0% |
| Ambíguas / variações ortográficas | 31.6% | 44.4% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|---|
| `keyword` | 21 | 0.895 | 0.889 |
| `scale` | 15 | 0.696 | 1.000 |
| `productType` | 13 | 0.815 | 1.000 |
| `state` | 19 | 0.833 | 0.923 |
| `city` | 5 | 0.750 | 1.000 |
| `supplyArea` | 11 | 0.900 | 1.000 |
| `project` | 5 | 0.909 | 1.000 |
| `publicationPeriod` | 14 | 0.519 | 0.000 |
| `creationPeriod` | 3 | 0.000 | 0.000 |
| `sortField` | 11 | 0.417 | 0.000 |
| `sortDirection` | 11 | 0.538 | 0.500 |
| `limit` | 6 | 0.500 | 1.000 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B | Gemma 4 E2B |
|---|---|---|
| P | 40.9% | 40.0% |
| N | 44.1% | 33.3% |
| G | 60.0% | 40.0% |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 17, 'valor_errado': 7, 'campo_inventado': 4, 'nao_chamou': 6}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.783, 'creationPeriod': 0.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 6
- observacionais: 6 casos, acurácia 66.7%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

### Gemma 4 E2B

- tipos de erro: {'misto': 2, 'valor_errado': 1, 'nao_chamou': 2, 'campo_omitido': 2, 'campo_inventado': 1}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.704}
- chamadas com erro: 0 {}
- não chamou quando devia: 2
- observacionais: 1 casos, acurácia 100.0%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

