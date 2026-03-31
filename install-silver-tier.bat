@echo off
REM Silver Tier Installation Script for Windows
REM Run this script to install all Silver Tier dependencies

echo ============================================================
echo AI Employee - Silver Tier Installation
echo ============================================================
echo.

REM Check for Python
echo [1/6] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found!
    echo Please install Python 3.13+ from: https://www.python.org/downloads/
    echo Or install from Microsoft Store
    pause
    exit /b 1
)
python --version
echo.

REM Check for Node.js
echo [2/6] Checking Node.js installation...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found!
    echo Please install Node.js v24+ LTS from: https://nodejs.org/
    pause
    exit /b 1
)
node --version
npm --version
echo.

REM Install Python dependencies
echo [3/6] Installing Python dependencies...
cd /d "%~dp0watchers"
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
cd ..
echo.

REM Install Playwright browsers
echo [4/6] Installing Playwright browsers...
python -m playwright install chromium
if %errorlevel% neq 0 (
    echo WARNING: Playwright browser installation failed
    echo You can install it later with: python -m playwright install chromium
)
echo.

REM Install Email MCP dependencies
echo [5/6] Installing Email MCP server dependencies...
cd /d "%~dp0mcp-servers\email-mcp"
npm install
if %errorlevel% neq 0 (
    echo WARNING: Email MCP installation failed
    echo You can install it later with: npm install
)
cd ..\..
echo.

REM Install Playwright MCP globally
echo [6/6] Installing Playwright MCP server...
npm install -g @playwright/mcp
if %errorlevel% neq 0 (
    echo WARNING: Playwright MCP installation failed
    echo You can install it later with: npm install -g @playwright/mcp
)
echo.

echo ============================================================
echo Installation Complete!
echo ============================================================
echo.
echo Next Steps:
echo 1. Setup Gmail API credentials (see SILVER_TIER_SETUP.md)
echo 2. Run: python verify_silver_tier.py
echo 3. Start orchestrator: python orchestrator.py --vault AI_Employee_Vault
echo.
pause
