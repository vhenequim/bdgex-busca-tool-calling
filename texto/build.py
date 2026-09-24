#!/usr/bin/env python3
"""
build.py — Compilador do PFC em Python

Uso:
    python build.py                # tenta pdflatex local; fallback = LaTeX.Online
    python build.py --clean        # limpa antes
    python build.py --quick        # 1 passada só (sem bibtex)
    python build.py --dataset      # regera o apêndice antes
    python build.py --open         # abre o PDF ao final
    python build.py --online       # força uso do compilador online

Não requer PowerShell. Roda em qualquer OS com Python 3.8+.

Compilação local: usa pdflatex/bibtex se disponíveis.
Compilação online: envia o projeto zipado para latexonline.cc (não requer instalação).
"""

from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import sys
import time
import zipfile
import io
import glob
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN = "main"
MAIN_TEX = HERE / f"{MAIN}.tex"
MAIN_PDF = HERE / f"{MAIN}.pdf"
MAIN_LOG = HERE / f"{MAIN}.log"

# ── cores no terminal (ANSI, ignora silenciosamente em terminais sem suporte) ──
class C:
    CYAN = "\033[0;36m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[0;33m"
    RED = "\033[0;31m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def step(msg): print(f"\n{C.CYAN}[--] {msg}{C.RESET}")
def ok(msg):   print(f"{C.GREEN}[OK] {msg}{C.RESET}")
def warn(msg): print(f"{C.YELLOW}[!!] {msg}{C.RESET}")
def err(msg):  print(f"{C.RED}[XX] {msg}{C.RESET}")

MIKTEX_SEARCH_DIRS = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "MiKTeX" / "miktex" / "bin" / "x64",
    Path(r"C:\Program Files\MiKTeX\miktex\bin\x64"),
    Path(r"C:\Program Files (x86)\MiKTeX\miktex\bin\x64"),
]

def find_latex_bin(cmd):
    found = shutil.which(cmd)
    if found:
        return found
    if sys.platform.startswith("win"):
        for d in MIKTEX_SEARCH_DIRS:
            candidate = d / f"{cmd}.exe"
            if candidate.is_file():
                return str(candidate)
        for d in sorted(glob.glob(r"C:\texlive\*\bin\windows"), reverse=True):
            candidate = Path(d) / f"{cmd}.exe"
            if candidate.is_file():
                return str(candidate)
    return None


def install_miktex():
    step("pdflatex não encontrado — tentando instalar MiKTeX via winget")
    winget = shutil.which("winget")
    if not winget:
        warn("winget não disponível; instale MiKTeX manualmente: https://miktex.org/download")
        return False
    r = subprocess.run(
        ["winget", "install", "MiKTeX.MiKTeX",
         "--accept-source-agreements", "--accept-package-agreements"],
        timeout=600,
    )
    if r.returncode != 0:
        warn("winget install falhou; instale manualmente: https://miktex.org/download")
        return False
    ok("MiKTeX instalado — buscando pdflatex novamente")
    return find_latex_bin("pdflatex") is not None

