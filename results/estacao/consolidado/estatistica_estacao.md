# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3 4B | 29 / 59 | 49.2% | 36.8–61.6% |
| Gemma 4 E2B | 28 / 59 | 47.5% | 35.3–60.0% |

## McNemar pareado (mesmas consultas × repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3 4B | Gemma 4 E2B | 8 | 7 | 1.0000 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares independentes — é uma aproximação, declarada como tal no texto.
