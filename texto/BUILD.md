# Como compilar o texto do PFC

Todos os comandos abaixo são executados **de dentro da pasta do texto** (no repositório,
`texto/`).

## Pré-requisitos

- **TeX Live 2022+** (Linux/macOS) ou **MiKTeX 2023+** (Windows), com `tikz`, `enumitem`,
  `longtable`, `multirow`, `hyperref` e o Babel `brazilian` (`texlive-lang-portuguese` no
  Linux). As classes abnTeX2 e a personalização do IME já vêm na pasta.
- **Python 3.12+**, só para `build.py` ou para regerar tabelas e figuras.

## Compilação

Sequência canônica do abnTeX2:

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Ou pelos scripts, que fazem o mesmo e reportam referências e citações indefinidas:

```bash
python build.py            # multiplataforma; --clean, --quick, --open
./build.sh                 # Linux / macOS / WSL
.\build.ps1                # Windows (PowerShell)
```

`python build.py --online` envia o projeto para o serviço latexonline.cc; sem essa opção,
a compilação é sempre local.

## Tabelas, figuras e números do texto

As tabelas de `tabelas/`, as figuras de `figuras/` e os valores citados na prosa
(`tabelas/numeros*.tex`, macros `\res{...}`) são gerados a partir de `data/` e `results/` do
repositório, com, na raiz do repositório:

```bash
python scripts/gerar_tabelas_texto.py --texto texto
```

Nenhum número de resultado é digitado à mão.

## Estrutura

```
main.tex                  arquivo principal
dados.tex                 título, autores, orientador, data e banca
pre-texto.tex             dedicatória, resumo e abstract
simbolo-abrev.tex         lista de abreviaturas e siglas
cap01-introducao.tex ... cap06-conclusao.tex
apendice.tex              Apêndices A (dataset e auditoria), B (ambientes) e C (repositório)
apendice_manual_anotacao.tex, apendice_dataset_P.tex, apendice_dataset_N.tex,
apendice_dataset_gerado.tex   gerados por pfc-dataset --apendice
tabelas/, figuras/        gerados (ver acima)
refs.bib                  referências
abntex2.cls, abntex2cite.sty, abntex2ime.sty   classes (não editar)
build.py, build.sh, build.ps1                  scripts de compilação
```

## Problemas comuns

- **"Unknown option 'brazil'"**: instale o pacote de português do LaTeX
  (`texlive-lang-portuguese`) ou use a instalação completa do MiKTeX.
- **"File `abntex2.cls' not found"**: rode a compilação de dentro da pasta do texto.
- **Sumário ou referências com "??"**: rode a sequência completa (com `bibtex` e duas passadas
  finais de `pdflatex`).
