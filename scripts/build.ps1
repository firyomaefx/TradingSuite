param(
    [Parameter(Mandatory = $true)]
    [string]$DataPath,
    [string]$MetaEditor = ""
)

$ErrorActionPreference = "Stop"
$repo = Split-Path $PSScriptRoot -Parent
$data = (Resolve-Path $DataPath).Path

if (-not $MetaEditor) {
    $candidates = @(
        "C:\Program Files\Mtrading MetaTrader 5\MetaEditor64.exe",
        "C:\Program Files\MetaTrader 5\MetaEditor64.exe"
    )
    $MetaEditor = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
if (-not $MetaEditor -or -not (Test-Path $MetaEditor)) {
    throw "MetaEditor64.exe not found. Pass -MetaEditor <path>."
}

& (Join-Path $PSScriptRoot "install.ps1") -DataPath $data
$src = Join-Path $data "MQL5\Experts\TradingSuite\TradingSuiteCore.mq5"
$log = Join-Path $data "MQL5\Experts\TradingSuite\compile.log"
if (Test-Path $log) { Remove-Item $log -Force }

$proc = Start-Process -FilePath $MetaEditor -ArgumentList @("/compile:$src", "/log:$log") -Wait -PassThru -WindowStyle Hidden
for ($i = 0; $i -lt 30; $i++) {
    if ((Test-Path $log) -and ((Get-Content $log -Raw) -match "Result:")) { break }
    Start-Sleep -Seconds 1
}
if (-not (Test-Path $log)) { throw "Compile log missing" }
$text = Get-Content $log -Raw
if ($text -notmatch "Result:\s*0 errors") { throw "Compile failed: $log" }

$version = (Get-Content (Join-Path $repo "VERSION") -Raw).Trim()
$dist = Join-Path $repo "dist"
New-Item -ItemType Directory -Force -Path $dist | Out-Null
Copy-Item (Join-Path $data "MQL5\Experts\TradingSuite\TradingSuiteCore.ex5") (Join-Path $dist "TradingSuiteCore_$version.ex5") -Force
Write-Host "OK: dist\TradingSuiteCore_$version.ex5"