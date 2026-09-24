#!/usr/bin/env bash
# build.sh — Compila o PFC (LaTeX) para PDF
# Uso:
#   ./build.sh            # build normal (pdflatex + bibtex + pdflatex x2)
#   ./build.sh --quick    # sem bibtex (só 1 passada de pdflatex)
#   ./build.sh --clean    # remove artefatos e recompila do zero
#   ./build.sh --open     # abre o PDF ao final
#   ./build.sh --dataset  # regera o apêndice antes de compilar

set -euo pipefail
cd "$(dirname "$0")"

MAIN=main
MAIN_TEX="$MAIN.tex"
MAIN_PDF="$MAIN.pdf"

QUICK=0; CLEAN=0; OPEN=0; DATASET=0
for arg in "$@"; do
    case "$arg" in
        --quick|-q)    QUICK=1 ;;
        --clean|-c)    CLEAN=1 ;;
        --open|-o)     OPEN=1  ;;
        --dataset|-d)  DATASET=1 ;;
        --help|-h)
            head -12 "$0"; exit 0 ;;
        *) echo "Opção desconhecida: $arg" >&2; exit 1 ;;
    esac
done

CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; RED='\033[0;31m'; NC='\033[0m'
step() { echo -e "\n${CYAN}[--] $1${NC}"; }
ok()   { echo -e "${GREEN}[OK] $1${NC}"; }
warn() { echo -e "${YELLOW}[!!] $1${NC}"; }
err()  { echo -e "${RED}[XX] $1${NC}"; }

# ---- deps ----
step "Verificando dependências"
command -v pdflatex >/dev/null || { err "pdflatex não encontrado. Instale TeX Live."; exit 1; }
command -v bibtex   >/dev/null || warn "bibtex não encontrado. Referências podem não resolver."
ok "$(pdflatex --version | head -1)"

# ---- dataset (opcional) ----
if [ "$DATASET" = 1 ]; then
    step "Regerando dataset"
    if command -v python3 >/dev/null; then
        python3 generate_dataset.py
    elif command -v python >/dev/null; then
        python generate_dataset.py
    else
        err "python não encontrado."; exit 1
    fi
    if [ -f /tmp/apendice_gerado.tex ]; then
        cp /tmp/apendice_gerado.tex apendice_dataset_gerado.tex
        ok "Dataset regerado em apendice_dataset_gerado.tex"
    fi
fi

# ---- clean ----
if [ "$CLEAN" = 1 ]; then
    step "Limpando artefatos"
    rm -f *.aux *.log *.toc *.lof *.lot *.loq *.out *.bbl *.blg *.bcf *.run.xml \
          *.idx *.ilg *.ind *.synctex.gz *.fdb_latexmk *.fls
    ok "Artefatos removidos"
fi

FLAGS=(-interaction=nonstopmode -file-line-error)

step "1ª passada — pdflatex"
pdflatex "${FLAGS[@]}" "$MAIN_TEX" >/tmp/build.log 2>&1 || true
if [ ! -f "$MAIN.aux" ]; then
    err "1ª passada falhou. Últimas 40 linhas:"
    tail -40 "$MAIN.log"; exit 1
fi
ok "1ª passada concluída"

if [ "$QUICK" = 0 ]; then
    if command -v bibtex >/dev/null; then
        step "bibtex"
        bibtex "$MAIN" 2>&1 | grep -Ei "warning|error|no file" || true
        ok "bibtex concluído"
    fi
    step "2ª passada — pdflatex"
    pdflatex "${FLAGS[@]}" "$MAIN_TEX" >>/tmp/build.log 2>&1 || true
    ok "2ª passada concluída"
    step "3ª passada — pdflatex (resolvendo cross-refs)"
    pdflatex "${FLAGS[@]}" "$MAIN_TEX" >>/tmp/build.log 2>&1 || true
    ok "3ª passada concluída"
fi

# ---- resumo ----
if [ -f "$MAIN_PDF" ]; then
    size=$(du -k "$MAIN_PDF" | cut -f1)
    pages=$(grep -oE "Output written on $MAIN\.pdf \([0-9]+ pages" "$MAIN.log" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "?")
    echo ""
    ok "PDF gerado: $MAIN_PDF (${size} KB, ${pages} páginas)"

    undef=$(grep -c "Reference.*undefined" "$MAIN.log" 2>/dev/null || echo 0)
    [ "$undef" -gt 0 ] && warn "$undef referências indefinidas (\\ref{})"
    missing=$(grep -c "Citation.*undefined" "$MAIN.log" 2>/dev/null || echo 0)
    [ "$missing" -gt 0 ] && warn "$missing citações indefinidas (verificar .bib)"
    over=$(grep -c "Overfull \\\\hbox" "$MAIN.log" 2>/dev/null || echo 0)
    [ "$over" -gt 0 ] && warn "$over overfull hboxes (só estético)"

    if [ "$OPEN" = 1 ]; then
        step "Abrindo o PDF"
        if [ "$(uname)" = "Darwin" ]; then open "$MAIN_PDF"
        elif command -v xdg-open >/dev/null; then xdg-open "$MAIN_PDF" &>/dev/null &
        elif command -v start >/dev/null; then start "$MAIN_PDF"
        else warn "Não consegui detectar como abrir o PDF neste sistema."
        fi
    fi
else
    err "PDF não gerado. Últimas 40 linhas do log:"
    tail -40 "$MAIN.log"; exit 1
fi
