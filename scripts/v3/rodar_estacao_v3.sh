#!/usr/bin/env bash
# Latência na estação de referência (RTX 3050, 4 GB): as 62 consultas P e N, como as rodadas de
# results/estacao/ da v1 (mesma data de referência, sem SQL, uma repetição). Rodar com o PC ocioso.
#
#     bash scripts/v3/rodar_estacao_v3.sh                         # as seis rodadas de 30/09 (E2B e E4B)
#     bash scripts/v3/rodar_estacao_v3.sh qwen3:4b-instruct-2507-q4_K_M:saida_estruturada_v3 ...   # outras
#
# Cada argumento é modelo:abordagem (o modelo pode ter ':' na tag; a abordagem é o que vem depois do último ':').
# Cada rodada começa descarregando os modelos residentes no Ollama (o avaliador faz isso e registra a VRAM
# livre no manifesto). A acurácia nas 62 consultas é de desenvolvimento (dentro da amostra); o objetivo é a
# latência no hardware modesto. Se o Ollama não estiver no ar, o script o inicia e o encerra no fim.
set -u
cd "$(dirname "$0")/../.."
PY=".venv/Scripts/python.exe"
[ -x "$PY" ] || PY="python"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"   # não depende do pacote instalado
if [ "$#" -gt 0 ]; then
  RODADAS=("$@")
else
  RODADAS=(
    "gemma4:e2b-it-qat:tool_calling_v3"
    "gemma4:e2b-it-qat:saida_estruturada_v3"
    "gemma4:e4b-it-qat:tool_calling"
    "gemma4:e4b-it-qat:saida_estruturada"
    "gemma4:e4b-it-qat:tool_calling_v3"
    "gemma4:e4b-it-qat:saida_estruturada_v3"
  )
fi
INICIOU_OLLAMA=""
if ! ollama list > /dev/null 2>&1; then
  ollama serve > /dev/null 2>&1 &
  INICIOU_OLLAMA=$!
  for _ in $(seq 1 30); do ollama list > /dev/null 2>&1 && break; sleep 2; done
fi
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader 2>/dev/null | sed 's/^/VRAM em uso no início: /'
for r in "${RODADAS[@]}"; do
  modelo="${r%:*}"
  abordagem="${r##*:}"
  echo "== $modelo · $abordagem · $(date +%H:%M:%S)"
  PYTHONIOENCODING=utf-8 "$PY" -m pfc_busca.evaluation.run_evaluation --modelo "$modelo" --abordagem "$abordagem" \
    --origem P,N --hoje 2026-09-14 --sem-sql --repeticoes 1 --saida results/estacao 2>&1 \
    | grep -E "^[✓·×] r|rro|Traceback|→" | tail -3
done
[ -n "$INICIOU_OLLAMA" ] && kill "$INICIOU_OLLAMA" 2>/dev/null
echo "fim $(date +%H:%M:%S)"
