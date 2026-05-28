[CmdletBinding()]
param(
    [int]$BackendPort = 8600,
    [int]$FrontendPort = 5173,
    [int]$FrontendAltPort = 5174,
    [int]$TimeoutSeconds = 45,
    [string]$BackendHost = "127.0.0.1",
    [string]$FrontendHost = "127.0.0.1",
    [string]$FrontendDir = "frontend"
)

$ErrorActionPreference = "SilentlyContinue"

$repo = (Get-Location).Path
$frontendPath = Join-Path $repo $FrontendDir
$logDir = Join-Path $repo ".tmp"

if (-not (Test-Path $frontendPath)) {
    Write-Host "ERROR: Frontend directory not found at $frontendPath"
    exit 1
}

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir | Out-Null
}

$backendCombinedLog = Join-Path $logDir "backend.restart.log"
$frontendCombinedLog = Join-Path $logDir "frontend.restart.log"

$backendOut = $backendCombinedLog
$backendErr = $backendCombinedLog
$frontendOut = $frontendCombinedLog
$frontendErr = $frontendCombinedLog

Remove-Item $backendCombinedLog, $frontendCombinedLog -Force -ErrorAction SilentlyContinue

$portsToClear = @($BackendPort, $FrontendPort, $FrontendAltPort)
$listenersBefore = Get-NetTCPConnection -LocalPort $portsToClear -ErrorAction SilentlyContinue |
    Select-Object LocalPort, OwningProcess

