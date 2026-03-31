# Silver Tier - Complete Setup Guide

## Overview

Silver Tier extends Bronze Tier with:
- ✅ Two or more Watcher scripts (Gmail, WhatsApp, File System)
- ✅ LinkedIn automation for business posts
- ✅ Plan.md generator for task reasoning
- ✅ Email MCP server for sending emails
- ✅ Human-in-the-Loop approval workflow
- ✅ Orchestrator with scheduling

**Estimated Time:** 20-30 hours

---

## Prerequisites

Ensure Bronze Tier is complete:
- ✅ Obsidian vault with all folders
- ✅ File System Watcher working
- ✅ Qwen Code integration tested

---

## Step 1: Install Python Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

This installs:
- `watchdog` - File system monitoring
- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` - Gmail API
- `playwright` - Browser automation for WhatsApp
- `requests` - HTTP requests
- `python-dotenv` - Environment variables

### Install Playwright Browsers

```bash
playwright install chromium
```

---

## Step 2: Install Node.js for MCP Servers

Silver Tier requires Node.js for MCP servers.

### Windows
```powershell
winget install OpenJS.NodeJS.LTS
```

### Verify
```bash
node --version  # Should be v18+
npm --version
```

---

## Step 3: Setup Email MCP Server

### Install Dependencies
```bash
cd mcp-servers/email-mcp
npm install
```

### Configure Gmail API

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create new project (e.g., "AI Employee")

2. **Enable Gmail API**
   - Go to "APIs & Services" → "Library"
   - Search for "Gmail API"
   - Click "Enable"

3. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Application type: "Desktop app"
   - Download `credentials.json`

4. **Save Credentials**
   ```bash
   # Save to mcp-servers/email-mcp/credentials.json
   # Or set environment variable:
   # export GMAIL_CREDENTIALS=/path/to/credentials.json
   ```

5. **Authenticate**
   ```bash
   cd mcp-servers/email-mcp
   node authenticate.js
   # Follow the link and paste authorization code
   ```

---

## Step 4: Configure Gmail Watcher

### Create Credentials File
```bash
# Copy the same credentials.json to watchers folder
cp mcp-servers/email-mcp/credentials.json watchers/
```

### Test Gmail Watcher
```bash
cd watchers
python gmail_watcher.py --vault ../AI_Employee_Vault --credentials credentials.json
```

**First Run:** A browser window will open for OAuth authentication.

---

## Step 5: Configure WhatsApp Watcher

### Test WhatsApp Watcher
```bash
cd watchers
python whatsapp_watcher.py --vault ../AI_Employee_Vault
```

**First Run:** 
- Browser will open WhatsApp Web
- Scan QR code with your WhatsApp mobile app
- Session is saved for future runs

**Important:** Be aware of WhatsApp's Terms of Service when automating.

---

## Step 6: Setup LinkedIn Automation

### Test LinkedIn Login
```bash
cd skills
python linkedin_automation.py --text "Test post" --vault ../AI_Employee_Vault
```

**Note:** LinkedIn automation uses browser automation. For production use, consider LinkedIn's official API.

---

## Step 7: Configure Approval Workflow

The approval workflow is automatically configured. Test it:

```bash
cd skills
python approval_workflow.py --vault ../AI_Employee_Vault
```

### Approval Workflow Process

1. **AI creates approval request** → `/Pending_Approval/`
2. **You review** the request file
3. **To approve** → Move to `/Approved/`
4. **To reject** → Move to `/Rejected/`
5. **Action executes** automatically when approved

---

## Step 8: Setup Orchestrator

### Create Configuration
```bash
cd AI_Employee_Vault
```

Create `orchestrator_config.json`:
```json
{
  "watchers": {
    "filesystem": {"enabled": true, "interval": 60},
    "gmail": {"enabled": true, "interval": 120},
    "whatsapp": {"enabled": true, "interval": 60}
  },
  "processing": {
    "auto_process": true,
    "process_interval": 300
  },
  "scheduled_tasks": {
    "daily_briefing": {"enabled": true, "time": "08:00"},
    "cleanup": {"enabled": true, "time": "23:00"}
  }
}
```

### Test Orchestrator
```bash
python orchestrator.py --vault AI_Employee_Vault --once
```

### Run Continuously
```bash
python orchestrator.py --vault AI_Employee_Vault
```

---

## Step 9: Setup MCP Configuration

Create MCP configuration for Qwen Code:

### Create config file at `~/.qwen/mcp.json` or project root:

```json
{
  "servers": [
    {
      "name": "filesystem",
      "command": "built-in"
    },
    {
      "name": "playwright",
      "command": "npx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "HEADLESS": "true"
      }
    },
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/mcp-servers/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  ]
}
```

---

## Step 10: Verify Silver Tier Installation

Run the verification script:

```bash
python verify_silver_tier.py
```

Expected output:
```
✓ File System Watcher installed
✓ Gmail Watcher installed
✓ WhatsApp Watcher installed
✓ LinkedIn automation skill ready
✓ Email MCP server configured
✓ Approval workflow active
✓ Plan generator ready
✓ Orchestrator configured
✓ All Silver Tier requirements met!
```

---

## Quick Start Commands

### Start All Watchers
```bash
# File System Watcher
python watchers/filesystem_watcher.py --vault AI_Employee_Vault &

