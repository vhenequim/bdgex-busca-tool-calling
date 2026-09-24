"""Copia as fontes do texto do PFC para texto/, a pasta publicada com o repositório.

    python scripts/sincronizar_texto.py                       # origem padrão: ../paper_revisado
    python scripts/sincronizar_texto.py --origem <pasta-do-texto>

A pasta de trabalho do texto continua fora do repositório; esta cópia leva só o que é
fonte ou resultado final: .tex, .bib, classes e estilos, scripts de compilação, tabelas e
figuras geradas e o main.pdf. Artefatos de compilação (.aux, .log, .toc, .synctex...) e
pastas de arquivo (nomes iniciados por "_") ficam de fora. Arquivos que deixaram de
existir na origem são removidos da cópia.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "texto"
EXTENSOES_RAIZ = {".tex", ".bib", ".cls", ".sty", ".md", ".py", ".ps1", ".sh", ".txt"}
SUBPASTAS = {"tabelas": {".tex"}, "figuras": {".pdf"}, "images": {".pdf", ".png", ".jpg", ".jpeg", ".eps"}}
EXTRAS = {"main.pdf"}


def selecionar(origem: Path) -> list[Path]:
    arquivos = [f for f in origem.iterdir()
                if f.is_file() and (f.suffix.lower() in EXTENSOES_RAIZ or f.name in EXTRAS)]
    for pasta, exts in SUBPASTAS.items():
        if (origem / pasta).is_dir():
            arquivos += [f for f in (origem / pasta).iterdir() if f.is_file() and f.suffix.lower() in exts]
    return sorted(arquivos)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--origem", type=Path, default=RAIZ.parent / "paper_revisado")
    args = p.parse_args()
    origem = args.origem.resolve()
    if not (origem / "main.tex").exists():
        raise SystemExit(f"{origem} não parece ser a pasta do texto (sem main.tex)")
    selecionados = selecionar(origem)
    relativos = {f.relative_to(origem) for f in selecionados}
    copiados = 0
    for f in selecionados:
        alvo = DESTINO / f.relative_to(origem)
        alvo.parent.mkdir(parents=True, exist_ok=True)
        if not alvo.exists() or alvo.read_bytes() != f.read_bytes():
            shutil.copy2(f, alvo)
            copiados += 1
    removidos = 0
    if DESTINO.exists():
        for f in DESTINO.rglob("*"):
            if f.is_file() and f.relative_to(DESTINO) not in relativos:
                f.unlink()
                removidos += 1
    print(f"texto/: {len(selecionados)} arquivos ({copiados} atualizados, {removidos} removidos) a partir de {origem}")


if __name__ == "__main__":
    main()