$killedPids = @()
foreach ($conn in $listenersBefore) {
    if ($conn.OwningProcess -and ($killedPids -notcontains $conn.OwningProcess)) {
        $killedPids += $conn.OwningProcess
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Milliseconds 750

$env:PYTHONPATH = "src"

$backendCommandPreview = ".\\.venv\\Scripts\\python.exe -m threat_modeler --host $BackendHost --port $BackendPort"
$frontendCommandPreview = "npm.cmd run dev -- --host $FrontendHost --port $FrontendPort --strictPort"

Write-Host "Launching backend command: $backendCommandPreview"
Write-Host "Backend working directory: $repo"
Write-Host "Backend logs: out=$backendOut err=$backendErr"

$backendPowerShellRunner = (
    "& { " +
    "`$env:PYTHONPATH='src'; " +
    "& '.\\.venv\\Scripts\\python.exe' -m threat_modeler --host $BackendHost --port $BackendPort 2>&1 | " +
    "Tee-Object -FilePath '$backendCombinedLog' -Append " +
    "}"
)
$backendCmdArgs = @(
    "/k",
    "title Threat Modeler Backend && cd /d `"$repo`" && echo Launching: $backendCommandPreview && powershell -NoProfile -ExecutionPolicy Bypass -Command `"$backendPowerShellRunner`""
)

$backendStartParams = @{
    FilePath = "cmd.exe"
    ArgumentList = $backendCmdArgs
    WorkingDirectory = $repo
    PassThru = $true
}
$backendProc = Start-Process @backendStartParams

Write-Host "Launching frontend command: $frontendCommandPreview"
Write-Host "Frontend working directory: $frontendPath"
Write-Host "Frontend logs: out=$frontendOut err=$frontendErr"

$frontendPowerShellRunner = (
    "& { " +
    "& npm.cmd run dev -- --host $FrontendHost --port $FrontendPort --strictPort 2>&1 | " +
    "Tee-Object -FilePath '$frontendCombinedLog' -Append " +
    "}"
)
$frontendCmdArgs = @(
    "/k",
    "title Threat Modeler Frontend && cd /d `"$frontendPath`" && echo Launching: $frontendCommandPreview && powershell -NoProfile -ExecutionPolicy Bypass -Command `"$frontendPowerShellRunner`""
)

$frontendStartParams = @{
    FilePath = "cmd.exe"
    ArgumentList = $frontendCmdArgs
    WorkingDirectory = $frontendPath
    PassThru = $true
}
$frontendProc = Start-Process @frontendStartParams

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$backendReady = $false
$frontendReady = $false
$backendReadySeconds = $null
$frontendReadySeconds = $null
$backendStatusCode = $null
$frontendStatusCode = $null

while ($stopwatch.Elapsed.TotalSeconds -lt $TimeoutSeconds) {
    if (-not $backendReady) {
        try {
            $resp = Invoke-WebRequest -Uri ("http://{0}:{1}/health" -f $BackendHost, $BackendPort) -UseBasicParsing -TimeoutSec 2
            $backendStatusCode = [int]$resp.StatusCode
            if ($backendStatusCode -eq 200) {
                $backendReady = $true
                $backendReadySeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
            }
        } catch {
            if ($_.Exception.Response) {
                $backendStatusCode = [int]$_.Exception.Response.StatusCode
            }
        }
    }

    if (-not $frontendReady) {
        try {
            $resp = Invoke-WebRequest -Uri ("http://{0}:{1}/" -f $FrontendHost, $FrontendPort) -UseBasicParsing -TimeoutSec 2
            $frontendStatusCode = [int]$resp.StatusCode
            if ($frontendStatusCode -eq 200) {
                $frontendReady = $true
                $frontendReadySeconds = [Math]::Round($stopwatch.Elapsed.TotalSeconds, 3)
            }
        } catch {
            if ($_.Exception.Response) {
                $frontendStatusCode = [int]$_.Exception.Response.StatusCode
            }
        }
    }

    if ($backendReady -and $frontendReady) {
        break
    }

    Start-Sleep -Milliseconds 500
}

$backendListener = Get-NetTCPConnection -LocalPort $BackendPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
$frontendListener = Get-NetTCPConnection -LocalPort $FrontendPort -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1
$backendListenerPid = if ($backendListener) { $backendListener.OwningProcess } else { $null }
$frontendListenerPid = if ($frontendListener) { $frontendListener.OwningProcess } else { $null }

$backendAlive = [bool]$backendListenerPid
$frontendAlive = [bool]$frontendListenerPid

$backendErrPreview = ""
$frontendErrPreview = ""
if (-not $backendReady -and (Test-Path $backendErr)) {
    $backendErrPreview = (Get-Content $backendErr -TotalCount 30 | Out-String).TrimEnd()
}
if (-not $frontendReady -and (Test-Path $frontendErr)) {
    $frontendErrPreview = (Get-Content $frontendErr -TotalCount 30 | Out-String).TrimEnd()
}

$result = [PSCustomObject]@{
    repo = $repo
    backendPid = if ($backendProc) { $backendProc.Id } else { $null }
    frontendPid = if ($frontendProc) { $frontendProc.Id } else { $null }
    backendLauncher = "cmd.exe"
    frontendLauncher = "cmd.exe"
    backendReady = $backendReady
    frontendReady = $frontendReady
    backendReadySeconds = $backendReadySeconds
    frontendReadySeconds = $frontendReadySeconds
    backendStatusCode = $backendStatusCode
    frontendStatusCode = $frontendStatusCode
    backendAlive = $backendAlive
    frontendAlive = $frontendAlive
    backendListenerPid = $backendListenerPid
    frontendListenerPid = $frontendListenerPid
    killedPids = $killedPids
    backendOutLog = $backendOut
    backendErrLog = $backendErr
    frontendOutLog = $frontendOut
    frontendErrLog = $frontendErr
    backendErrPreview = $backendErrPreview
    frontendErrPreview = $frontendErrPreview
}

Write-Host "=== Restart Status ==="
Write-Host ("Backend PID: {0} | Ready: {1} | ReadySeconds: {2}" -f $result.backendPid, $result.backendReady, $result.backendReadySeconds)
Write-Host ("Frontend PID: {0} | Ready: {1} | ReadySeconds: {2}" -f $result.frontendPid, $result.frontendReady, $result.frontendReadySeconds)

if (-not $result.backendReady) {
    Write-Host "--- Backend stderr preview ---"
    Write-Host $result.backendErrPreview
}
if (-not $result.frontendReady) {
    Write-Host "--- Frontend stderr preview ---"
    Write-Host $result.frontendErrPreview
}

$result | ConvertTo-Json -Depth 4

if (-not ($backendReady -and $frontendReady)) {
    exit 1
}
