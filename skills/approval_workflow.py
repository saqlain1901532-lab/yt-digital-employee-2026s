"""
Human-in-the-Loop (HITL) Approval Workflow for AI Employee - Silver Tier

This module provides the approval workflow system that requires human
approval before executing sensitive actions like:
- Sending emails to new contacts
- Making payments
- Posting to social media
- Deleting files

The workflow uses file movement between folders to track approval status:
/Pending_Approval/ → /Approved/ → Execute → /Done/
                 → /Rejected/ → Discard
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent


@dataclass
class ApprovalRequest:
    """Represents an approval request."""
    id: str
    action_type: str
    description: str
    created: str
    expires: str
    status: str  # pending, approved, rejected
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]


class ApprovalWorkflowHandler(FileSystemEventHandler):
    """
    Handler for approval workflow file movements.
    
    Monitors the /Approved/ and /Rejected/ folders for moved files
    and triggers appropriate actions.
    """
    
    def __init__(self, workflow_manager: 'ApprovalWorkflowManager'):
        """
        Initialize the handler.
        
        Args:
            workflow_manager: Parent workflow manager instance
        """
        super().__init__()
        self.workflow_manager = workflow_manager
        self.logger = workflow_manager.logger
    
    def on_moved(self, event):
        """
        Handle file move events.
        
        Args:
            event: File system move event
        """
        if event.is_directory:
            return
        
        dest_path = Path(event.dest_path)
        src_path = Path(event.src_path)
        
        # Check if moved to Approved folder
        if '/Approved/' in str(dest_path) or '\\Approved\\' in str(dest_path):
            self.workflow_manager.process_approval(dest_path, approved=True)
        
        # Check if moved to Rejected folder
        elif '/Rejected/' in str(dest_path) or '\\Rejected\\' in str(dest_path):
            self.workflow_manager.process_approval(dest_path, approved=False)


class ApprovalWorkflowManager:
    """
    Manages the Human-in-the-Loop approval workflow.
    
    Creates approval requests, tracks their status, and executes
    approved actions.
    """
    
    def __init__(self, vault_path: str):
        """
        Initialize the approval workflow manager.
        
        Args:
            vault_path: Path to the Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_folder = self.vault_path / 'Pending_Approval'
        self.approved_folder = self.vault_path / 'Approved'
        self.rejected_folder = self.vault_path / 'Rejected'
        self.done_folder = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'
        
        # Ensure folders exist
        for folder in [self.pending_folder, self.approved_folder, 
                       self.rejected_folder, self.done_folder, self.logs_path]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Registered action handlers
        self.action_handlers: Dict[str, Callable] = {}
        
        # Setup file watcher for approval folder
        self.observer = Observer()
        self.handler = ApprovalWorkflowHandler(self)
        self.observer.schedule(self.handler, str(self.approved_folder), recursive=False)
        self.observer.schedule(self.handler, str(self.rejected_folder), recursive=False)
    
    def _setup_logging(self):
        """Setup logging for the workflow manager."""
        import logging
        log_file = self.logs_path / 'approval_workflow.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def register_action_handler(self, action_type: str, handler: Callable):
        """
        Register a handler for a specific action type.
        
        Args:
            action_type: Type of action (e.g., 'send_email', 'linkedin_post')
            handler: Function to call when action is approved
        """
        self.action_handlers[action_type] = handler
        self.logger.info(f'Registered handler for action type: {action_type}')
    
    def create_approval_request(
        self,
        action_type: str,
        description: str,
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        expiry_hours: int = 24
    ) -> Path:
        """
        Create a new approval request.
        
        Args:
            action_type: Type of action requiring approval
            description: Human-readable description
            parameters: Action parameters
            metadata: Additional metadata
            expiry_hours: Hours until request expires
            
        Returns:
            Path to the created approval request file
        """
        # Generate unique ID
        request_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate expiry
        created = datetime.now()
        expires = datetime.fromtimestamp(created.timestamp() + (expiry_hours * 3600))
        
        # Create request object
        request = ApprovalRequest(
            id=request_id,
            action_type=action_type,
            description=description,
            created=created.isoformat(),
            expires=expires.isoformat(),
            status='pending',
            parameters=parameters,
            metadata=metadata or {}
        )
        
        # Create markdown file
        content = self._create_approval_file_content(request)
        filename = f'{request_id}.md'
        filepath = self.pending_folder / filename
        filepath.write_text(content)
        
        self.logger.info(f'Created approval request: {request_id}')
        
        # Log the request
        self._log_event('approval_created', asdict(request))
        
        return filepath
    
    def _create_approval_file_content(self, request: ApprovalRequest) -> str:
        """
        Create markdown content for approval request file.
        
        Args:
            request: Approval request object
            
        Returns:
            Markdown content string
        """
        params_json = json.dumps(request.parameters, indent=2, default=str)
        metadata_json = json.dumps(request.metadata, indent=2, default=str)
        
        return f'''---
type: approval_request
id: {request.id}
action_type: {request.action_type}
created: {request.created}
expires: {request.expires}
status: {request.status}
---

# Approval Request: {request.action_type}

## Description
{request.description}

## Created
{request.created}

## Expires
{request.expires}

## Parameters
```json
{params_json}
```

## Metadata
```json
{metadata_json}
```

## Instructions

### To Approve
1. Review the request details above
2. Move this file to the `/Approved/` folder
3. The action will be executed automatically

### To Reject
1. Move this file to the `/Rejected/` folder
2. The request will be discarded

### To Request Changes
1. Edit this file with your comments
2. Leave in `/Pending_Approval/` folder

---
*Generated by Approval Workflow Manager v0.1 (Silver Tier)*

**Note**: This request will expire on {request.expires}.
'''
    
    def process_approval(self, filepath: Path, approved: bool):
        """
        Process an approval or rejection.
        
        Args:
            filepath: Path to the approval file
            approved: True if approved, False if rejected
        """
        try:
            # Read the file
            content = filepath.read_text()
            
            # Parse frontmatter to get request details
            request_data = self._parse_frontmatter(content)
            request_id = request_data.get('id', filepath.stem)
            action_type = request_data.get('action_type', 'unknown')
            
            if approved:
                self.logger.info(f'Approval granted: {request_id}')
                self._log_event('approval_granted', {'id': request_id, 'action_type': action_type})
                
                # Execute the action
                if action_type in self.action_handlers:
                    try:
                        # Parse parameters from content
                        params = self._parse_parameters(content)
                        
                        # Call the handler
                        handler = self.action_handlers[action_type]
                        result = handler(params)
                        
                        self.logger.info(f'Action executed: {request_id}')
                        self._log_event('action_executed', {
                            'id': request_id,
                            'action_type': action_type,
                            'result': str(result)
                        })
                        
                        # Update file with result
                        self._append_result(filepath, result)
                        
                        # Move to Done
                        done_path = self.done_folder / filepath.name
                        shutil.move(str(filepath), str(done_path))
                        
                    except Exception as e:
                        self.logger.error(f'Error executing action: {e}')
                        self._log_event('action_failed', {
                            'id': request_id,
                            'error': str(e)
                        })
                else:
                    self.logger.warning(f'No handler for action type: {action_type}')
            else:
                self.logger.info(f'Approval rejected: {request_id}')
                self._log_event('approval_rejected', {'id': request_id, 'action_type': action_type})
                
                # Just leave in Rejected folder
                
        except Exception as e:
            self.logger.error(f'Error processing approval: {e}', exc_info=True)
    
    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown content."""
        import re
        
        match = re.search(r'^---\s*\n(.*?)\n---\s*$', content, re.DOTALL)
        if not match:
            return {}
        
        frontmatter = match.group(1)
        data = {}
        
        for line in frontmatter.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        
        return data
    
    def _parse_parameters(self, content: str) -> Dict[str, Any]:
        """Parse parameters JSON from markdown content."""
        import re
        import json
        
        # Find parameters JSON block
        match = re.search(r'## Parameters\s*```json\s*(.*?)\s*```', content, re.DOTALL)
        if not match:
            return {}
        
        try:
            return json.loads(match.group(1))
        except:
            return {}
    
    def _append_result(self, filepath: Path, result: Any):
        """Append execution result to the approval file."""
        content = filepath.read_text()
        
        result_section = f'''
## Execution Result
- **Status**: Success
- **Timestamp**: {datetime.now().isoformat()}
- **Result**: {result}

---
*Action completed by Approval Workflow Manager*
'''
        content = content.replace('---\n*Generated by Approval Workflow Manager', 
                                   result_section + '\n---\n*Generated by Approval Workflow Manager')
        filepath.write_text(content)
    
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to the audit log."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            **data
        }
        
        log_file = self.logs_path / f'{datetime.now().strftime("%Y-%m-%d")}_approvals.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def start_watcher(self):
        """Start the file watcher for approval folders."""
        self.observer.start()
        self.logger.info('Approval workflow watcher started')
    
    def stop_watcher(self):
        """Stop the file watcher."""
        self.observer.stop()
        self.observer.join()
        self.logger.info('Approval workflow watcher stopped')
    
    def list_pending_requests(self) -> List[ApprovalRequest]:
        """
        List all pending approval requests.
        
        Returns:
            List of pending approval requests
        """
        requests = []
        
        for filepath in self.pending_folder.glob('*.md'):
            content = filepath.read_text()
            data = self._parse_frontmatter(content)
            
            if data.get('status') == 'pending':
                requests.append(ApprovalRequest(
                    id=data.get('id', filepath.stem),
                    action_type=data.get('action_type', 'unknown'),
                    description='',
                    created=data.get('created', ''),
                    expires=data.get('expires', ''),
                    status='pending',
                    parameters={},
                    metadata={}
                ))
        
        return requests
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired approval requests.
        
        Returns:
            Number of requests cleaned up
        """
        cleaned = 0
        now = datetime.now()
        
        for filepath in self.pending_folder.glob('*.md'):
            content = filepath.read_text()
            data = self._parse_frontmatter(content)
            
            expires_str = data.get('expires')
            if expires_str:
                try:
                    expires = datetime.fromisoformat(expires_str)
                    if expires < now:
                        # Move to Rejected
                        shutil.move(str(filepath), str(self.rejected_folder / filepath.name))
                        self.logger.info(f'Cleaned up expired request: {data.get("id")}')
                        cleaned += 1
                except:
                    pass
        
        return cleaned


