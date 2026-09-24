# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 213 | 52.1% | 45.4–58.7% | 0.725 | 0.756 | 0.716 | 0.645 | 993 | 2398 | 0 |
| Gemma 4 E4B | 213 | 55.4% | 48.7–61.9% | 0.866 | 0.648 | 0.713 | 0.704 | 820 | 3504 | 0 |
| Gemma 4 E2B | 213 | 50.7% | 44.0–57.3% | 0.801 | 0.730 | 0.722 | 0.696 | 427 | 956 | 0 |
| Mistral Nemo 12B | 213 | 22.5% | 17.4–28.6% | 0.775 | 0.295 | 0.406 | 0.361 | 3191 | 9662 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 0.798 | 0.903 | 0.770 | 0.442 |
| Compostas | 0.705 | 0.690 | 0.721 | 0.392 |
| Com código MI/INOM | 0.872 | 0.721 | 0.910 | 0.232 |
| Com referência temporal relativa | 0.718 | 0.530 | 0.714 | 0.511 |
| Com ordenação | 0.740 | 0.510 | 0.566 | 0.464 |
| Ambíguas / variações ortográficas | 0.642 | 0.687 | 0.654 | 0.391 |

## Acurácia por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 77.3% | 84.8% | 77.3% | 31.8% |
| Compostas | 38.6% | 42.4% | 38.6% | 13.6% |
| Com código MI/INOM | 73.3% | 46.7% | 60.0% | 13.3% |
| Com referência temporal relativa | 33.3% | 20.0% | 20.0% | 13.3% |
| Com ordenação | 20.0% | 20.0% | 0.0% | 10.0% |
| Ambíguas / variações ortográficas | 34.1% | 44.7% | 39.0% | 14.6% |
| Fora do domínio (recusa) | 100.0% | 100.0% | 100.0% | 100.0% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|---|
| `keyword` | 60 | 0.895 | 0.792 | 0.739 | 0.333 |
| `scale` | 51 | 0.640 | 0.771 | 0.828 | 0.455 |
| `productType` | 42 | 0.774 | 0.734 | 0.815 | 0.636 |
| `state` | 57 | 0.757 | 0.871 | 0.765 | 0.500 |
| `city` | 15 | 0.750 | 1.000 | 0.923 | 0.500 |
| `supplyArea` | 51 | 0.938 | 0.851 | 1.000 | 0.300 |
| `project` | 15 | 0.833 | 0.909 | 0.800 | 0.000 |
| `publicationPeriod` | 42 | 0.593 | 0.353 | 0.600 | 0.526 |
| `creationPeriod` | 6 | 0.000 | 0.667 | 0.667 | 0.000 |
| `sortField` | 30 | 0.500 | 0.462 | 0.182 | 0.353 |
| `sortDirection` | 30 | 0.500 | 0.462 | 0.462 | 0.133 |
| `limit` | 18 | 0.556 | 0.571 | 0.571 | 0.600 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| P | 45.5% | 43.9% | 40.9% | 9.1% |
| N | 51.4% | 55.9% | 51.4% | 29.7% |
| G | 66.7% | 75.0% | 66.7% | 25.0% |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 51, 'valor_errado': 15, 'campo_inventado': 12, 'nao_chamou': 21, 'campo_omitido': 3}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.742, 'creationPeriod': 0.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 21
- observacionais: 12 casos, acurácia 0.0%, chamou sem dever 6
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E4B

- tipos de erro: {'valor_errado': 21, 'misto': 12, 'campo_omitido': 4, 'campo_inventado': 9, 'nao_chamou': 49}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 1.0, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 49
- observacionais: 12 casos, acurácia 50.0%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E2B

- tipos de erro: {'campo_omitido': 12, 'campo_inventado': 15, 'valor_errado': 21, 'misto': 30, 'nao_chamou': 27}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.743, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 27
- observacionais: 12 casos, acurácia 75.0%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Mistral Nemo 12B

- tipos de erro: {'nao_chamou': 141, 'campo_omitido': 3, 'campo_inventado': 12, 'valor_errado': 6, 'misto': 3}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.825}
- chamadas com erro: 0 {}
- não chamou quando devia: 141
- observacionais: 12 casos, acurácia 50.0%, chamou sem dever 0
- thinking desativado: False · Ollama 0.34.4 · repetições [1, 2, 3]

