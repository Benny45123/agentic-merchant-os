# ==============================================================================
# Stop Full Stack on Windows via PowerShell
# ==============================================================================
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "🛑 Stopping Agentic Merchant OS Servers..." -ForegroundColor Yellow
Write-Host "=================================================================="

# Stop processes listening on 8000 and 3000
$ports = @(8000, 3000)
foreach ($port in $ports) {
    $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($pid_num in $processes) {
        if ($pid_num) {
            Stop-Process -Id $pid_num -Force -ErrorAction SilentlyContinue
            Write-Host "Killed process $pid_num on port $port" -ForegroundColor Green
        }
    }
}

Write-Host "✅ All servers stopped successfully." -ForegroundColor Green