# ── operations ────────────────────────────────────────────────────────────
def run(cmd, capture=True):
    """Roda comando, retorna (returncode, stdout+stderr)."""
    try:
        r = subprocess.run(cmd, cwd=HERE, capture_output=capture, text=True, timeout=180)
        return r.returncode, (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"

def clean_artifacts():
    step("Limpando artefatos")
    exts = ["aux", "log", "toc", "lof", "lot", "loq", "out", "bbl", "blg",
            "bcf", "run.xml", "idx", "ilg", "ind", "synctex.gz",
            "fdb_latexmk", "fls"]
    count = 0
    for ext in exts:
        for f in HERE.glob(f"*.{ext}"):
            f.unlink(); count += 1
    ok(f"{count} arquivos removidos")

def regenerate_dataset():
    step("Regerando apêndice do dataset")
    py = which("python") or which("python3")
    if not py:
        err("python não encontrado"); sys.exit(1)
    r, out = run([py, "generate_dataset.py"], capture=True)
    if r != 0:
        err("generate_dataset.py falhou:"); print(out); sys.exit(1)
    tmp = Path("/tmp/apendice_gerado.tex")
    if tmp.exists():
        shutil.copy(tmp, HERE / "apendice_dataset_gerado.tex")
    ok("dataset regerado")

def local_compile(quick=False, auto_install=True):
    step("Compilação local (pdflatex)")
    pdflatex = find_latex_bin("pdflatex")

    if not pdflatex and auto_install:
        if install_miktex():
            pdflatex = find_latex_bin("pdflatex")

    if not pdflatex:
        return False

    flags = ["-interaction=nonstopmode", "-file-line-error", MAIN_TEX.name]

    ok(f"pdflatex encontrado: {pdflatex}")
    r, out = run([pdflatex] + flags)
    if not (HERE / f"{MAIN}.aux").exists():
        err("1ª passada de pdflatex falhou:")
        print(out[-2000:]); return False
    ok("1ª passada concluída")

    if not quick:
        bibtex = find_latex_bin("bibtex")
        if bibtex:
            step("bibtex")
            run([bibtex, MAIN])
            ok("bibtex concluído")

        step("2ª passada pdflatex")
        run([pdflatex] + flags); ok("OK")

        step("3ª passada pdflatex")
        run([pdflatex] + flags); ok("OK")

    return MAIN_PDF.exists()

def online_compile():
    """Envia projeto para latexonline.cc via requests (se disponível)."""
    step("Compilação online (latexonline.cc)")
    try:
        import requests
    except ImportError:
        err("módulo `requests` não instalado. Instale com: pip install requests")
        return False

    # zipa o diretório
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in HERE.rglob("*"):
            if p.is_file() and not any(
                p.name.endswith(e) for e in (".pdf", ".aux", ".log", ".synctex.gz",
                                              ".bbl", ".blg", ".toc", ".lof", ".lot",
                                              ".out", ".idx", ".ilg", ".ind", ".fls",
                                              ".fdb_latexmk", ".run.xml", ".bcf")
            ):
                zf.write(p, arcname=str(p.relative_to(HERE)))
    buf.seek(0)

    ok(f"upload preparado ({len(buf.getvalue())/1024:.0f} KB)")

    try:
        # latexonline.cc: POST multipart com o zip
        url = "https://latexonline.cc/data"
        r = requests.post(
            url,
            files={"file": ("project.zip", buf.getvalue(), "application/zip")},
            data={"target": MAIN_TEX.name, "compiler": "pdflatex", "force": "true"},
            timeout=180,
        )
        if r.status_code != 200:
            err(f"latexonline.cc retornou HTTP {r.status_code}")
            print(r.text[:2000]); return False
        MAIN_PDF.write_bytes(r.content)
        ok(f"PDF recebido do servidor ({len(r.content)/1024:.0f} KB)")
        return True
    except requests.RequestException as e:
        err(f"erro de rede: {e}"); return False

def report():
    if not MAIN_PDF.exists():
        err("PDF não foi gerado"); return False

    size_kb = MAIN_PDF.stat().st_size / 1024
    pages = "?"
    if MAIN_LOG.exists():
        log = MAIN_LOG.read_text(errors="ignore")
        import re
        m = re.search(rf"Output written on {MAIN}\.pdf \((\d+) pages", log)
        if m: pages = m.group(1)

    ok(f"PDF gerado: {MAIN_PDF.name} ({size_kb:.1f} KB, {pages} páginas)")

    # avisos comuns
    if MAIN_LOG.exists():
        log = MAIN_LOG.read_text(errors="ignore")
        undef = log.count("Reference") and log.count("undefined") - log.count("Citation")
        cites = log.count("Citation") and log.count("undefined")
        if "Reference" in log and "undefined" in log:
            n = len([1 for l in log.split("\n") if "Reference" in l and "undefined" in l])
            if n: warn(f"{n} referências indefinidas (\\ref{{}})")
        if "Citation" in log:
            n = len([1 for l in log.split("\n") if "Citation" in l and "undefined" in l])
            if n: warn(f"{n} citações indefinidas (\\cite{{}})")

    return True

def open_pdf():
    step("Abrindo o PDF")
    if sys.platform.startswith("win"):
        os.startfile(str(MAIN_PDF))  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.call(["open", str(MAIN_PDF)])
    else:
        subprocess.call(["xdg-open", str(MAIN_PDF)])

# ── main ────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--clean", action="store_true", help="limpa antes de compilar")
    ap.add_argument("--quick", action="store_true", help="só 1 passada, sem bibtex")
    ap.add_argument("--dataset", action="store_true", help="regera apêndice do dataset")
    ap.add_argument("--online", action="store_true", help="força compilação online")
    ap.add_argument("--open", action="store_true", help="abre o PDF ao final")
    args = ap.parse_args()

    os.chdir(HERE)

    if args.dataset:
        regenerate_dataset()
    if args.clean:
        clean_artifacts()

    success = False
    if not args.online:
        success = local_compile(quick=args.quick)
        if not success:
            warn("compilação local falhou — tentando online")
    if not success:
        success = online_compile()

    if success:
        report()
        if args.open:
            open_pdf()
        sys.exit(0)
    else:
        err("Não foi possível gerar o PDF.")
        sys.exit(1)

if __name__ == "__main__":
    main()
