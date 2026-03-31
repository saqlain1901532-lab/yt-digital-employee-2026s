# Qwen Code - AI Employee Quick Reference

## Quick Start Commands

### Start the File System Watcher
```bash
cd yt-digital-employee-2026
python watchers/filesystem_watcher.py --vault AI_Employee_Vault
```

### Start Qwen Code with the Vault
```bash
cd AI_Employee_Vault
qwen
```

---

## Common Qwen Prompts

### Process Pending Items
```
Check the Needs_Action folder for any pending items. For each item:
1. Summarize what needs to be done
2. Create a plan in the Plans folder
3. Execute the required actions
4. Move completed items to Done
```

### Update Dashboard
```
Update the Dashboard.md with:
1. Current count of items in each folder
2. Recent activity from the logs
3. Any pending approvals needed
4. System health status
```

### Generate Daily Briefing
```
Create a daily briefing in Briefings/ folder with:
1. Tasks completed yesterday
2. Pending items requiring attention
3. Any patterns or insights from recent activity
4. Recommendations for today
```

### Process Specific File
```
Read the file [filename] in Needs_Action and:
1. Analyze the content
2. Determine required actions
3. Execute or create approval request
4. Document your reasoning
```

---

## Folder Structure Reference

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring attention |
| `/Plans` | Generated action plans |
| `/Pending_Approval` | Awaiting human approval |
| `/Approved` | Ready to execute |
| `/Done` | Completed items |
| `/Logs` | Activity audit logs |

---

## Human-in-the-Loop Pattern

When Qwen detects a sensitive action needed:

1. **Qwen creates**: `/Pending_Approval/ACTION_description.md`
2. **You review**: Read the file and decide
3. **To approve**: Move file to `/Approved/`
4. **To reject**: Move file to `/Rejected/`

---

## Watcher Status

| Status | Indicator | Meaning |
|--------|-----------|---------|
| Running | 🟢 | Watcher active, monitoring |
| Stopped | 🔴 | Watcher not running |
| Error | 🟡 | Check logs in `/Logs/` |

---

## Troubleshooting

### Qwen doesn't start
```bash
# Verify installation
qwen --version

# Try with explicit path
qwen --cwd /full/path/to/AI_Employee_Vault
```

### Watcher not detecting files
```bash
# Check if Python is available
python --version

# Install dependencies
pip install -r watchers/requirements.txt

# Restart watcher
python watchers/filesystem_watcher.py --vault AI_Employee_Vault
```

### Files not being processed
```bash
# Check Needs_Action folder
ls AI_Employee_Vault/Needs_Action/

# Review logs
cat AI_Employee_Vault/Logs/FileSystemWatcher.log

# Prompt Qwen to check
qwen "Check the Needs_Action folder and report what you find"
```

---

## Best Practices

1. **Review daily**: Check Dashboard.md each morning
2. **Approve promptly**: Process `/Pending_Approval/` items quickly
3. **Clean Done folder**: Archive completed items weekly
4. **Update Handbook**: Refine rules as you learn
5. **Monitor logs**: Check `/Logs/` for errors

---

## Example Workflow

```
1. Drop file → AI_Employee_Vault/Drop/document.pdf
2. Watcher detects → Creates FILE_abc123.md in Needs_Action
3. Qwen processes → Reads file, creates plan, executes
4. Approval needed → Creates Pending_Approval/request.md
5. You approve → Move to Approved/
6. Qwen completes → Moves to Done/, updates Dashboard
```

---

*Generated for AI Employee Bronze Tier - Qwen Code Edition*
