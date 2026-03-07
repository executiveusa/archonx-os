@echo off
REM Start Open Brain MCP Server (Windows)
REM Validates .env, runs schema check, then starts the server

setlocal enabledelayedexpansion

echo ================================
echo Open Brain MCP Server - Startup
echo ================================

REM Change to script directory
cd /d "%~dp0" || exit /b 1

REM Check .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and fill in the required values.
    exit /b 1
)

echo ^✓ .env file found

REM Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ^✓ Python available: %PYTHON_VERSION%

REM Install/upgrade dependencies
echo.
echo Installing dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    exit /b 1
)
echo ^✓ Dependencies installed

REM Run schema check
echo.
echo Verifying database schema...
python schema_check.py
if errorlevel 1 (
    echo ERROR: Schema check failed
    exit /b 1
)
echo ^✓ Schema check passed

REM Start the server
echo.
echo Starting Open Brain MCP Server...
echo Press Ctrl+C to stop
python open_brain_mcp_server.py

exit /b 0
