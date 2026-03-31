# Quick Start Guide - Silver Tier Installation

## Step 1: Install Python

1. **Download Python**: https://www.python.org/downloads/
2. **Run the installer**
3. **✅ IMPORTANT**: Check "Add Python to PATH" before clicking Install
4. Click "Install Now"

### Verify Python Installation
Open a **NEW** terminal/command prompt and run:
```bash
python --version
```
Should show: `Python 3.13.x` or higher

---

## Step 2: Install Node.js

1. **Download Node.js**: https://nodejs.org/
2. Download the **LTS version** (v20 or v22)
3. Run the installer
4. Click "Next" through all steps

### Verify Node.js Installation
Open a **NEW** terminal/command prompt and run:
```bash
node --version
npm --version
```
Should show: `v20.x.x` or higher

---

## Step 3: Install Silver Tier

After Python and Node.js are installed, run:

### Windows (Double-click this file)
```
install-silver-tier.bat
```

### Or run manually:
```bash
# 1. Install Python packages
cd watchers
pip install -r requirements.txt

# 2. Install Playwright browsers
python -m playwright install chromium

# 3. Install Email MCP
cd ../mcp-servers/email-mcp
npm install

# 4. Install Playwright MCP
npm install -g @playwright/mcp

# 5. Verify installation
cd ../..
python verify_silver_tier.py
```

---

## Step 4: Setup Gmail API (Required for Email features)

1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Copy to:
   - `watchers/credentials.json`
   - `mcp-servers/email-mcp/credentials.json`

### Authenticate Gmail
```bash
cd mcp-servers/email-mcp
node authenticate.js
```

---

## Step 5: Start AI Employee

```bash
# Start the orchestrator (manages all watchers)
python orchestrator.py --vault AI_Employee_Vault
```

Or start individual watchers:
```bash
# File watcher (always running)
python watchers/filesystem_watcher.py --vault AI_Employee_Vault

# Gmail watcher (requires credentials)
python watchers/gmail_watcher.py --vault AI_Employee_Vault --credentials credentials.json
```

---

## Troubleshooting

### "python is not recognized"
- Make sure you checked "Add Python to PATH" during installation
- Open a NEW terminal after installing
- Restart your computer if needed

### "node is not recognized"
- Open a NEW terminal after installing Node.js
- Restart your computer if needed

### pip install fails
```bash
python -m pip install -r watchers/requirements.txt
```

### Playwright install fails
```bash
python -m playwright install chromium --force
```

---

## Checklist

After installation, verify:

- [ ] Python installed: `python --version`
- [ ] Node.js installed: `node --version`
- [ ] Dependencies installed: `pip show watchdog`
- [ ] Playwright browsers: `python -m playwright --version`
- [ ] Email MCP: `ls mcp-servers/email-mcp/node_modules`
- [ ] Verification passes: `python verify_silver_tier.py`

---

## Need Help?

1. Read `INSTALL_SILVER_TIER.md` for detailed instructions
2. Read `SILVER_TIER_SETUP.md` for complete setup guide
3. Join Wednesday Research Meetings (10:00 PM PKT)

---

*Quick Start Guide - AI Employee Silver Tier*
