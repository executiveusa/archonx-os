@echo off
setlocal

echo [devika-pi] Installing PI coding agent package...
call npm install --save-dev @mariozechner/pi-coding-agent
if errorlevel 1 (
  echo [devika-pi] npm install failed
  exit /b 1
)

echo [devika-pi] Installation complete
exit /b 0

