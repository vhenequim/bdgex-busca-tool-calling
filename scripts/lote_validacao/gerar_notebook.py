"""Gera notebooks/lote_validacao_colab.ipynb (rodadas do lote de validação na T4 do Colab).

    python scripts/lote_validacao/gerar_notebook.py

Os hashes do dataset das 310 e do lote são gravados depois por `scripts/empacotar_colab.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DESTINO = RAIZ / "notebooks" / "lote_validacao_colab.ipynb"

MD_INICIO = """# PFC · Lote de validação independente (Colab)

Roda o **mesmo** `pfc-avaliar`, na **mesma** GPU T4 das rodadas completas, com **um** modelo — o Gemma 4 E4B, o de maior acurácia com Tool Calling nas 310 consultas — em quatro configurações:

| Configuração | O que é |
|---|---|
| Tool Calling v1 | a solução do Cap. 4, sem mudança |
| Saída Estruturada v1 | a linha de base da seção 5.3 |
| Tool Calling v2 | descrições dos parâmetros com as convenções do manual, ferramenta `recusar_consulta` e proibição de pedir esclarecimento |
| Saída Estruturada v2 | a mesma especificação v2, com o campo `fora_do_escopo` para recusar |

Dois conjuntos: o **lote de validação** (`data/lote_validacao.json`, consultas novas, redigidas a partir de alvos sorteados de catálogos reais e confirmadas por anotação às cegas; metodologia em `docs/lote_validacao.md`) nas quatro configurações, e as **310 consultas** só nas duas v2 (a v1 nas 310 já foi rodada).

Uma repetição por configuração (temperatura zero). **Antes de começar:** `Ambiente de execução → Alterar tipo de ambiente de execução → T4 GPU`, depois `Executar tudo`. A célula 3 pede o arquivo `pfc_busca_colab.zip`. São cerca de 8.300 chamadas ao modelo (1.929 consultas do lote × 4 configurações + 310 × 2); leva cerca de 2 h. Deixe a aba aberta.

> Nenhum serviço de LLM em nuvem é usado: o Ollama roda dentro desta máquina virtual. Só a GPU é alugada.

**Se a sessão cair no meio:** `Executar tudo` de novo; o avaliador pula o que já foi feito enquanto a pasta `results/` existir. A célula 5 baixa um zip parcial ao fim de cada rodada, para não perder o que já rodou."""

CEL_CONFIG = """# 1) Configuração — NÃO altere depois de começar
MODELO = 'gemma4:e4b-it-qat'
HOJE_310 = '2026-09-14'    # a mesma data de referência das rodadas v1 nas 310 (T4)
HOJE_LOTE = '2026-09-24'   # a data de referência da anotação às cegas do lote
DATASET_SHA256 = ''   # gravado por scripts/empacotar_colab.py
LOTE_SHA256 = ''      # gravado por scripts/empacotar_colab.py
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
"""

CEL_OLLAMA = """# 2) Instala o Ollama (precisa de zstd) e sobe o servidor
!apt-get -qq update > /dev/null 2>&1 && apt-get -qq install -y zstd pciutils > /dev/null 2>&1 && echo "zstd instalado"
!curl -fsSL https://ollama.com/install.sh | sh 2>&1 | tail -3

import os, shutil, subprocess, time, json, urllib.request
assert shutil.which('ollama'), 'o Ollama NÃO foi instalado — veja as mensagens acima'
servidor = subprocess.Popen(['ollama', 'serve'], stdout=open('/content/ollama.log', 'w'), stderr=subprocess.STDOUT,
                            env=dict(os.environ, OLLAMA_KEEP_ALIVE='30m'))
for _ in range(40):
    try:
        v = json.load(urllib.request.urlopen('http://127.0.0.1:11434/api/version', timeout=3))['version']
        print('Ollama', v, 'no ar')
        break
    except Exception:
        time.sleep(2)
else:
    raise RuntimeError('o servidor do Ollama não subiu — veja /content/ollama.log')
"""

CEL_PACOTE = """# 3) Envia o repositório (pfc_busca_colab.zip), confere os dois datasets e instala o pacote
import os, hashlib, shutil, datetime
from google.colab import files

def sha(caminho):
    p = '/content/pfc_busca/' + caminho
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None

def pacote_atual():
    return sha('data/dataset.json') == DATASET_SHA256 and sha('data/lote_validacao.json') == LOTE_SHA256

if os.path.exists('/content/pfc_busca') and not pacote_atual():
    antigo = '/content/pfc_busca_anterior_' + datetime.datetime.now().strftime('%H%M%S')
    shutil.move('/content/pfc_busca', antigo)
    print('pacote anterior movido para', antigo, '(não será usado)')
