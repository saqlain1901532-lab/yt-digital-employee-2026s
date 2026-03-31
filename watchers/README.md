# AI Employee Watchers

Lightweight Python scripts that monitor various inputs and create actionable files for Claude Code to process.

## Quick Start

### 1. Install Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

### 2. Run the File System Watcher

```bash
# From the watchers directory
python filesystem_watcher.py --vault ../AI_Employee_Vault
```

### 3. Test the Watcher

In a separate terminal, drop a file into the Drop folder:

```bash
# Create the drop folder if it doesn't exist
mkdir -p ../AI_Employee_Vault/Drop

# Drop a test file
echo "Test content" > ../AI_Employee_Vault/Drop/test.txt
```

The watcher should detect the new file and create an action file in `../AI_Employee_Vault/Needs_Action/`.

## Available Watchers

### FileSystemWatcher (Bronze Tier)

Monitors a drop folder for new files and creates action files.

**Features:**
- Real-time file detection using watchdog
- Tracks file hashes to avoid duplicate processing
- Creates detailed markdown action files with metadata
- Logs all actions for audit trail

**Usage:**
```bash
python filesystem_watcher.py --vault /path/to/vault
```

**Options:**
- `--vault`: Path to Obsidian vault (default: `../AI_Employee_Vault`)
- `--drop-folder`: Custom drop folder path (default: `vault/Drop`)

## Architecture

All watchers follow the `BaseWatcher` pattern:

```
┌─────────────────┐
│  Data Source    │ (Gmail, WhatsApp, FileSystem, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Watcher       │ (check_for_updates → create_action_file)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Needs_Action/   │ (Markdown files for Qwen)
└─────────────────┘
```

## Creating a Custom Watcher

1. Inherit from `BaseWatcher`
2. Implement `check_for_updates()` - return list of new items
3. Implement `create_action_file()` - create markdown file in Needs_Action
4. Run with `watcher.run()` or `watcher.run_with_observer()`

Example:
```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def check_for_updates(self):
        # Return list of new items
        return new_items
    
    def create_action_file(self, item):
        # Create markdown file and return path
        filepath = self.needs_action / f"ITEM_{item['id']}.md"
        filepath.write_text(content)
        return filepath
```

## Logs

Watcher logs are stored in `Vault/Logs/`:
- `FileSystemWatcher.log` - Runtime logs
- `YYYY-MM-DD.jsonl` - Daily audit logs

## Troubleshooting

### Watcher doesn't detect files
- Ensure the drop folder exists
- Check file permissions
- Verify watchdog is installed: `pip install watchdog`

### Action files not created
- Check `Needs_Action/` folder exists
- Review logs in `Vault/Logs/`
- Verify vault path is correct

### High CPU usage
- FileSystemWatcher uses real-time events (low CPU)
- If using polling, increase `check_interval`

## Next Steps (Silver Tier)

- [ ] Gmail Watcher - Monitor email inbox
- [ ] WhatsApp Watcher - Monitor WhatsApp Web
- [ ] LinkedIn Watcher - Monitor LinkedIn messages
- [ ] Finance Watcher - Track bank transactions
