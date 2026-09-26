# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 918 | 54.2% | 48.6–59.7% | 0.697 | 0.743 | 0.666 | 0.599 | 828 | 1403 | 0 |
| Gemma 4 E4B | 918 | 60.2% | 54.7–65.6% | 0.853 | 0.763 | 0.793 | 0.741 | 725 | 1230 | 0 |
| Gemma 4 E2B | 918 | 56.5% | 50.9–62.0% | 0.821 | 0.760 | 0.765 | 0.744 | 397 | 703 | 0 |
| Mistral Nemo 12B | 918 | 26.8% | 22.1–32.0% | 0.804 | 0.326 | 0.451 | 0.420 | 2391 | 5860 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 0.691 | 0.874 | 0.844 | 0.443 |
| Compostas | 0.654 | 0.794 | 0.763 | 0.431 |
| Com código MI/INOM | 0.949 | 0.878 | 0.929 | 0.362 |
| Com referência temporal relativa | 0.725 | 0.547 | 0.645 | 0.450 |
| Com ordenação | 0.775 | 0.650 | 0.691 | 0.530 |
| Ambíguas / variações ortográficas | 0.640 | 0.825 | 0.744 | 0.429 |

## Acurácia por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 74.0% | 77.3% | 79.0% | 32.0% |
| Compostas | 39.4% | 53.1% | 47.8% | 20.0% |
| Com código MI/INOM | 91.2% | 77.2% | 78.9% | 21.1% |
| Com referência temporal relativa | 48.3% | 25.6% | 21.7% | 16.7% |
| Com ordenação | 41.4% | 35.6% | 20.7% | 24.1% |
| Ambíguas / variações ortográficas | 44.2% | 56.9% | 51.3% | 19.8% |
| Fora do domínio (recusa) | 100.0% | 100.0% | 62.5% | 100.0% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|---|
| `keyword` | 186 | 0.776 | 0.883 | 0.713 | 0.430 |
| `scale` | 252 | 0.526 | 0.875 | 0.841 | 0.415 |
| `productType` | 132 | 0.684 | 0.635 | 0.871 | 0.554 |
| `state` | 390 | 0.818 | 0.920 | 0.795 | 0.489 |
| `city` | 81 | 0.412 | 1.000 | 0.892 | 0.667 |
| `supplyArea` | 120 | 0.950 | 0.897 | 0.947 | 0.431 |
| `project` | 33 | 0.541 | 0.806 | 0.909 | 0.000 |
| `publicationPeriod` | 153 | 0.693 | 0.424 | 0.548 | 0.455 |
| `creationPeriod` | 30 | 0.625 | 0.378 | 0.429 | 0.462 |
| `sortField` | 87 | 0.400 | 0.641 | 0.513 | 0.377 |
| `sortDirection` | 87 | 0.400 | 0.641 | 0.651 | 0.314 |
| `limit` | 42 | 0.358 | 0.794 | 0.824 | 0.444 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| P | 45.5% | 37.9% | 40.9% | 9.1% |
| N | 51.4% | 55.9% | 51.4% | 29.7% |
| G | 55.5% | 62.9% | 58.7% | 27.9% |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 291, 'valor_errado': 33, 'campo_inventado': 48, 'nao_chamou': 39, 'campo_omitido': 9}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.819, 'creationPeriod': 0.833}
- chamadas com erro: 0 {}
- não chamou quando devia: 39
- observacionais: 12 casos, acurácia 0.0%, chamou sem dever 6
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E4B

- tipos de erro: {'valor_errado': 96, 'misto': 22, 'campo_omitido': 7, 'campo_inventado': 79, 'nao_chamou': 161}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.667, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 161
- observacionais: 12 casos, acurácia 50.0%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E2B

- tipos de erro: {'campo_omitido': 42, 'campo_inventado': 24, 'valor_errado': 87, 'misto': 150, 'nao_chamou': 87, 'chamou_sem_dever': 9}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.844, 'creationPeriod': 0.875}
- chamadas com erro: 0 {}
- não chamou quando devia: 87
- observacionais: 12 casos, acurácia 75.0%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Mistral Nemo 12B

- tipos de erro: {'nao_chamou': 561, 'campo_omitido': 18, 'campo_inventado': 48, 'valor_errado': 27, 'misto': 18}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.897, 'creationPeriod': 0.936}
- chamadas com erro: 0 {}
- não chamou quando devia: 561
- observacionais: 12 casos, acurácia 50.0%, chamou sem dever 0
- thinking desativado: False · Ollama 0.34.4 · repetições [1, 2, 3]