# Example action handlers
def send_email_handler(params: Dict[str, Any]) -> str:
    """Handler for send_email action type."""
    # This would integrate with the Email MCP server
    return f"Email sent to {params.get('to', 'unknown')}"


def linkedin_post_handler(params: Dict[str, Any]) -> str:
    """Handler for linkedin_post action type."""
    # This would integrate with LinkedIn automation
    return f"LinkedIn post created: {params.get('text', '')[:50]}..."


# Main entry point
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Approval Workflow Manager')
    parser.add_argument('--vault', type=str, default='../AI_Employee_Vault',
                       help='Path to Obsidian vault')
    parser.add_argument('--watch', action='store_true',
                       help='Run in watch mode')
    
    args = parser.parse_args()
    
    script_dir = Path(__file__).parent.absolute()
    vault_path = Path(args.vault)
    if not vault_path.is_absolute():
        vault_path = script_dir / vault_path
    
    manager = ApprovalWorkflowManager(str(vault_path))
    
    # Register default handlers
    manager.register_action_handler('send_email', send_email_handler)
    manager.register_action_handler('linkedin_post', linkedin_post_handler)
    
    if args.watch:
        manager.start_watcher()
        print('Approval Workflow Manager running. Press Ctrl+C to stop.')
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.stop_watcher()
    else:
        # List pending requests
        pending = manager.list_pending_requests()
        print(f'Pending approval requests: {len(pending)}')
        for req in pending:
            print(f'  - {req.id}: {req.action_type}')
