# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 61 | 44.3% | 32.5–56.7% | 0.711 | 0.752 | 0.706 | 0.648 | 2944 | 5962 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B |
|---|---|
| Simples | 0.889 |
| Compostas | 0.692 |
| Com código MI/INOM | 0.863 |
| Com referência temporal relativa | 0.669 |
| Com ordenação | 0.723 |
| Ambíguas / variações ortográficas | 0.649 |

## Acurácia por categoria

| Categoria | Qwen 3 4B |
|---|---|
| Simples | 83.3% |
| Compostas | 35.6% |
| Com código MI/INOM | 68.8% |
| Com referência temporal relativa | 25.0% |
| Com ordenação | 18.2% |
| Ambíguas / variações ortográficas | 31.6% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B |
|---|---|---|
| `keyword` | 21 | 0.895 |
| `scale` | 15 | 0.696 |
| `productType` | 13 | 0.815 |
| `state` | 19 | 0.833 |
| `city` | 5 | 0.750 |
| `supplyArea` | 11 | 0.900 |
| `project` | 5 | 0.909 |
| `publicationPeriod` | 14 | 0.519 |
| `creationPeriod` | 3 | 0.000 |
| `sortField` | 11 | 0.417 |
| `sortDirection` | 11 | 0.538 |
| `limit` | 6 | 0.500 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B |
|---|---|
| P | 40.9% |
| N | 44.1% |
| G | 60.0% |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 17, 'valor_errado': 7, 'campo_inventado': 4, 'nao_chamou': 6}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.783, 'creationPeriod': 0.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 6
- observacionais: 6 casos, acurácia 66.7%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

