#!/bin/bash
# Silver Tier Installation Script for Linux/Mac
# Run this script to install all Silver Tier dependencies

echo "============================================================"
echo "AI Employee - Silver Tier Installation"
echo "============================================================"
echo ""

# Check for Python
echo "[1/6] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.13+"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Mac: brew install python@3.13"
    exit 1
fi
python3 --version
echo ""

# Check for Node.js
echo "[2/6] Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js not found!"
    echo "Please install Node.js v24+ LTS"
    echo "  Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash - && sudo apt install -y nodejs"
    echo "  Mac: brew install node@24"
    exit 1
fi
node --version
npm --version
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Install Python dependencies
echo "[3/6] Installing Python dependencies..."
cd watchers
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install Python dependencies"
    exit 1
fi
cd ..
echo ""

# Install Playwright browsers
echo "[4/6] Installing Playwright browsers..."
python3 -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "WARNING: Playwright browser installation failed"
    echo "You can install it later with: python3 -m playwright install chromium"
fi
echo ""

# Install Email MCP dependencies
echo "[5/6] Installing Email MCP server dependencies..."
cd mcp-servers/email-mcp
npm install
if [ $? -ne 0 ]; then
    echo "WARNING: Email MCP installation failed"
    echo "You can install it later with: npm install"
fi
cd ../..
echo ""

# Install Playwright MCP globally
echo "[6/6] Installing Playwright MCP server..."
npm install -g @playwright/mcp
if [ $? -ne 0 ]; then
    echo "WARNING: Playwright MCP installation failed"
    echo "You can install it later with: npm install -g @playwright/mcp"
fi
echo ""

echo "============================================================"
echo "Installation Complete!"
echo "============================================================"
echo ""
echo "Next Steps:"
echo "1. Setup Gmail API credentials (see INSTALL_SILVER_TIER.md)"
echo "2. Run: python3 verify_silver_tier.py"
echo "3. Start orchestrator: python3 orchestrator.py --vault AI_Employee_Vault"
echo ""
