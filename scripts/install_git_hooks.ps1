param(
    [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

$hooksPath = ".githooks"
$prePushHook = Join-Path $repoRoot ".githooks\pre-push"

if (-not (Test-Path $prePushHook)) {
    throw "Missing pre-push hook at '$prePushHook'."
}

$currentHooksPath = git config --local --get core.hooksPath 2>$null
if ($Force -or [string]::IsNullOrWhiteSpace($currentHooksPath) -or $currentHooksPath -ne $hooksPath) {
    git config --local core.hooksPath $hooksPath
}

Write-Host "Git hooks path configured: $hooksPath"
Write-Host "Installed hooks:"
Get-ChildItem (Join-Path $repoRoot ".githooks") -File | ForEach-Object {
    Write-Host " - $($_.Name)"
}

Write-Host ""
Write-Host "Hook install complete."
Write-Host "Pre-commit and pre-merge-commit will now run archive hygiene checks."
Write-Host "Pre-push will now run unit tests, sprint traceability checks, archive hygiene,"
Write-Host "and cross-domain exception policy validation before push."
Write-Host ""
Write-Host "Env toggles:"
Write-Host " - TRACEABILITY_ENFORCE=1 makes traceability check blocking"
Write-Host " - ARCHIVE_HYGIENE_ENFORCE=0 makes archive hygiene check warning-only on pre-push"
Write-Host " - EXCEPTION_POLICY_ENFORCE=0 makes exception policy check warning-only"
