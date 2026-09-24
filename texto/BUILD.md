# Como compilar o PFC

## Pré-requisitos

- **TeX Live 2022+** (Linux/macOS) ou **MiKTeX 2023+** (Windows) — deve incluir os pacotes:
  - `abntex2` (classe base do IME)
  - `tikz`, `enumitem`, `float`, `hyperref` (já vêm no *full install*)
  - `texlive-lang-portuguese` (Linux) — para o Babel `brazilian`
- **Python 3.11+** (só se for regerar o dataset via `--dataset`)

## Uso rápido

### Python (multiplataforma, recomendado)

```bash
python build.py                # local se tiver LaTeX; fallback online (latexonline.cc)
python build.py --clean        # limpa artefatos antes
python build.py --quick        # 1 passada só (sem bibtex)
python build.py --dataset      # regera o apêndice antes
python build.py --online       # força compilação online (não precisa de LaTeX local)
python build.py --open         # abre o PDF ao final
```

Para o modo `--online`, instale a dependência opcional uma única vez:
```bash
pip install -r requirements-build.txt
```

### Windows (PowerShell)

```powershell
cd paper_revisado
.\build.ps1                # build normal
.\build.ps1 -Open          # compila e abre o PDF
.\build.ps1 -Clean         # limpa e recompila do zero
.\build.ps1 -Quick         # só 1 passada de pdflatex (sem bibtex — mais rápido)
.\build.ps1 -Dataset       # regera o apêndice do dataset antes de compilar
```

Se der erro de política de execução, rode uma vez:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Linux / macOS / WSL

```bash
cd paper_revisado
./build.sh                 # build normal
./build.sh --open          # compila e abre
./build.sh --clean         # limpa e recompila do zero
./build.sh --quick         # só 1 passada
./build.sh --dataset       # regera o apêndice
```

## O que o script faz

1. **Verifica** que `pdflatex` e `bibtex` estão no PATH.
2. **(Opcional)** Roda `python generate_dataset.py` para regerar `apendice_dataset_gerado.tex`.
3. **(Opcional)** Limpa artefatos (`*.aux`, `*.log`, `*.toc`, `*.bbl`…).
4. Roda a sequência canônica de compilação **abntex2**:
   - `pdflatex main.tex` (gera `.aux` inicial)
   - `bibtex main` (resolve referências bibliográficas)
   - `pdflatex main.tex` (integra a bibliografia)
   - `pdflatex main.tex` (resolve *cross-references*, sumário, LOF/LOT)
5. **Reporta**:
   - PDF gerado (nome, tamanho, número de páginas)
   - Referências indefinidas (`\ref{}` quebrado)
   - Citações indefinidas (`\cite{}` sem entrada no `.bib`)
   - Contagem de *Overfull hboxes* (linhas longas — só estético)

## Estrutura de arquivos

```
paper_revisado/
├── main.tex                        # arquivo principal (entry point)
├── dados.tex                       # metadados (título, autores, orientador)
├── pre-texto.tex                   # resumo, abstract
├── simbolo-abrev.tex               # lista de abreviaturas
├── cap01-introducao.tex
├── cap02-referencial.tex
├── cap03-metodologia.tex
├── cap04-aprimoramento.tex
├── cap05-resultados.tex            # (desativado — só será preenchido após F6)
├── cap06-conclusao.tex             # (desativado)
├── apendice.tex                    # Apêndices A (dataset) e B (specs de HW)
├── apendice_dataset_gerado.tex     # \input{}-ado por apendice.tex
├── refs.bib                        # referências bibliográficas
├── abntex2.cls                     # classe (não editar)
├── abntex2ime.sty                  # personalização IME (não editar)
├── abntex2cite.sty                 # citações ABNT (não editar)
├── generate_dataset.py             # regerador programático do dataset
├── images/                         # figuras (poucas — quase tudo é TikZ)
├── build.ps1                       # compilador PowerShell (Windows)
├── build.sh                        # compilador Bash (Linux/Mac/WSL)
└── BUILD.md                        # este arquivo
```

## Troubleshooting

### "! Package babel Error: Unknown option 'brazil'"
Instale o pacote de português: `sudo apt install texlive-lang-portuguese` (Ubuntu/Debian) ou reinstale MiKTeX com *full install*.

### "! LaTeX Error: File `abntex2.cls' not found"
O arquivo já vem no repositório. Confirme que está rodando o script **de dentro** do diretório `paper_revisado/`.

### PDF gerado, mas sumário/referências aparecem como "??"
Normal na 1ª compilação. Rode o script novamente — ou use `--clean` e depois build normal.

### "Reference `algo' undefined on input line X"
Você tem `\ref{algo}` mas nenhum `\label{algo}`. Confira no capítulo mencionado.

### "Citation `xxx' undefined"
`\cite{xxx}` não bate com nenhuma entrada de `refs.bib`. Confira grafia.
