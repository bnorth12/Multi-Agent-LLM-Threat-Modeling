param(
    [string]$Sprint = "",
    [string]$PolicyProfile = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$defaultSprint = if ($env:INDEPENDENT_REVIEW_SPRINT) { $env:INDEPENDENT_REVIEW_SPRINT } elseif ($env:DEFAULT_SPRINT) { $env:DEFAULT_SPRINT } else { "2026_013" }
if ([string]::IsNullOrWhiteSpace($Sprint)) {
    $Sprint = $defaultSprint
}

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
