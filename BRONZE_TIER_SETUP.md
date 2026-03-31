# AI Employee - Bronze Tier Setup Guide

## Overview

This guide walks you through setting up the **Bronze Tier** of the Personal AI Employee hackathon.

**Bronze Tier Deliverables:**
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ One working Watcher script (File System Watcher)
- ✅ Qwen Code reading from and writing to the vault
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done

**Estimated Time:** 8-12 hours

---

## Prerequisites

Before starting, ensure you have:

1. **Python 3.13+** - [Download](https://www.python.org/downloads/)
2. **Qwen Code** - Installed and configured
3. **Obsidian** (optional, for viewing vault) - [Download](https://obsidian.md/download)

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13 or higher

# Check Qwen Code
qwen --version
```

---

## Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd yt-digital-employee-2026

# Install Python dependencies for watchers
cd watchers
pip install -r requirements.txt
cd ..
```

---

## Step 2: Verify Vault Structure

The Obsidian vault should be set up at `AI_Employee_Vault/` with these folders:

```
AI_Employee_Vault/
├── Inbox/
├── Needs_Action/
├── Done/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Logs/
├── Briefings/
├── Accounting/
├── Invoices/
├── Drop/
├── Dashboard.md
├── Company_Handbook.md
└── Business_Goals.md
```

---

## Step 3: Start the File System Watcher

Open a terminal and run:

```bash
# From the project root directory
python watchers/filesystem_watcher.py --vault AI_Employee_Vault
```

You should see output like:

```
2026-03-31 10:00:00 - INFO - Starting FileSystemWatcher
2026-03-31 10:00:00 - INFO - Drop folder: AI_Employee_Vault/Drop
2026-03-31 10:00:00 - INFO - File observer started - watching for new files...
```

**Keep this terminal running** - the watcher monitors continuously.

---

## Step 4: Test the Watcher

In a **separate terminal**, drop a test file:

```bash
# Create a test file in the drop folder
echo "This is a test document for processing" > AI_Employee_Vault/Drop/test_document.txt
```

The watcher should detect the file and create an action file in `Needs_Action/`:

```
2026-03-31 10:01:00 - INFO - New file found: test_document.txt
2026-03-31 10:01:00 - INFO - Created action file: FILE_abc12345_20260331_100100.md
```

---

## Step 5: Process with Qwen Code

Now use Qwen Code to process the action file:

```bash
# Navigate to the vault directory
cd AI_Employee_Vault

# Start Qwen Code
qwen
```

Once Qwen starts, give it this prompt:

```
Check the Needs_Action folder for any pending items. Read the action files and:
1. Summarize what needs to be done
2. Create a plan in the Plans folder
3. Process the items and move them to Done when complete
```

Qwen should:
1. Read the action file
2. Create a plan in `/Plans/`
3. Process the request
4. Move completed items to `/Done/`

---

## Step 6: Update Dashboard

After Qwen processes items, update the Dashboard.md:

```
Please update the Dashboard.md with:
1. Current count of items in Needs_Action
2. Recent activity from the last processing run
3. Any pending approvals needed
```

---

## Verification Checklist

### Bronze Tier Requirements

- [ ] **Obsidian vault exists** at `AI_Employee_Vault/`
- [ ] **Dashboard.md** created with status tracking
- [ ] **Company_Handbook.md** created with rules of engagement
- [ ] **Business_Goals.md** created with objectives
- [ ] **Folder structure** complete (/Inbox, /Needs_Action, /Done, etc.)
- [ ] **File System Watcher** runs without errors
- [ ] **Watcher detects files** dropped into Drop folder
- [ ] **Action files created** in Needs_Action folder
- [ ] **Qwen Code processes** action files successfully
- [ ] **Completed items moved** to Done folder

---

## Troubleshooting

### Python not found
Install Python 3.13 or higher from [python.org](https://www.python.org/downloads/)

### pip not found
```bash
python -m pip install watchdog
```

### Watcher doesn't detect files
1. Verify the Drop folder exists: `ls AI_Employee_Vault/Drop`
2. Check file permissions
3. Restart the watcher

### Qwen Code not found
Install Qwen Code and ensure it's in your PATH.

### Action files not created
1. Check `Needs_Action/` folder exists
2. Review logs in `Vault/Logs/`
3. Verify watchdog is installed: `pip show watchdog`

---

## Next Steps (Silver Tier)

Once Bronze Tier is complete, you can add:

1. **Gmail Watcher** - Monitor email inbox
2. **WhatsApp Watcher** - Monitor WhatsApp Web messages
3. **MCP Server** - Send emails automatically
4. **Human-in-the-Loop** - Approval workflow
5. **Scheduled Tasks** - Cron-based automation

---

## Resources

- [Main Hackathon Document](./Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Watcher Documentation](./watchers/README.md)
- [Company Handbook](./AI_Employee_Vault/Company_Handbook.md)
- [Business Goals](./AI_Employee_Vault/Business_Goals.md)

---

## Support

Join the Wednesday Research Meeting for help:
- **When:** Wednesdays 10:00 PM PKT
- **Zoom:** [Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [@panaversity](https://www.youtube.com/@panaversity)
