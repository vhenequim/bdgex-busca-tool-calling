"""Gera notebooks/lote2_v3_colab.ipynb: a rodada de TESTE da v3 no lote 2 (Gemma 4 E4B, T4).

    python scripts/v3/gerar_notebook_lote2.py

Pré-registro: o caderno grava o SHA-256 da configuração v3 congelada (prompts, ferramentas, código e
dados das ferramentas: `v3.texto_hash`) e se recusa a rodar se o pacote tiver outra v3. Os hashes
dos datasets são gravados por `scripts/empacotar_colab.py`.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "scripts" / "lote_validacao"))

from gerar_notebook import CEL_OLLAMA, _celula  # noqa: E402

from pfc_busca import v3  # noqa: E402

DESTINO = RAIZ / "notebooks" / "lote2_v3_colab.ipynb"

# ordem: primeiro a comparação principal (v3 × controle), depois o que a arquitetura em duas etapas simulada
# precisa (tc2 e se1), depois os degraus que faltam e as outras referências; por fim, as 310 (desenvolvimento)
RODADAS = [
    ("tool_calling_v3", "lote2"), ("saida_estruturada_v3", "lote2"), ("tool_calling_v2", "lote2"),
    ("saida_estruturada", "lote2"), ("tool_calling_v3a", "lote2"), ("tool_calling_v3d", "lote2"),
    ("tool_calling", "lote2"), ("saida_estruturada_v2", "lote2"),
    ("tool_calling_v3", "base"), ("saida_estruturada_v3", "base"),
]


def main() -> None:
    v3_sha = {a: hashlib.sha256(v3.texto_hash(a).encode("utf-8")).hexdigest() for a in v3.ABORDAGENS_V3}
    md_inicio = """# PFC · Teste da v3 no lote 2 (Colab)

Rodada de **teste** da v3, no **lote 2** (945 consultas novas, construídas como o lote 1, com outra semente, outros redatores e outros anotadores; nenhuma delas foi usada no desenvolvimento da v3). Um modelo, o Gemma 4 E4B, na T4. Metodologia em `docs/v3.md`.

Os degraus do Tool Calling, cada um acrescentando uma peça ao anterior:

| Degrau | Configuração | O que acrescenta |
|---|---|---|
| 0 | TC v1 | a solução do Cap. 4 |
| 1 | TC v2 | descrições com as convenções do manual + ferramenta de recusa |
| 2 | TC v3 descrições | descrições corrigidas com os erros do lote 1 |
| 3 | TC v3 + ferramentas auxiliares | identificar_nome, normalizar_codigo, normalizar_escala, resolver_periodo e pedir_esclarecimento (usuário simulado) |
| 4 | **TC v3** | + retorno: a busca confere os parâmetros e devolve erros e avisos; a recusa de consulta com critério do catálogo volta uma vez |
| controle | **SE v3** | as mesmas descrições e o mesmo retorno, como nova tentativa, sem Tool Calling |
| referências | SE v1, SE v2 | já medidas no lote 1; TC v2 + SE v1 formam a arquitetura em duas etapas simulada |

**Pré-registro:** a célula 3 confere que a v3 do pacote é exatamente a congelada antes do teste (SHA-256 abaixo). Leva cerca de 2 h 30 min; deixe a aba aberta. Se a sessão cair, `Executar tudo` de novo: o avaliador retoma. A célula 5 grava um zip parcial ao fim de cada rodada.

> Nenhum serviço de LLM em nuvem é usado: o Ollama roda dentro desta máquina virtual."""
    cel_config = f"""# 1) Configuração — NÃO altere depois de começar
MODELO = 'gemma4:e4b-it-qat'
HOJE_LOTE = '2026-09-24'
HOJE_310 = '2026-09-14'
DATASET_SHA256 = ''    # gravado por scripts/empacotar_colab.py
LOTE_SHA256 = ''       # gravado por scripts/empacotar_colab.py
LOTE2_SHA256 = ''      # gravado por scripts/empacotar_colab.py
V3_SHA256 = {json.dumps(v3_sha, indent=1)}   # pré-registro da v3 (scripts/v3/gerar_notebook_lote2.py)
!nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
"""
    cel_pacote = """# 3) Envia o pacote, confere datasets e a v3 congelada, instala
import os, hashlib, shutil, datetime
from google.colab import files

