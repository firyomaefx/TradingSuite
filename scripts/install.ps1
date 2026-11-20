# Mirror JevScalper install: copy TradingSuite MQL5 tree into terminal DataPath.
param(
    [Parameter(Mandatory = $true)]
    [string]$DataPath
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent
$data = (Resolve-Path $DataPath).Path
$src = Join-Path $repo "MQL5"
$dst = Join-Path $data "MQL5"

function Copy-Tree($rel) {
    $from = Join-Path $src $rel
    $to = Join-Path $dst $rel
    if (Test-Path $from) {
        New-Item -ItemType Directory -Force -Path (Split-Path $to -Parent) | Out-Null
        Copy-Item -Path $from -Destination $to -Recurse -Force
    }
}

Copy-Tree "Experts\TradingSuite"
Copy-Tree "Include\TradingSuite"
Write-Host "OK: TradingSuite copied to $dst"