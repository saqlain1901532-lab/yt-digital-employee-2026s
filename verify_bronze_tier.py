"""
Bronze Tier Verification Script

Run this script to verify all Bronze Tier requirements are met.
"""

import sys
from pathlib import Path


def check_file(path: Path, description: str) -> bool:
    """Check if a file or directory exists."""
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists


def verify_bronze_tier():
    """Verify all Bronze Tier requirements."""
    print("=" * 60)
    print("BRONZE TIER VERIFICATION")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.absolute()
    vault = base_dir / 'AI_Employee_Vault'
    watchers = base_dir / 'watchers'
    
    all_passed = True
    
    # 1. Vault Structure
    print("\n1. VAULT STRUCTURE")
    print("-" * 40)
    required_folders = [
        'Inbox', 'Needs_Action', 'Done', 'Plans',
        'Pending_Approval', 'Approved', 'Rejected',
        'Logs', 'Briefings', 'Accounting', 'Invoices', 'Drop'
    ]
    for folder in required_folders:
        if not check_file(vault / folder, f"Folder /{folder}"):
            all_passed = False
    
    # 2. Core Documents
    print("\n2. CORE DOCUMENTS")
    print("-" * 40)
    required_files = [
        ('Dashboard.md', 'Dashboard'),
        ('Company_Handbook.md', 'Company Handbook'),
        ('Business_Goals.md', 'Business Goals'),
    ]
    for filename, description in required_files:
        if not check_file(vault / filename, description):
            all_passed = False
    
    # 3. Watcher Scripts
    print("\n3. WATCHER SCRIPTS")
    print("-" * 40)
    watcher_files = [
        ('base_watcher.py', 'Base Watcher Class'),
        ('filesystem_watcher.py', 'File System Watcher'),
        ('requirements.txt', 'Python Dependencies'),
        ('README.md', 'Watcher Documentation'),
    ]
    for filename, description in watcher_files:
        if not check_file(watchers / filename, description):
            all_passed = False
    
    # 4. Setup Files
    print("\n4. SETUP FILES")
    print("-" * 40)
    setup_files = [
        ('BRONZE_TIER_SETUP.md', 'Setup Guide'),
        ('test_watcher.py', 'Test Script'),
        ('.gitignore', 'Git Ignore File'),
    ]
    for filename, description in setup_files:
        if not check_file(base_dir / filename, description):
            all_passed = False
    
    # 5. Python Dependencies Check
    print("\n5. PYTHON DEPENDENCIES")
    print("-" * 40)
    try:
        import watchdog
        print(f"  ✓ watchdog installed (v{watchdog.__version__})")
    except ImportError:
        print(f"  ✗ watchdog NOT installed")
        print(f"    Install with: pip install -r watchers/requirements.txt")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("\n✓ ALL BRONZE TIER REQUIREMENTS MET!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r watchers/requirements.txt")
        print("2. Start watcher: python watchers/filesystem_watcher.py --vault AI_Employee_Vault")
        print("3. Test with Qwen Code: cd AI_Employee_Vault && qwen")
        print("\nYou're ready to process the hackathon Bronze Tier!")
    else:
        print("\n✗ SOME REQUIREMENTS NOT MET")
        print("Review the missing items above and create them before proceeding.")
    
    print("\n" + "=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = verify_bronze_tier()
    sys.exit(0 if success else 1)
