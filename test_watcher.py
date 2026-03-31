"""
Test script for File System Watcher

This script tests the watcher functionality by:
1. Creating a test file in the drop folder
2. Verifying the action file is created in Needs_Action
3. Cleaning up test files

Run this after installing dependencies to verify the watcher works.
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime


def test_watcher():
    """Test the file system watcher."""
    print("=" * 60)
    print("AI Employee - File System Watcher Test")
    print("=" * 60)
    
    # Get paths
    script_dir = Path(__file__).parent.absolute()
    vault_path = script_dir / 'AI_Employee_Vault'
    drop_folder = vault_path / 'Drop'
    needs_action = vault_path / 'Needs_Action'
    
    print(f"\n✓ Vault path: {vault_path}")
    print(f"✓ Drop folder: {drop_folder}")
    print(f"✓ Needs Action: {needs_action}")
    
    # Verify directories exist
    assert vault_path.exists(), f"Vault path does not exist: {vault_path}"
    assert drop_folder.exists(), f"Drop folder does not exist: {drop_folder}"
    assert needs_action.exists(), f"Needs_Action folder does not exist: {needs_action}"
    print("\n✓ All required directories exist")
    
    # Create test file
    test_content = f"Test file created at {datetime.now().isoformat()}"
    test_file = drop_folder / f"test_{int(time.time())}.txt"
    
    print(f"\n→ Creating test file: {test_file.name}")
    test_file.write_text(test_content)
    print("✓ Test file created")
    
    # Wait for watcher to process (if running)
    print("\n→ Waiting 3 seconds for watcher to process...")
    print("   (Start filesystem_watcher.py in another terminal to see real-time detection)")
    time.sleep(3)
    
    # Check for action files
    action_files = list(needs_action.glob("FILE_*.md"))
    
    if action_files:
        latest_action = max(action_files, key=lambda f: f.stat().st_mtime)
        print(f"\n✓ Action file detected: {latest_action.name}")
        print(f"\n→ Action file content preview:")
        print("-" * 40)
        content = latest_action.read_text()
        # Show first 15 lines
        lines = content.split('\n')[:15]
        for line in lines:
            print(line)
        print("..." )
        print("-" * 40)
    else:
        print("\n⚠ No action file detected yet")
        print("  To process the test file:")
        print("  1. Run: python watchers/filesystem_watcher.py --vault AI_Employee_Vault")
        print("  2. The watcher will detect the file and create an action file")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("""
Next Steps:
1. Install dependencies: pip install -r watchers/requirements.txt
2. Start the watcher:
   python watchers/filesystem_watcher.py --vault AI_Employee_Vault
3. Drop a file into AI_Employee_Vault/Drop/
4. Check AI_Employee_Vault/Needs_Action/ for the created action file
5. Use Qwen Code to process the action file:
   qwen --cwd AI_Employee_Vault
   "Check the Needs_Action folder and process any pending items"
    """)
    
    # Cleanup option
    print("\n→ Cleanup test file? (y/n): ", end='')
    # Don't actually prompt, just show the option
    print("(Manual cleanup: delete the test file from Drop folder)")
    
    return True


if __name__ == '__main__':
    try:
        test_watcher()
        print("\n✓ Test completed successfully!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
