# Estatística

## Acurácia com IC 95% (Wilson)

| Modelo | acertos / n | acurácia | IC 95% |
|---|---|---|---|
| Qwen 3.8 27B (Groq) | 291 / 306 | 95.1% | 92.1–97.0% |
| GPT-OSS 20B (Groq) | 273 / 306 | 89.2% | 85.2–92.2% |
| GPT-OSS 120B (Groq) | 275 / 306 | 89.9% | 86.0–92.8% |

IC com n = número de consultas (as repetições de uma consulta não são independentes).

## McNemar pareado (uma observação por consulta: maioria das repetições)

| Modelo A | Modelo B | só A acerta | só B acerta | p-valor exato |
|---|---|---|---|---|
| Qwen 3.8 27B (Groq) | GPT-OSS 20B (Groq) | 28 | 10 | 0.0051 |
| Qwen 3.8 27B (Groq) | GPT-OSS 120B (Groq) | 24 | 8 | 0.0070 |
| GPT-OSS 20B (Groq) | GPT-OSS 120B (Groq) | 21 | 23 | 0.8804 |

Leitura: p < 0,05 indica que a diferença de acurácia entre os dois modelos, sobre as mesmas consultas, dificilmente é obra do acaso. Cada consulta entra uma vez, com o resultado da maioria das suas repetições.
