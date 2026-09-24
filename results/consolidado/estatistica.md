# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 111 / 213 | 52.1% | 45.4–58.7% |
| Gemma 4 E4B | 118 / 213 | 55.4% | 48.7–61.9% |
| Gemma 4 E2B | 108 / 213 | 50.7% | 44.0–57.3% |
| Mistral Nemo 12B | 48 / 213 | 22.5% | 17.4–28.6% |

## McNemar pareado (mesmas consultas × repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E4B | 30 | 37 | 0.4638 |
| Qwen 3 4B | Gemma 4 E2B | 24 | 21 | 0.7660 |
| Qwen 3 4B | Mistral Nemo 12B | 63 | 0 | 0.0000 |
| Gemma 4 E4B | Gemma 4 E2B | 26 | 16 | 0.1641 |
| Gemma 4 E4B | Mistral Nemo 12B | 82 | 12 | 0.0000 |
| Gemma 4 E2B | Mistral Nemo 12B | 69 | 9 | 0.0000 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares independentes — é uma aproximação, declarada como tal no texto.
