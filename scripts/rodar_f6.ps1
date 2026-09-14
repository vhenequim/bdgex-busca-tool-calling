# Rodada F6: todos os modelos, em sequência, com a MESMA data de referência.
#
#   .\scripts\rodar_f6.ps1                       # 4 modelos x 3 repetições
#   .\scripts\rodar_f6.ps1 -Repeticoes 1         # rodada rápida
#   .\scripts\rodar_f6.ps1 -Modelos qwen3:4b     # um modelo só
#
# Retomável: se cair no meio, rode o mesmo comando com o MESMO -Hoje que
# aparece no log (o avaliador pula o que já foi feito).
param(
    [string[]]$Modelos = @("qwen3:4b-instruct-2507-q4_K_M", "gemma4:e4b-it-qat", "gemma4:e2b-it-qat", "mistral-nemo:12b"),
    [int]$Repeticoes = 3,
    [string]$Hoje = (Get-Date -Format "yyyy-MM-dd"),
    [switch]$SemSql
)

$ErrorActionPreference = "Continue"
Set-Location (Join-Path $PSScriptRoot "..")
New-Item -ItemType Directory -Force -Path results | Out-Null
$log = "results\f6_$(Get-Date -Format 'yyyyMMdd_HHmm').log"

function Registrar($texto) { $texto | Tee-Object -FilePath $log -Append }

Registrar "== F6 iniciada em $(Get-Date -Format 'yyyy-MM-dd HH:mm') | hoje=$Hoje | repeticoes=$Repeticoes | modelos=$($Modelos -join ', ')"

# Pré-voo: VRAM livre e servidor
$vram = & nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader 2>$null
Registrar "VRAM (usada, livre): $vram"
try { $v = (Invoke-RestMethod -Uri "http://localhost:11434/api/version" -TimeoutSec 5).version; Registrar "Ollama servidor $v" }
catch { Registrar "ERRO: Ollama não responde em localhost:11434 — abra o Ollama e rode de novo."; exit 2 }

$extra = @()
if ($SemSql) { $extra += "--sem-sql" }

foreach ($m in $Modelos) {
    Registrar ""
    Registrar "== $m == $(Get-Date -Format 'HH:mm:ss')"
    & .\.venv\Scripts\pfc-avaliar.exe --modelo $m --repeticoes $Repeticoes --hoje $Hoje @extra 2>&1 | Tee-Object -FilePath $log -Append
    Registrar "saída $LASTEXITCODE em $(Get-Date -Format 'HH:mm:ss')"
    # libera a VRAM antes do próximo modelo
    & ollama stop $m 2>$null
}

Registrar ""
Registrar "== consolidando =="
& .\.venv\Scripts\pfc-relatorio.exe --modelos ($Modelos -join ",") 2>&1 | Tee-Object -FilePath $log -Append
Registrar "== F6 encerrada em $(Get-Date -Format 'yyyy-MM-dd HH:mm') =="
