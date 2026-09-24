# Comparativo entre modelos

| Modelo | n | Acurácia | IC 95% (Wilson) | Precisão | Recall | F1 pond. | F1 macro | Lat. mediana (ms) | Lat. p95 (ms) | Erros infra |
|---|---|---|---|---|---|---|---|---|---|---|
| Qwen 3 4B | 891 | 43.8% | 40.5–47.0% | 0.645 | 0.711 | 0.623 | 0.521 | 1044 | 1824 | 0 |
| Gemma 4 E4B | 891 | 50.4% | 47.1–53.7% | 0.775 | 0.683 | 0.709 | 0.643 | 745 | 1306 | 0 |
| Gemma 4 E2B | 891 | 46.9% | 43.7–50.2% | 0.720 | 0.631 | 0.636 | 0.594 | 404 | 729 | 0 |
| Mistral Nemo 12B | 891 | 23.6% | 20.9–26.5% | 0.696 | 0.351 | 0.448 | 0.370 | 2739 | 7433 | 0 |

## F1 ponderado por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 0.650 | 0.853 | 0.806 | 0.534 |
| Compostas | 0.623 | 0.723 | 0.646 | 0.436 |
| Com código MI/INOM | 0.934 | 0.865 | 0.927 | 0.390 |
| Com referência temporal relativa | 0.555 | 0.360 | 0.392 | 0.415 |
| Com ordenação | 0.631 | 0.533 | 0.435 | 0.492 |
| Ambíguas / variações ortográficas | 0.589 | 0.695 | 0.613 | 0.449 |

## Acurácia por categoria

| Categoria | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| Simples | 66.7% | 78.1% | 77.0% | 40.0% |
| Compostas | 34.2% | 42.4% | 38.0% | 17.4% |
| Com código MI/INOM | 87.7% | 75.4% | 84.2% | 29.8% |
| Com referência temporal relativa | 24.6% | 6.0% | 8.2% | 8.2% |
| Com ordenação | 10.3% | 6.9% | 0.0% | 10.3% |
| Ambíguas / variações ortográficas | 33.8% | 43.8% | 40.7% | 18.5% |

## F1 por campo

| Campo | Ocorr. | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|---|
| `keyword` | 186 | 0.720 | 0.848 | 0.637 | 0.506 |
| `scale` | 249 | 0.605 | 0.883 | 0.823 | 0.434 |
| `productType` | 129 | 0.548 | 0.579 | 0.769 | 0.479 |
| `state` | 390 | 0.794 | 0.848 | 0.691 | 0.541 |
| `city` | 78 | 0.424 | 0.916 | 0.809 | 0.650 |
| `supplyArea` | 120 | 0.974 | 0.855 | 0.974 | 0.481 |
| `project` | 33 | 0.714 | 0.732 | 0.833 | 0.000 |
| `publicationPeriod` | 177 | 0.440 | 0.116 | 0.203 | 0.338 |
| `creationPeriod` | 9 | 0.000 | 0.231 | 0.286 | 0.000 |
| `sortField` | 87 | 0.250 | 0.460 | 0.242 | 0.222 |
| `sortDirection` | 87 | 0.444 | 0.662 | 0.343 | 0.345 |
| `limit` | 51 | 0.333 | 0.583 | 0.522 | 0.450 |

## Acurácia por origem do caso

| Origem | Qwen 3 4B | Gemma 4 E4B | Gemma 4 E2B | Mistral Nemo 12B |
|---|---|---|---|---|
| P | 40.9% | 37.9% | 40.9% | 9.1% |
| N | 47.1% | 54.9% | 50.0% | 23.5% |
| G | 43.6% | 50.9% | 47.0% | 24.9% |

## Diagnósticos

### Qwen 3 4B

- tipos de erro: {'misto': 279, 'valor_errado': 78, 'campo_inventado': 87, 'nao_chamou': 48, 'campo_omitido': 9}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.736, 'creationPeriod': 0.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 48
- observacionais: 39 casos, acurácia 53.8%, chamou sem dever 9
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E4B

- tipos de erro: {'valor_errado': 94, 'misto': 87, 'campo_omitido': 7, 'campo_inventado': 86, 'nao_chamou': 168}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.788, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 168
- observacionais: 39 casos, acurácia 69.2%, chamou sem dever 0
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Gemma 4 E2B

- tipos de erro: {'misto': 244, 'campo_inventado': 27, 'valor_errado': 66, 'nao_chamou': 115, 'campo_omitido': 21}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.873, 'creationPeriod': 1.0}
- chamadas com erro: 0 {}
- não chamou quando devia: 115
- observacionais: 39 casos, acurácia 69.2%, chamou sem dever 3
- thinking desativado: True · Ollama 0.34.4 · repetições [1, 2, 3]

### Mistral Nemo 12B

- tipos de erro: {'nao_chamou': 501, 'campo_omitido': 12, 'campo_inventado': 78, 'valor_errado': 51, 'misto': 39}
- campos fora do schema: {}
- IoU médio de períodos: {'publicationPeriod': 0.784}
- chamadas com erro: 0 {}
- não chamou quando devia: 501
- observacionais: 39 casos, acurácia 69.2%, chamou sem dever 0
- thinking desativado: False · Ollama 0.34.4 · repetições [1, 2, 3]