if not os.path.exists('/content/pfc_busca/pyproject.toml'):
    enviado = files.upload()
    nome = next(iter(enviado))
    !unzip -q -o "$nome" -d /content
assert pacote_atual(), 'O zip enviado NÃO é o pacote atual (os hashes não conferem). Baixe de novo dist/pfc_busca_colab.zip.'
print('datasets conferidos:', DATASET_SHA256[:12], LOTE_SHA256[:12])
%cd /content/pfc_busca
!pip install -q -e . 2>&1 | tail -2
!python -c "from pfc_busca.evaluation.dataset_builder import carregar_dataset as c; from pathlib import Path; print(len(c()), 'consultas nas 310;', len(c(Path('data/lote_validacao.json'))), 'no lote')"
!python -m pytest -q tests/test_lote_validacao.py 2>&1 | tail -2
"""

CEL_MODELO = """# 4) Baixa o modelo (~10 GB)
!ollama pull {MODELO} 2>&1 | tail -1
!ollama list
"""

CEL_RODADAS = """# 5) Rodadas: lote (4 configurações) e 310 (as duas v2), 1 repetição cada
import datetime, re, subprocess
from google.colab import files

def rodar(abordagem, dataset, saida, hoje):
    cmd = ['pfc-avaliar', '--modelo', MODELO, '--abordagem', abordagem, '--repeticoes', '1', '--hoje', hoje,
           '--sem-sql', '--saida', saida] + (['--dataset', dataset] if dataset else [])
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                            env=dict(os.environ, COLUMNS='110'))
    n = 0
    for linha in proc.stdout:
        linha = linha.rstrip()
        if re.match(r'^[✓·×] r\\d', linha):
            n += 1
            if linha.startswith('×') or n % 100 == 0:
                print(f'   [{n}] {linha}', flush=True)
        elif linha.strip() and not linha.startswith('avaliando'):
            print(linha, flush=True)
    return proc.wait()

def baixar_parcial():
    !cd /content && rm -f lote_validacao_colab.zip && zip -q -r lote_validacao_colab.zip pfc_busca/results/lote pfc_busca/results/v2_310 2>/dev/null; ls -la lote_validacao_colab.zip

rodadas = [
    ('tool_calling', 'data/lote_validacao.json', 'results/lote', HOJE_LOTE),
    ('saida_estruturada', 'data/lote_validacao.json', 'results/lote', HOJE_LOTE),
    ('tool_calling_v2', 'data/lote_validacao.json', 'results/lote', HOJE_LOTE),
    ('saida_estruturada_v2', 'data/lote_validacao.json', 'results/lote', HOJE_LOTE),
    ('tool_calling_v2', None, 'results/v2_310', HOJE_310),
    ('saida_estruturada_v2', None, 'results/v2_310', HOJE_310),
]
for abordagem, dataset, saida, hoje in rodadas:
    print(f'\\n== {abordagem} · {dataset or "310 consultas"} == início {datetime.datetime.now():%H:%M}', flush=True)
    codigo = rodar(abordagem, dataset, saida, hoje)
    print(f'   saída {codigo} às {datetime.datetime.now():%H:%M}', flush=True)
    baixar_parcial()
"""

CEL_FINAL = """# 6) Confere e baixa o resultado final
!python -m pfc_busca.evaluation.conferencia results/lote/* results/v2_310/* 2>&1 | grep -v consolidado
baixar_parcial()
files.download('/content/lote_validacao_colab.zip')
"""

MD_FIM = """## De volta ao PC

Descompacte `lote_validacao_colab.zip` na pasta que contém `pfc_busca/` (as rodadas vão para `pfc_busca/results/lote/` e `pfc_busca/results/v2_310/`) e gere tabelas e macros com `python -m pfc_busca.evaluation.lote --paper ../paper_revisado`."""


def _celula(tipo: str, fonte: str) -> dict:
    c = {"cell_type": tipo, "metadata": {}, "source": fonte.strip("\n").splitlines(keepends=True)}
    if tipo == "code":
        c.update(execution_count=None, outputs=[])
    return c


def main() -> None:
    nb = {"cells": [_celula("markdown", MD_INICIO), _celula("code", CEL_CONFIG), _celula("code", CEL_OLLAMA),
                    _celula("code", CEL_PACOTE), _celula("code", CEL_MODELO), _celula("code", CEL_RODADAS),
                    _celula("code", CEL_FINAL), _celula("markdown", MD_FIM)],
          "metadata": {"accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []},
                       "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    DESTINO.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"{DESTINO.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
