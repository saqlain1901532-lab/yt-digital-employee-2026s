# Silver Tier - Installation Instructions

## Quick Install (Automated)

### Windows
```bash
# Run the installation script
install-silver-tier.bat
```

### Linux/Mac
```bash
# Run the installation script
bash install-silver-tier.sh
```

---

## Manual Installation

If the automated script doesn't work, follow these steps:

### Step 1: Install Python 3.13+

**Windows:**
1. Download from https://www.python.org/downloads/
2. Run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"

**Verify:**
```bash
python --version  # Should show Python 3.13.x
```

### Step 2: Install Node.js v24+ LTS

**Windows:**
1. Download from https://nodejs.org/
2. Run installer
3. Click "Next" through the wizard

**Verify:**
```bash
node --version  # Should show v24.x.x
npm --version
```

### Step 3: Install Python Dependencies

```bash
cd yt-digital-employee-2026/watchers
pip install -r requirements.txt
```

This installs:
- `watchdog` - File system monitoring
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Gmail API
- `playwright` - Browser automation
- `requests` - HTTP requests
- `python-dotenv` - Environment variables

### Step 4: Install Playwright Browsers

```bash
python -m playwright install chromium
```

### Step 5: Install Node.js Dependencies

```bash
# Email MCP Server
cd mcp-servers/email-mcp
npm install

# Playwright MCP (global)
npm install -g @playwright/mcp
```

---

## Post-Installation Setup

### 1. Setup Gmail API Credentials

1. Visit https://console.cloud.google.com/
2. Create new project (e.g., "AI Employee")
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json`
6. Save to:
   - `watchers/credentials.json`
   - `mcp-servers/email-mcp/credentials.json`

### 2. Authenticate Gmail

```bash
cd mcp-servers/email-mcp
node authenticate.js
# Follow the link and paste authorization code
```

### 3. Verify Installation

```bash
python verify_silver_tier.py
```

Expected output:
```
✓ ALL SILVER TIER REQUIREMENTS MET!
```

---

## Start Silver Tier

### Option 1: Start Orchestrator (Recommended)
```bash
python orchestrator.py --vault AI_Employee_Vault
```

This starts:
- File System Watcher
- Gmail Watcher (if enabled)
- WhatsApp Watcher (if enabled)
- Scheduled tasks (briefings, cleanup)

### Option 2: Start Individual Watchers
```bash
# File System Watcher
python watchers/filesystem_watcher.py --vault AI_Employee_Vault

# Gmail Watcher (in another terminal)
python watchers/gmail_watcher.py --vault AI_Employee_Vault --credentials credentials.json

# WhatsApp Watcher (in another terminal)
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault
```

### Option 3: Use Qwen Code Directly
```bash
cd AI_Employee_Vault
qwen
```

---

## Troubleshooting

### Python Not Found
**Windows:** Install from https://www.python.org/downloads/
**Make sure to check "Add Python to PATH"**

### Node.js Not Found
Install from https://nodejs.org/

### pip Not Found
```bash
python -m pip install -r watchers/requirements.txt
```

### Playwright Browser Install Fails
```bash
# Try with admin/sudo
python -m playwright install chromium --force

# Or manually download browsers
```

### Gmail API Error
- Ensure Gmail API is enabled in Google Cloud Console
- Check credentials.json is valid
- Re-run authentication: `node authenticate.js`

---

## Silver Tier Components

| Component | File | Status |
|-----------|------|--------|
| File System Watcher | `watchers/filesystem_watcher.py` | ✅ |
| Gmail Watcher | `watchers/gmail_watcher.py` | ✅ |
| WhatsApp Watcher | `watchers/whatsapp_watcher.py` | ✅ |
| Email MCP Server | `mcp-servers/email-mcp/` | ✅ |
| LinkedIn Automation | `skills/linkedin_automation.py` | ✅ |
| Approval Workflow | `skills/approval_workflow.py` | ✅ |
| Plan Generator | `skills/plan_generator.py` | ✅ |
| Orchestrator | `orchestrator.py` | ✅ |

---

## Configuration

### Enable/Disable Watchers

Edit `AI_Employee_Vault/orchestrator_config.json`:

```json
{
  "watchers": {
    "filesystem": {"enabled": true, "interval": 60},
    "gmail": {"enabled": true, "interval": 120},
    "whatsapp": {"enabled": false, "interval": 60}
  }
}
```

### Set Gmail Credentials Path

```bash
# Environment variable (recommended)
export GMAIL_CREDENTIALS=/path/to/credentials.json

# Or copy to default location
cp /path/to/credentials.json watchers/
cp /path/to/credentials.json mcp-servers/email-mcp/
```

---

## Testing

### Test File System Watcher
```bash
# Start watcher
python watchers/filesystem_watcher.py --vault AI_Employee_Vault

# In another terminal, drop a file
echo "Test document" > AI_Employee_Vault/Drop/test.txt

# Check Needs_Action folder for created action file
```

### Test Gmail Watcher
```bash
# Send yourself an email
# Watcher will detect it and create action file
```

### Test WhatsApp Watcher
```bash
# Start watcher
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault

# Send yourself a WhatsApp message with keyword "urgent"
# Watcher will detect and create action file
```

### Test Approval Workflow
```bash
# Create a test approval request
python -c "
from skills.approval_workflow import ApprovalWorkflowManager
manager = ApprovalWorkflowManager('AI_Employee_Vault')
manager.create_approval_request(
    action_type='test_action',
    description='Test approval request',
    parameters={'test': 'data'}
)
"

# Check Pending_Approval folder
```

---

## Resources

- [Full Setup Guide](SILVER_TIER_SETUP.md)
- [Watcher Documentation](watchers/README.md)
- [Quick Reference](QWEN_QUICK_REFERENCE.md)

---

*Silver Tier Installation Guide - Qwen Code Edition*
