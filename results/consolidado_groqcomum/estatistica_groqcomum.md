# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| GPT-OSS 20B (Groq) | 58 / 71 | 81.7% | 71.2–89.0% |
| GPT-OSS 120B (Groq) | 55 / 71 | 77.5% | 66.5–85.6% |

## McNemar pareado (mesmas consultas × repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) | 8 | 5 | 0.5811 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Repetições do mesmo modelo entram como pares independentes — é uma aproximação, declarada como tal no texto.
