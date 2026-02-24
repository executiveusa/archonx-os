@echo off
setlocal

echo [devika-pi] Checking PI coding agent installation...
call npm ls @mariozechner/pi-coding-agent --depth=0 >nul 2>nul
if errorlevel 1 (
  echo [devika-pi] package not found
  exit /b 1
)

echo [devika-pi] package detected
exit /b 0

