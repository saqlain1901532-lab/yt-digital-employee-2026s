"""
Orchestrator for AI Employee - Silver Tier

Main orchestration script that:
- Schedules and runs watchers
- Triggers Qwen Code processing
- Manages approval workflows
- Handles periodic tasks (daily briefings, etc.)

Usage:
    python orchestrator.py --vault AI_Employee_Vault

For scheduled execution, use cron (Linux/Mac) or Task Scheduler (Windows).
"""

import os
import sys
import time
import json
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ScheduledTask:
    """Represents a scheduled task."""
    name: str
    schedule: str  # cron-like: hourly, daily, weekly, or interval in seconds
    command: str
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    
    Coordinates watchers, Qwen Code processing, and scheduled tasks.
    """
    
    def __init__(self, vault_path: str, config_path: Optional[str] = None):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            config_path: Path to configuration file (optional)
        """
        self.vault_path = Path(vault_path)
        self.config_path = Path(config_path) if config_path else self.vault_path / 'orchestrator_config.json'
        
        # Sub-paths
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'
        self.briefings = self.vault_path / 'Briefings'
        
        # Ensure directories exist
        for folder in [self.needs_action, self.plans, self.pending_approval,
                       self.approved, self.done, self.logs_path, self.briefings]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config()
        
        # Scheduled tasks
        self.scheduled_tasks = self._init_scheduled_tasks()
        
        # Watcher processes
        self.watcher_processes: List = []
    
    def _setup_logging(self):
        """Setup logging for the orchestrator."""
        log_file = self.logs_path / 'orchestrator.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        
        # Default configuration
        return {
            'watchers': {
                'filesystem': {'enabled': True, 'interval': 60},
                'gmail': {'enabled': False, 'interval': 120},
                'whatsapp': {'enabled': False, 'interval': 60},
            },
            'processing': {
                'auto_process': True,
                'process_interval': 300,  # 5 minutes
            },
            'scheduled_tasks': {
                'daily_briefing': {'enabled': True, 'time': '08:00'},
                'cleanup': {'enabled': True, 'time': '23:00'},
            }
        }
    
    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _init_scheduled_tasks(self) -> List[ScheduledTask]:
        """Initialize scheduled tasks from configuration."""
        tasks = []
        
        # Daily briefing
        if self.config.get('scheduled_tasks', {}).get('daily_briefing', {}).get('enabled'):
            tasks.append(ScheduledTask(
                name='daily_briefing',
                schedule='daily',
                command='generate_briefing',
                next_run=self._next_daily_run('08:00')
            ))
        
        # Hourly processing check
        tasks.append(ScheduledTask(
            name='process_needs_action',
            schedule='300',  # 5 minutes
            command='process_needs_action',
            next_run=datetime.now() + timedelta(minutes=5)
        ))
        
        # Cleanup expired approvals
        tasks.append(ScheduledTask(
            name='cleanup_expired',
            schedule='3600',  # 1 hour
            command='cleanup_expired',
            next_run=datetime.now() + timedelta(hours=1)
        ))
        
        return tasks
    
    def _next_daily_run(self, time_str: str) -> datetime:
        """Calculate next daily run time."""
        hour, minute = map(int, time_str.split(':'))
        now = datetime.now()
        next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        if next_run <= now:
            next_run += timedelta(days=1)
        
        return next_run
    
    def start_watchers(self):
        """Start all enabled watchers."""
        watchers_config = self.config.get('watchers', {})
        script_dir = Path(__file__).parent.absolute()
        
        # File System Watcher (always enabled)
        if watchers_config.get('filesystem', {}).get('enabled', True):
            self.logger.info('Starting File System Watcher...')
            cmd = [sys.executable, str(script_dir / 'watchers' / 'filesystem_watcher.py'),
                   '--vault', str(self.vault_path)]
            proc = subprocess.Popen(cmd)
            self.watcher_processes.append(('filesystem', proc))
        
        # Gmail Watcher
        if watchers_config.get('gmail', {}).get('enabled', False):
            self.logger.info('Starting Gmail Watcher...')
            cmd = [sys.executable, str(script_dir / 'watchers' / 'gmail_watcher.py'),
                   '--vault', str(self.vault_path)]
            proc = subprocess.Popen(cmd)
            self.watcher_processes.append(('gmail', proc))
        
        # WhatsApp Watcher
        if watchers_config.get('whatsapp', {}).get('enabled', False):
            self.logger.info('Starting WhatsApp Watcher...')
            cmd = [sys.executable, str(script_dir / 'watchers' / 'whatsapp_watcher.py'),
                   '--vault', str(self.vault_path)]
            proc = subprocess.Popen(cmd)
            self.watcher_processes.append(('whatsapp', proc))
        
        self.logger.info(f'Started {len(self.watcher_processes)} watchers')
    
    def stop_watchers(self):
        """Stop all watchers."""
        for name, proc in self.watcher_processes:
            self.logger.info(f'Stopping {name} watcher...')
            proc.terminate()
            proc.wait(timeout=5)
        
        self.watcher_processes.clear()
        self.logger.info('All watchers stopped')
    
    def process_needs_action(self):
        """
        Process items in Needs_Action folder using Qwen Code.
        
        This triggers Qwen Code to read pending items and create plans.
        """
        items = list(self.needs_action.glob('*.md'))
        
        if not items:
            self.logger.debug('No items in Needs_Action')
            return
        
        self.logger.info(f'Processing {len(items)} items in Needs_Action')
        
        # Create a processing prompt file
        prompt_file = self.vault_path / '.processing_prompt.txt'
        prompt_file.write_text(f'''
Process the following items in Needs_Action folder:
{chr(10).join([item.name for item in items])}

For each item:
1. Read and understand the content
2. Create a plan in Plans/ folder
3. Execute required actions or create approval requests
4. Move completed items to Done/

Be thorough and follow the Company Handbook guidelines.
''')
        
        # Log the processing
        self._log_event('processing_started', {
            'items': [item.name for item in items],
            'count': len(items)
        })
        
        # In a real implementation, this would trigger Qwen Code
        # For now, we just log that processing is needed
        self.logger.info('Processing triggered. Qwen Code should process these items.')
    
    def generate_briefing(self):
        """Generate a daily/weekly briefing."""
        self.logger.info('Generating daily briefing...')
        
        # Count items in each folder
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        pending_approval_count = len(list(self.pending_approval.glob('*.md')))
        done_today = len([f for f in self.done.glob('*.md') 
                         if f.stat().st_mtime > (datetime.now() - timedelta(days=1)).timestamp()])
        
        # Create briefing file
        briefing_date = datetime.now().strftime('%Y-%m-%d')
        briefing_file = self.briefings / f'{briefing_date}_Daily_Briefing.md'
        
        content = f'''---
generated: {datetime.now().isoformat()}
type: daily_briefing
period: {briefing_date}
---

# Daily Briefing: {briefing_date}

## Summary
- **Items Pending Action**: {needs_action_count}
- **Awaiting Approval**: {pending_approval_count}
- **Completed Today**: {done_today}

## Pending Actions
{self._list_pending_summary()}

## Pending Approvals
{self._list_approvals_summary()}

## Recent Completions
{self._list_recent_done()}

## Recommendations
{self._generate_recommendations()}

---
*Generated by Orchestrator v0.1 (Silver Tier)*
'''
        
        briefing_file.write_text(content)
        
        self.logger.info(f'Briefing generated: {briefing_file}')
        self._log_event('briefing_generated', {'file': str(briefing_file)})
        
        return briefing_file
    
    def _list_pending_summary(self) -> str:
        """Generate summary of pending items."""
        items = list(self.needs_action.glob('*.md'))[:5]
        if not items:
            return '- No pending items'
        
        return '\n'.join([f'- {item.name}' for item in items])
    
    def _list_approvals_summary(self) -> str:
        """Generate summary of pending approvals."""
        items = list(self.pending_approval.glob('*.md'))[:5]
        if not items:
            return '- No pending approvals'
        
        return '\n'.join([f'- {item.name}' for item in items])
    
    def _list_recent_done(self) -> str:
        """List recently completed items."""
        now = datetime.now()
        items = []
        
        for f in self.done.glob('*.md'):
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            if (now - mtime).days < 1:
                items.append(f'- {f.name} ({mtime.strftime("%H:%M")})')
        
        if not items:
            return '- No items completed today'
        
        return '\n'.join(items[:10])
    
    def _generate_recommendations(self) -> str:
        """Generate recommendations based on current state."""
        recommendations = []
        
        pending_count = len(list(self.needs_action.glob('*.md')))
        approval_count = len(list(self.pending_approval.glob('*.md')))
        
        if pending_count > 10:
            recommendations.append(f'- ⚠️ High backlog ({pending_count} items). Consider processing soon.')
        
        if approval_count > 0:
            recommendations.append(f'- 📋 {approval_count} approval(s) awaiting review.')
        
        if not recommendations:
            recommendations.append('- ✅ All systems operating normally.')
        
        return '\n'.join(recommendations)
    
    def cleanup_expired(self):
        """Clean up expired approval requests and old logs."""
        from skills.approval_workflow import ApprovalWorkflowManager
        
        manager = ApprovalWorkflowManager(str(self.vault_path))
        cleaned = manager.cleanup_expired()
        
        if cleaned > 0:
            self.logger.info(f'Cleaned up {cleaned} expired approval requests')
            self._log_event('cleanup_completed', {'expired_approvals': cleaned})
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the audit log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **data
        }
        
        log_file = self.logs_path / f'{datetime.now().strftime("%Y-%m-%d")}_orchestrator.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def run_scheduled_tasks(self):
        """Check and run any due scheduled tasks."""
        now = datetime.now()
        
        for task in self.scheduled_tasks:
            if task.next_run and task.next_run <= now:
                self.logger.info(f'Running scheduled task: {task.name}')
                
                try:
                    if task.command == 'generate_briefing':
                        self.generate_briefing()
                    elif task.command == 'process_needs_action':
                        self.process_needs_action()
                    elif task.command == 'cleanup_expired':
                        self.cleanup_expired()
                    
                    # Schedule next run
                    if task.schedule == 'daily':
                        task.next_run = self._next_daily_run('08:00')
                    else:
                        # Interval in seconds
                        interval = int(task.schedule)
                        task.next_run = now + timedelta(seconds=interval)
                    
                    task.last_run = now
                    
                except Exception as e:
                    self.logger.error(f'Error running task {task.name}: {e}')
    
    def run(self, continuous: bool = True):
        """
        Run the orchestrator.
        
        Args:
            continuous: If True, run continuously. If False, run once and exit.
        """
        self.logger.info('Starting Orchestrator...')
        self.logger.info(f'Vault path: {self.vault_path}')
        
        try:
            # Start watchers
            self.start_watchers()
            
            # Main loop
            while continuous:
                # Run scheduled tasks
                self.run_scheduled_tasks()
                
                # Sleep
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info('Orchestrator stopped by user')
        finally:
            self.stop_watchers()
            self.logger.info('Orchestrator stopped')


def main():
    """Main entry point for the orchestrator."""
    parser = argparse.ArgumentParser(description='AI Employee Orchestrator')
    parser.add_argument(
        '--vault',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to configuration file'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for cron/scheduler)'
    )
    parser.add_argument(
        '--task',
        type=str,
        choices=['briefing', 'process', 'cleanup'],
        help='Run a specific task'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent.absolute()
    vault_path = Path(args.vault)
    
    if not vault_path.is_absolute():
        vault_path = script_dir / vault_path
    
    # Create orchestrator
    orchestrator = Orchestrator(str(vault_path), args.config)
    
    # Run specific task if requested
    if args.task:
        if args.task == 'briefing':
            orchestrator.generate_briefing()
        elif args.task == 'process':
            orchestrator.process_needs_action()
        elif args.task == 'cleanup':
            orchestrator.cleanup_expired()
        return 0
    
    # Run orchestrator
    orchestrator.run(continuous=not args.once)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
