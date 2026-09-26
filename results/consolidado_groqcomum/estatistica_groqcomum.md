# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| GPT-OSS 20B (Groq) | 273 / 306 | 89.2% | 85.2–92.2% |
| GPT-OSS 120B (Groq) | 275 / 306 | 89.9% | 86.0–92.8% |

IC com n = número de consultas (as repetições de uma consulta não são independentes).

## McNemar pareado (uma observação por consulta: maioria das repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) | 21 | 23 | 0.8804 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Cada consulta entra uma vez, com o resultado da maioria das suas repetições.
