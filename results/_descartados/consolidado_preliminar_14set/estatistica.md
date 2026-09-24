# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 27 / 61 | 44.3% | 32.5–56.7% |
| Gemma 4 E2B | 5 / 13 | 38.5% | 17.7–64.5% |

## McNemar pareado (mesmas consultas × repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E2B | 3 | 0 | 0.2500 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares independentes — é uma aproximação, declarada como tal no texto.
