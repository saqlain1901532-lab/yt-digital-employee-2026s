"""
Silver Tier Verification Script

Run this script to verify all Silver Tier requirements are met.
"""

import sys
import importlib
from pathlib import Path


def check_file(path: Path, description: str) -> bool:
    """Check if a file or directory exists."""
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {path}")
    return exists


def check_module(module_name: str, description: str) -> bool:
    """Check if a Python module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"  ✓ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"  ✗ {description}: {module_name} - {e}")
        return False


def verify_silver_tier():
    """Verify all Silver Tier requirements."""
    print("=" * 60)
    print("SILVER TIER VERIFICATION")
    print("=" * 60)
    
    base_dir = Path(__file__).parent.absolute()
    vault = base_dir / 'AI_Employee_Vault'
    watchers = base_dir / 'watchers'
    mcp_servers = base_dir / 'mcp-servers'
    skills = base_dir / 'skills'
    
    all_passed = True
    
    # 1. Watcher Scripts
    print("\n1. WATCHER SCRIPTS")
    print("-" * 40)
    watcher_files = [
        ('base_watcher.py', 'Base Watcher Class'),
        ('filesystem_watcher.py', 'File System Watcher'),
        ('gmail_watcher.py', 'Gmail Watcher'),
        ('whatsapp_watcher.py', 'WhatsApp Watcher'),
    ]
    for filename, description in watcher_files:
        if not check_file(watchers / filename, description):
            all_passed = False
    
    # 2. MCP Servers
    print("\n2. MCP SERVERS")
    print("-" * 40)
    mcp_files = [
        ('email-mcp/index.js', 'Email MCP Server'),
        ('email-mcp/package.json', 'Email MCP Config'),
        ('email-mcp/authenticate.js', 'Email Auth Script'),
    ]
    for filename, description in mcp_files:
        if not check_file(mcp_servers / filename, description):
            all_passed = False
    
    # 3. Skills
    print("\n3. SKILLS")
    print("-" * 40)
    skill_files = [
        ('linkedin_automation.py', 'LinkedIn Automation'),
        ('approval_workflow.py', 'Approval Workflow'),
        ('plan_generator.py', 'Plan Generator'),
    ]
    for filename, description in skill_files:
        if not check_file(skills / filename, description):
            all_passed = False
    
    # 4. Orchestrator
    print("\n4. ORCHESTRATOR")
    print("-" * 40)
    if not check_file(base_dir / 'orchestrator.py', 'Main Orchestrator'):
        all_passed = False
    
    # 5. Documentation
    print("\n5. DOCUMENTATION")
    print("-" * 40)
    doc_files = [
        ('SILVER_TIER_SETUP.md', 'Silver Tier Setup Guide'),
        ('watchers/README.md', 'Watcher Documentation'),
    ]
    for filename, description in doc_files:
        if not check_file(base_dir / filename, description):
            all_passed = False
    
    # 6. Vault Structure
    print("\n6. VAULT STRUCTURE")
    print("-" * 40)
    required_folders = [
        'Inbox', 'Needs_Action', 'Done', 'Plans',
        'Pending_Approval', 'Approved', 'Rejected',
        'Logs', 'Briefings', 'Drop'
    ]
    for folder in required_folders:
        if not check_file(vault / folder, f"Folder /{folder}"):
            all_passed = False
    
    required_files = [
        ('Dashboard.md', 'Dashboard'),
        ('Company_Handbook.md', 'Company Handbook'),
        ('Business_Goals.md', 'Business Goals'),
    ]
    for filename, description in required_files:
        if not check_file(vault / filename, description):
            all_passed = False
    
    # 7. Python Dependencies
    print("\n7. PYTHON DEPENDENCIES")
    print("-" * 40)
    dependencies = [
        ('watchdog', 'File System Monitoring'),
        ('playwright', 'Browser Automation'),
        ('requests', 'HTTP Requests'),
    ]
    for module_name, description in dependencies:
        if not check_module(module_name, description):
            all_passed = False
    
    # Optional dependencies (not required for pass)
    print("\n  Optional Dependencies (for reference):")
    optional_deps = [
        ('google.oauth2.credentials', 'Gmail Auth'),
        ('googleapiclient.discovery', 'Gmail API'),
    ]
    for module_name, description in optional_deps:
        try:
            importlib.import_module(module_name)
            print(f"  ✓ {description}")
        except ImportError:
            print(f"  ⚪ {description} (install with: pip install -r watchers/requirements.txt)")
    
    # 8. Node.js Check
    print("\n8. NODE.JS ENVIRONMENT")
    print("-" * 40)
    import subprocess
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Node.js installed: {result.stdout.strip()}")
        else:
            print(f"  ✗ Node.js not found")
            all_passed = False
    except FileNotFoundError:
        print(f"  ✗ Node.js not found - Install from https://nodejs.org/")
        all_passed = False
    
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ npm installed: {result.stdout.strip()}")
        else:
            print(f"  ✗ npm not found")
            all_passed = False
    except FileNotFoundError:
        print(f"  ✗ npm not found")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    if all_passed:
        print("\n✓ ALL SILVER TIER REQUIREMENTS MET!")
        print("\nNext steps:")
        print("1. Install Python deps: pip install -r watchers/requirements.txt")
        print("2. Install Playwright browsers: playwright install chromium")
        print("3. Setup Gmail API credentials (see SILVER_TIER_SETUP.md)")
        print("4. Configure MCP servers")
        print("5. Start orchestrator: python orchestrator.py --vault AI_Employee_Vault")
        print("\nYou're ready for Silver Tier!")
    else:
        print("\n✗ SOME REQUIREMENTS NOT MET")
        print("Review the missing items above and complete them before proceeding.")
    
    print("\n" + "=" * 60)
    
    return all_passed


if __name__ == '__main__':
    success = verify_silver_tier()
    sys.exit(0 if success else 1)
