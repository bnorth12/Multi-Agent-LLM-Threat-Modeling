param(
    [string]$Sprint = "2026_12",
    [string]$PolicyProfile = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$pythonBin = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonBin)) {
    $pythonBin = "python"
}

$args = @(
    "scripts/governance_autoflow.py",
    "--context", "closeout",
    "--sprint", $Sprint
)
if ($PolicyProfile) {
    $args += @("--policy-profile", $PolicyProfile)
}

& $pythonBin @args
exit $LASTEXITCODE