def sha(caminho):
    p = '/content/pfc_busca/' + caminho
    return hashlib.sha256(open(p, 'rb').read()).hexdigest() if os.path.exists(p) else None

def pacote_atual():
    return (sha('data/dataset.json') == DATASET_SHA256 and sha('data/lote_validacao.json') == LOTE_SHA256
            and sha('data/lote_validacao_2.json') == LOTE2_SHA256)

if os.path.exists('/content/pfc_busca') and not pacote_atual():
    antigo = '/content/pfc_busca_anterior_' + datetime.datetime.now().strftime('%H%M%S')
    shutil.move('/content/pfc_busca', antigo)
    print('pacote anterior movido para', antigo)
if not os.path.exists('/content/pfc_busca/pyproject.toml'):
    enviado = files.upload()
    nome = next(iter(enviado))
    !unzip -q -o "$nome" -d /content
assert pacote_atual(), 'O zip enviado NÃO é o pacote atual (hashes dos datasets). Baixe de novo dist/pfc_busca_colab.zip.'
%cd /content/pfc_busca
!pip install -q -e . 2>&1 | tail -2
import subprocess, json as _json
atual = _json.loads(subprocess.run(['python', '-c', 'import hashlib, json; from pfc_busca import v3; print(json.dumps({a: hashlib.sha256(v3.texto_hash(a).encode()).hexdigest() for a in v3.ABORDAGENS_V3}))'],
                                   capture_output=True, text=True).stdout)
assert atual == V3_SHA256, 'A v3 do pacote NÃO é a pré-registrada. Não rode: o teste perderia o valor.'
print('datasets e v3 conferidos (pré-registro ok)')
!python -m pytest -q tests/test_v3.py 2>&1 | tail -2
"""
    cel_modelo = """# 4) Baixa o modelo (~6 GB)
!ollama pull {MODELO} 2>&1 | tail -1
!ollama list
"""
    rodadas = ",\n    ".join(f"({a!r}, {c!r})" for a, c in RODADAS)
    cel_rodadas = f"""# 5) Rodadas (uma repetição cada)
import datetime, re, subprocess
from google.colab import files

CONJUNTOS = {{'lote2': ('data/lote_validacao_2.json', 'results/lote2', HOJE_LOTE),
             'base': (None, 'results/v3_310', HOJE_310)}}

def rodar(abordagem, conjunto):
    dataset, saida, hoje = CONJUNTOS[conjunto]
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
                print(f'   [{{n}}] {{linha}}', flush=True)
        elif linha.strip() and not linha.startswith('avaliando'):
            print(linha, flush=True)
    return proc.wait()

def baixar_parcial():
    !cd /content && rm -f lote2_v3_colab.zip && zip -q -r lote2_v3_colab.zip pfc_busca/results/lote2 pfc_busca/results/v3_310 2>/dev/null; ls -la lote2_v3_colab.zip

rodadas = [
    {rodadas},
]
for abordagem, conjunto in rodadas:
    print(f'\\n== {{abordagem}} · {{conjunto}} == início {{datetime.datetime.now():%H:%M}}', flush=True)
    codigo = rodar(abordagem, conjunto)
    print(f'   saída {{codigo}} às {{datetime.datetime.now():%H:%M}}', flush=True)
    baixar_parcial()
"""
    cel_final = """# 6) Confere e baixa o resultado final
!python -m pfc_busca.evaluation.conferencia results/lote2/* results/v3_310/* 2>&1 | grep -v consolidado
baixar_parcial()
files.download('/content/lote2_v3_colab.zip')
"""
    md_fim = """## De volta ao PC

Descompacte `lote2_v3_colab.zip` na pasta que contém `pfc_busca/` (as rodadas vão para `pfc_busca/results/lote2/` e `pfc_busca/results/v3_310/`) e gere as tabelas com `python -m pfc_busca.evaluation.lote --paper ../paper_revisado`."""
    nb = {"cells": [_celula("markdown", md_inicio), _celula("code", cel_config), _celula("code", CEL_OLLAMA),
                    _celula("code", cel_pacote), _celula("code", cel_modelo), _celula("code", cel_rodadas),
                    _celula("code", cel_final), _celula("markdown", md_fim)],
          "metadata": {"accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []},
                       "kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 0}
    DESTINO.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(DESTINO.relative_to(RAIZ), "· v3 tc3", v3_sha["tool_calling_v3"][:12])


if __name__ == "__main__":
    main()
