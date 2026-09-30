#!/usr/bin/env bash
# Latência da v3 na estação de referência (RTX 3050, 4 GB): as 62 consultas P e N, como as rodadas de
# results/estacao/ da v1 (mesma data de referência, sem SQL, uma repetição). Rodar com o PC ocioso.
#
#     bash scripts/v3/rodar_estacao_v3.sh
#
# Cada rodada começa descarregando os modelos residentes no Ollama (o pfc-avaliar faz isso e registra a VRAM
# livre no manifesto). A acurácia nas 62 consultas é de desenvolvimento (dentro da amostra); o objetivo é a
# latência no hardware modesto: v3 e controle com o Gemma 4 E2B (o modelo recomendado para GPU modesta) e
# v1, v3 e controle com o Gemma 4 E4B, que não fora medido na estação.
set -u
cd "$(dirname "$0")/../.."
AVALIAR=".venv/Scripts/pfc-avaliar.exe"
[ -x "$AVALIAR" ] || AVALIAR="pfc-avaliar"
RODADAS=(
  "gemma4:e2b-it-qat tool_calling_v3"
  "gemma4:e2b-it-qat saida_estruturada_v3"
  "gemma4:e4b-it-qat tool_calling"
  "gemma4:e4b-it-qat saida_estruturada"
  "gemma4:e4b-it-qat tool_calling_v3"
  "gemma4:e4b-it-qat saida_estruturada_v3"
)
for r in "${RODADAS[@]}"; do
  set -- $r
  echo "== $1 · $2 · $(date +%H:%M:%S)"
  PYTHONIOENCODING=utf-8 "$AVALIAR" --modelo "$1" --abordagem "$2" --origem P,N --hoje 2026-09-14 \
    --sem-sql --repeticoes 1 --saida results/estacao 2>&1 | grep -E "^[✓·×] r|rro|Traceback|→" | tail -3
done
echo "fim $(date +%H:%M:%S)"
