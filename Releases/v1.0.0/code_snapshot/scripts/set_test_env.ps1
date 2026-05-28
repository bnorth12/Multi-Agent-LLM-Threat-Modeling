Param(
    [switch]$EnableVisibleBrowserTests = $true
)

$ErrorActionPreference = "Stop"

# Enforce UTF-8 output/input behavior for Python logging and subprocess pipes.
$env:PYTHONIOENCODING = "utf-8"

if ($EnableVisibleBrowserTests) {
    $env:RUN_VISIBLE_BROWSER_TESTS = "1"
}

$hasGrokApi = -not [string]::IsNullOrWhiteSpace($env:GROK_API)
$hasGrokApiKey = -not [string]::IsNullOrWhiteSpace($env:GROK_API_KEY)

if (-not ($hasGrokApi -or $hasGrokApiKey)) {
    Write-Host "[TEST ENV] GROK_API/GROK_API_KEY is not currently set in this shell." -ForegroundColor Yellow
    Write-Host "[TEST ENV] Browser E2E smoke will fail fast until one of these is set." -ForegroundColor Yellow
} else {
    Write-Host "[TEST ENV] GROK API credential detected for browser E2E tests." -ForegroundColor Green
}

Write-Host "[TEST ENV] PYTHONIOENCODING=utf-8" -ForegroundColor Green
Write-Host "[TEST ENV] RUN_VISIBLE_BROWSER_TESTS=$($env:RUN_VISIBLE_BROWSER_TESTS)" -ForegroundColor Green
Write-Host "[TEST ENV] Environment configured for test execution." -ForegroundColor Green
