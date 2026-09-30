"""Gera dist/pfc_busca_colab.zip para as rodadas completas no Colab.

    python scripts/empacotar_colab.py

Antes de empacotar, grava nos notebooks (célula 1) o hash SHA-256 do data/dataset.json
vigente e, no notebook do lote, também o do data/lote_validacao.json: o notebook se recusa
a rodar com um pacote cujos datasets não sejam esses, o que impede reaproveitar por engano
um zip antigo.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
NOTEBOOKS = [RAIZ / "notebooks" / "avaliacao_colab.ipynb", RAIZ / "notebooks" / "linha_de_base_colab.ipynb",
             RAIZ / "notebooks" / "lote_validacao_colab.ipynb", RAIZ / "notebooks" / "lote2_v3_colab.ipynb",
             RAIZ / "notebooks" / "lote2_v3_modelos_colab.ipynb"]
INCLUIR = ["src", "tests", "scripts", "db", "notebooks", "docs", "data/dataset.json", "data/auditoria",
           "data/lote_validacao.json", "data/lote_validacao_2.json",
           "pyproject.toml", "README.md", ".env.example", ".gitignore", "docker-compose.yml"]


def gravar_hash_no_notebook(sha: str, sha_lote: str | None = None, sha_lote2: str | None = None) -> None:
    for notebook in NOTEBOOKS:
        if notebook.exists():
            _gravar_hash(notebook, {"DATASET_SHA256": sha, "LOTE_SHA256": sha_lote, "LOTE2_SHA256": sha_lote2})


def _gravar_hash(notebook: Path, hashes: dict[str, str | None]) -> None:
    nb = json.loads(notebook.read_text(encoding="utf-8"))
    alterou = False
    for celula in nb["cells"]:
        fonte = "".join(celula["source"])
        nova = fonte
        for nome, valor in hashes.items():
            if valor and f"{nome} =" in nova:
                nova = re.sub(nome + r" = '[0-9a-f]*'", f"{nome} = '{valor}'", nova)
        if nova != fonte:
            alterou = True
            celula["source"] = nova.splitlines(keepends=True)
    if alterou:
        notebook.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    sha = hashlib.sha256((RAIZ / "data" / "dataset.json").read_bytes()).hexdigest()
    lote = RAIZ / "data" / "lote_validacao.json"
    sha_lote = hashlib.sha256(lote.read_bytes()).hexdigest() if lote.exists() else None
    lote2 = RAIZ / "data" / "lote_validacao_2.json"
    sha_lote2 = hashlib.sha256(lote2.read_bytes()).hexdigest() if lote2.exists() else None
    gravar_hash_no_notebook(sha, sha_lote, sha_lote2)
    arquivos = []
    for item in INCLUIR:
        p = RAIZ / item
        if p.is_file():
            arquivos.append(p)
        elif p.is_dir():
            arquivos += [f for f in p.rglob("*")
                         if f.is_file() and "__pycache__" not in f.parts and f.suffix != ".pyc"]
    destino = RAIZ / "dist" / "pfc_busca_colab.zip"
    destino.parent.mkdir(exist_ok=True)
    import subprocess
    commit = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True, check=False).stdout.strip()
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(arquivos):
            z.write(f, "pfc_busca/" + f.relative_to(RAIZ).as_posix())
        if commit:
            z.writestr("pfc_busca/VERSAO", commit + "\n")
    print(f"{destino.relative_to(RAIZ)}: {len(arquivos)} arquivos, {destino.stat().st_size // 1024} KB; "
          f"dataset {sha[:12]}" + (f"; lote {sha_lote[:12]}" if sha_lote else ""))


if __name__ == "__main__":
    main()
