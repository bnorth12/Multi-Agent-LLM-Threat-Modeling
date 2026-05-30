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
Write-Host "Pre-commit and pre-merge-commit will now run archive hygiene checks and governance autoflow."
Write-Host "Pre-push will now run unit tests, sprint traceability checks, archive hygiene,"
Write-Host "cross-domain exception policy validation, and governance autoflow before push."
Write-Host "Governance routing is loaded from config/governance_autoflow_routing.json."
Write-Host "Governance execution ledger is written under independent_reviews/latest and independent_reviews/history."
Write-Host ""
Write-Host "Env toggles:"
Write-Host " - TRACEABILITY_ENFORCE=1 makes traceability check blocking"
Write-Host " - ARCHIVE_HYGIENE_ENFORCE=0 makes archive hygiene check warning-only on pre-push"
Write-Host " - EXCEPTION_POLICY_ENFORCE=0 makes exception policy check warning-only"
Write-Host " - Sprint defaults are centralized in config/sprint_defaults.env"
Write-Host " - INDEPENDENT_REVIEW_SPRINT and TRACEABILITY_SPRINT accept YYYY-NN, YYYY_NN, YYYY-NNN, or YYYY_NNN"
Write-Host "   Default sprint now comes from config/sprint_defaults.env (DEFAULT_SPRINT=2026_013)"
Write-Host " - INDEPENDENT_REVIEW_PROFILE manually overrides profile selection (options: strict/default/advisory)"
Write-Host "   If unset, hooks auto-select strict on main/release/* and default otherwise"
Write-Host " - INDEPENDENT_REVIEW_HOOK_FAIL_MODE=warn downgrades profile blocking to warning-only"
Write-Host ""
Write-Host "Operator commands:"
Write-Host " - .\scripts\run_governance_planning.ps1 -Sprint 2026_013"
Write-Host " - .\scripts\run_governance_closeout.ps1 -Sprint 2026_013"
