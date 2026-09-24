#Requires -Version 5.1
<#
    build.ps1 — Compila o PFC (LaTeX) para PDF
    Uso:
        .\build.ps1              # build normal (pdflatex + bibtex + pdflatex x2)
        .\build.ps1 -Quick       # sem bibtex (só 1 passada de pdflatex)
        .\build.ps1 -Clean       # remove artefatos e recompila do zero
        .\build.ps1 -Open        # abre o PDF ao final
        .\build.ps1 -Dataset     # regera o apêndice antes de compilar

    Requer: TeX Live ou MiKTeX, com o pacote `abntex2` instalado.
#>

[CmdletBinding()]
param(
    [switch]$Quick,
    [switch]$Clean,
    [switch]$Open,
    [switch]$Dataset
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

$MAIN = "main"
$MAIN_TEX = "$MAIN.tex"
$MAIN_PDF = "$MAIN.pdf"

function Write-Step($msg) {
    Write-Host ""
    Write-Host "[--] $msg" -ForegroundColor Cyan
}

function Write-OK($msg)   { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!!] $msg" -ForegroundColor Yellow }
function Write-Err($msg)  { Write-Host "[XX] $msg" -ForegroundColor Red }

function Test-Command($cmd) {
    $null = Get-Command $cmd -ErrorAction SilentlyContinue
    return $?
}

# --------- Pré-requisitos ---------
Write-Step "Verificando dependências"
if (-not (Test-Command "pdflatex")) {
    Write-Err "pdflatex não encontrado. Instale TeX Live ou MiKTeX e reabra o PowerShell."
    exit 1
}
if (-not (Test-Command "bibtex")) {
    Write-Warn "bibtex não encontrado. Referências podem não resolver."
}
Write-OK "pdflatex: $(pdflatex --version | Select-Object -First 1)"

# --------- Dataset opcional ---------
if ($Dataset) {
    Write-Step "Regerando apêndice do dataset (generate_dataset.py)"
    if (-not (Test-Command "python") -and -not (Test-Command "python3")) {
        Write-Err "python não encontrado."
        exit 1
    }
    $py = if (Test-Command "python") { "python" } else { "python3" }
    & $py "generate_dataset.py"
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Falha ao rodar generate_dataset.py"
        exit 1
    }
    # O script escreve /tmp/apendice_gerado.tex por padrão; copiar
    if (Test-Path "/tmp/apendice_gerado.tex") {
        Copy-Item "/tmp/apendice_gerado.tex" "apendice_dataset_gerado.tex" -Force
        Write-OK "Dataset regerado em apendice_dataset_gerado.tex"
    }
}

# --------- Clean ---------
if ($Clean) {
    Write-Step "Limpando artefatos"
    $exts = @("aux","log","toc","lof","lot","loq","out","bbl","blg","bcf","run.xml","idx","ilg","ind","synctex.gz","fdb_latexmk","fls")
    foreach ($ext in $exts) {
        Get-ChildItem -Filter "*.$ext" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
    }
    Write-OK "Artefatos removidos"
}

# --------- Build ---------
$pdflatexFlags = @("-interaction=nonstopmode", "-file-line-error")

Write-Step "1ª passada — pdflatex"
& pdflatex @pdflatexFlags $MAIN_TEX 2>&1 | Out-Null

if ($LASTEXITCODE -ne 0 -and -not (Test-Path "$MAIN.aux")) {
    Write-Err "pdflatex falhou na 1ª passada. Verifique $MAIN.log"
    Get-Content "$MAIN.log" -Tail 40
    exit 1
}
Write-OK "1ª passada concluída"

if (-not $Quick) {
    if (Test-Command "bibtex") {
        Write-Step "bibtex — resolvendo referências"
        & bibtex $MAIN 2>&1 | ForEach-Object {
            if ($_ -match "^(Warning|I found no)") { Write-Warn $_ }
            elseif ($_ -match "error") { Write-Err $_ }
        }
        # bibtex retorna 1 quando há warnings; não é fatal
        Write-OK "bibtex concluído"
    }

    Write-Step "2ª passada — pdflatex"
    & pdflatex @pdflatexFlags $MAIN_TEX 2>&1 | Out-Null
    Write-OK "2ª passada concluída"

    Write-Step "3ª passada — pdflatex (resolvendo cross-refs)"
    & pdflatex @pdflatexFlags $MAIN_TEX 2>&1 | Out-Null
    Write-OK "3ª passada concluída"
}

# --------- Resumo ---------
if (Test-Path $MAIN_PDF) {
    $size = [math]::Round((Get-Item $MAIN_PDF).Length / 1KB, 1)
    $pages = 0
    try {
        $log = Get-Content "$MAIN.log" -Raw
        if ($log -match "Output written on $MAIN\.pdf \((\d+) pages") {
            $pages = $matches[1]
        }
    } catch {}

    Write-Host ""
    Write-OK "PDF gerado: $MAIN_PDF ($size KB, $pages páginas)"

    # avisos comuns
    $warns = @()
    if ((Select-String -Path "$MAIN.log" -Pattern "Reference.*undefined" -SimpleMatch).Count -gt 0) {
        $undef = (Select-String -Path "$MAIN.log" -Pattern "Reference.*undefined" -SimpleMatch).Count
        $warns += "$undef referências indefinidas (verifique \ref{})"
    }
    if ((Select-String -Path "$MAIN.log" -Pattern "Citation.*undefined" -SimpleMatch).Count -gt 0) {
        $missing = (Select-String -Path "$MAIN.log" -Pattern "Citation.*undefined" -SimpleMatch).Count
        $warns += "$missing citações indefinidas (verifique .bib)"
    }
    if ((Select-String -Path "$MAIN.log" -Pattern "Overfull \\hbox" -SimpleMatch).Count -gt 0) {
        $over = (Select-String -Path "$MAIN.log" -Pattern "Overfull \\hbox" -SimpleMatch).Count
        $warns += "$over overfull hboxes (linhas longas — só estético)"
    }
    foreach ($w in $warns) { Write-Warn $w }

    if ($Open) {
        Write-Step "Abrindo o PDF"
        Start-Process $MAIN_PDF
    }
} else {
    Write-Err "PDF não foi gerado. Últimas 40 linhas do log:"
    Get-Content "$MAIN.log" -Tail 40
    exit 1
}
