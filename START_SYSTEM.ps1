# School ID Automation System - Startup Script
# This script starts both the backend (Python FastAPI) and frontend (React Vite)

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "          School ID Automation System - Starting...            " -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvPath)) {
    Write-Host "[X] Virtual environment not found!" -ForegroundColor Red
    Write-Host "    Please create it first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Check if node_modules exists
$nodeModulesPath = ".\UI\node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "[!] Node modules not found. Installing..." -ForegroundColor Yellow
    Set-Location .\UI
    npm install
    Set-Location ..
}

Write-Host "[*] Starting Backend Server (Python FastAPI)..." -ForegroundColor Green
Write-Host "    Port: 8000" -ForegroundColor Gray
Write-Host "    URL: http://localhost:8000`n" -ForegroundColor Gray

# Start backend in new PowerShell window
$backendScript = @"
`$host.ui.RawUI.WindowTitle = 'Backend Server (Port 8000)'
Write-Host '================================================================' -ForegroundColor Magenta
Write-Host '               BACKEND SERVER - Python FastAPI                  ' -ForegroundColor Magenta
Write-Host '================================================================' -ForegroundColor Magenta
Set-Location '$PWD'
.\venv\Scripts\Activate.ps1
Write-Host '[OK] Virtual environment activated' -ForegroundColor Green
Write-Host '[*] Starting FastAPI server on port 8000...' -ForegroundColor Cyan
Write-Host ''
python run.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

Start-Sleep -Seconds 3

Write-Host "[*] Starting Frontend Server (React Vite)..." -ForegroundColor Green
Write-Host "    Port: 5173" -ForegroundColor Gray
Write-Host "    URL: http://localhost:5173`n" -ForegroundColor Gray

# Start frontend in new PowerShell window
$frontendScript = @"
`$host.ui.RawUI.WindowTitle = 'Frontend Server (Port 5173)'
Write-Host '================================================================' -ForegroundColor Blue
Write-Host '               FRONTEND SERVER - React + Vite                   ' -ForegroundColor Blue
Write-Host '================================================================' -ForegroundColor Blue
Set-Location '$PWD\UI'
Write-Host '[*] Starting Vite dev server on port 5173...' -ForegroundColor Cyan
Write-Host ''
npm run dev
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

Start-Sleep -Seconds 5

Write-Host "================================================================" -ForegroundColor Green
Write-Host "             [OK] SYSTEM STARTED SUCCESSFULLY!                  " -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

Write-Host "[*] Access Points:" -ForegroundColor Cyan
Write-Host "    - Main UI:    http://localhost:5173" -ForegroundColor White
Write-Host "    - Backend:    http://localhost:8000" -ForegroundColor White
Write-Host "    - API Docs:   http://localhost:8000/docs`n" -ForegroundColor White

Write-Host "[*] Quick Actions:" -ForegroundColor Cyan
Write-Host "    - Capture Station: http://localhost:5173/capture" -ForegroundColor Gray
Write-Host "    - Dashboard:       http://localhost:5173/dashboard" -ForegroundColor Gray
Write-Host "    - Layout Editor:   http://localhost:5173/editor" -ForegroundColor Gray
Write-Host "    - Settings:        http://localhost:5173/settings`n" -ForegroundColor Gray

Write-Host "[!] To stop the system:" -ForegroundColor Yellow
Write-Host "    - Close both PowerShell windows" -ForegroundColor Gray
Write-Host "    - Or press Ctrl+C in each window`n" -ForegroundColor Gray

Write-Host "[*] Documentation:" -ForegroundColor Cyan
Write-Host "    - Integration Guide: INTEGRATION_GUIDE.md" -ForegroundColor Gray
Write-Host "    - Frontend README:   UI/README.md`n" -ForegroundColor Gray

# Open browser after a delay
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

Write-Host "[*] Browser opened to http://localhost:5173" -ForegroundColor Green
Write-Host "`nPress any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')