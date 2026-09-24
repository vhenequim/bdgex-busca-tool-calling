# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 59 | 47.5% | 35.3–60.0% | 0.724 | 0.761 | 0.724 | 0.663 | 3019 | 5962 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B |
|---|---|
| Simples | 0.879 |
| Compostas | 0.709 |
| Com código MI/INOM | 0.856 |
| Com referência temporal relativa | 0.729 |
| Com ordenação | 0.749 |
| Ambíguas / variações ortográficas | 0.677 |

## Acurácia por categoria

| Categoria | Qwen 3 4B |
|---|---|
| Simples | 81.8% |
| Compostas | 37.2% |
| Com código MI/INOM | 66.7% |
| Com referência temporal relativa | 33.3% |
| Com ordenação | 20.0% |
| Ambíguas / variações ortográficas | 34.3% |
| Fora do domínio (recusa) | 100.0% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B |
|---|---|---|
| `keyword` | 20 | 0.889 |
| `scale` | 14 | 0.727 |
| `productType` | 14 | 0.828 |
| `state` | 15 | 0.759 |
| `city` | 5 | 0.750 |
| `supplyArea` | 11 | 0.900 |
| `project` | 5 | 0.909 |
| `publicationPeriod` | 14 | 0.593 |
| `creationPeriod` | 2 | 0.000 |
| `sortField` | 10 | 0.522 |
| `sortDirection` | 10 | 0.522 |
| `limit` | 6 | 0.556 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B |
|---|---|
| P | 45.5% |
| N | 48.6% |
| G | — |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 14, 'campo_omitido': 1, 'valor_errado': 6, 'campo_inventado': 4, 'nao_chamou': 6}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.742, 'creationPeriod': 0.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 6
- observacionais: 3 casos, acurácia 33.3%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.0 · repetições [1]