# Gmail Watcher
python watchers/gmail_watcher.py --vault AI_Employee_Vault --credentials credentials.json &

# WhatsApp Watcher
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault &
```

### Start Orchestrator
```bash
python orchestrator.py --vault AI_Employee_Vault
```

### Start Qwen Code
```bash
cd AI_Employee_Vault
qwen
```

---

## Testing the Full Workflow

### Test 1: File Drop → Plan → Action
```bash
# 1. Drop a file
echo "Please process this document" > AI_Employee_Vault/Drop/test.txt

# 2. Watcher creates action file in Needs_Action/

# 3. Orchestrator triggers processing

# 4. Plan generator creates plan in Plans/

# 5. Qwen Code processes the task
```

### Test 2: Email Approval Workflow
```bash
# 1. Gmail watcher detects new email
# 2. Action file created in Needs_Action/
# 3. Qwen creates draft response
# 4. Approval request created in Pending_Approval/
# 5. You move to Approved/
# 6. Email MCP sends the email
# 7. Task moved to Done/
```

### Test 3: LinkedIn Post
```bash
# 1. Create post request
python skills/linkedin_automation.py \
  --text "Excited to share our latest project!" \
  --vault AI_Employee_Vault

# 2. Approval file created in Pending_Approval/
# 3. You approve by moving to Approved/
# 4. Post published to LinkedIn
```

---

## Scheduled Tasks

### Daily Briefing (8:00 AM)
Automatically generates briefing in `/Briefings/`:
- Pending items count
- Awaiting approvals count
- Completed items summary
- Recommendations

### Processing Check (Every 5 minutes)
Checks `/Needs_Action/` for new items and triggers processing.

### Cleanup (Hourly)
Removes expired approval requests.

---

## Troubleshooting

### Gmail Watcher Not Working
```bash
# Check credentials
ls -la credentials.json

# Re-authenticate
cd mcp-servers/email-mcp
node authenticate.js

# Check Gmail API is enabled
# Visit: https://console.cloud.google.com/apis/library/gmail.googleapis.com
```

### WhatsApp Watcher Not Detecting Messages
```bash
# Check session exists
ls -la AI_Employee_Vault/whatsapp_session/

# Re-authenticate WhatsApp
# Delete session folder and restart watcher
rm -rf AI_Employee_Vault/whatsapp_session
python watchers/whatsapp_watcher.py --vault AI_Employee_Vault
```

### MCP Server Not Connecting
```bash
# Check Node.js version
node --version

# Reinstall MCP
npm install -g @playwright/mcp

# Check port availability
netstat -ano | findstr :8808
```

### Orchestrator Not Running
```bash
# Check Python path
which python

# Check vault path
ls AI_Employee_Vault/

# Run in debug mode
python orchestrator.py --vault AI_Employee_Vault --once
```

---

## Silver Tier Requirements Checklist

| Requirement | Status | Verification |
|-------------|--------|--------------|
| Two or more Watcher scripts | ✅ | File, Gmail, WhatsApp |
| LinkedIn automation | ✅ | `skills/linkedin_automation.py` |
| Plan.md generator | ✅ | `skills/plan_generator.py` |
| One working MCP server | ✅ | Email MCP |
| HITL approval workflow | ✅ | `skills/approval_workflow.py` |
| Basic scheduling | ✅ | Orchestrator |
| All as Agent Skills | ✅ | All in `skills/` folder |

---

## File Structure Summary

```
yt-digital-employee-2026/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md
│   ├── Company_Handbook.md
│   ├── Business_Goals.md
│   ├── orchestrator_config.json
│   └── [folders: Inbox, Needs_Action, Plans, etc.]
├── watchers/
│   ├── base_watcher.py
│   ├── filesystem_watcher.py
│   ├── gmail_watcher.py
│   ├── whatsapp_watcher.py
│   └── requirements.txt
├── mcp-servers/
│   └── email-mcp/
│       ├── index.js
│       ├── authenticate.js
│       └── package.json
├── skills/
│   ├── linkedin_automation.py
│   ├── approval_workflow.py
│   └── plan_generator.py
├── orchestrator.py
└── SILVER_TIER_SETUP.md        # This file
```

---

## Next Steps (Gold Tier)

After mastering Silver Tier:
1. **Odoo Community ERP** - Accounting integration
2. **Twitter/X MCP** - Twitter posting
3. **Facebook/Instagram MCP** - Social media integration
4. **Ralph Wiggum Loop** - Persistence for multi-step tasks
5. **CEO Briefing Generator** - Weekly business audit

---

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Playwright Documentation](https://playwright.dev/python/)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Wednesday Research Meetings](https://www.youtube.com/@panaversity)

---

*Silver Tier Setup Guide - Qwen Code Edition*
