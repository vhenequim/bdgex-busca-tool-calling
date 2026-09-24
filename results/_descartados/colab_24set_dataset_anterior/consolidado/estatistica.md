# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 390 / 891 | 43.8% | 40.5–47.0% |
| Gemma 4 E4B | 449 / 891 | 50.4% | 47.1–53.7% |
| Gemma 4 E2B | 418 / 891 | 46.9% | 43.7–50.2% |
| Mistral Nemo 12B | 210 / 891 | 23.6% | 20.9–26.5% |

## McNemar pareado (mesmas consultas × repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E4B | 88 | 147 | 0.0001 |
| Qwen 3 4B | Gemma 4 E2B | 96 | 124 | 0.0685 |
| Qwen 3 4B | Mistral Nemo 12B | 249 | 69 | 0.0000 |
| Gemma 4 E4B | Gemma 4 E2B | 111 | 80 | 0.0297 |
| Gemma 4 E4B | Mistral Nemo 12B | 300 | 61 | 0.0000 |
| Gemma 4 E2B | Mistral Nemo 12B | 260 | 52 | 0.0000 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares independentes — é uma aproximação, declarada como tal no texto.
