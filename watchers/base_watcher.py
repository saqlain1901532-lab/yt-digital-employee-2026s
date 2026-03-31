"""
Base Watcher Module for AI Employee

This module provides the abstract base class for all watcher scripts.
Watchers monitor various inputs (Gmail, WhatsApp, filesystem, etc.) and
create actionable files in the Needs_Action folder for Claude to process.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Any, Optional


class BaseWatcher(ABC):
    """
    Abstract base class for all AI Employee watchers.
    
    Watchers run continuously, monitoring their respective data sources
    and creating markdown files in the Needs_Action folder when new
    items requiring attention are detected.
    """
    
    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            check_interval: Time in seconds between checks (default: 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs_path = self.vault_path / 'Logs'
        self.check_interval = check_interval
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Track processed items to avoid duplicates
        self.processed_ids: set = set()
        
    def _setup_logging(self):
        """Configure logging for the watcher."""
        log_file = self.logs_path / f"{self.__class__.__name__}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check the data source for new items.
        
        Returns:
            List of new items that need processing
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a markdown action file for an item.
        
        Args:
            item: The item to create an action file for
            
        Returns:
            Path to the created file, or None if creation failed
            
        Raises:
            NotImplementedError: Must be implemented by subclass
        """
        pass
    
    def run(self):
        """
        Main run loop for the watcher.
        
        Continuously checks for updates and creates action files.
        Runs until interrupted (Ctrl+C).
        """
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')
        
        try:
            while True:
                try:
                    items = self.check_for_updates()
                    self.logger.debug(f'Found {len(items)} new items')
                    
                    for item in items:
                        filepath = self.create_action_file(item)
                        if filepath:
                            self.logger.info(f'Created action file: {filepath.name}')
                    
                except Exception as e:
                    self.logger.error(f'Error processing items: {e}', exc_info=True)
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info(f'{self.__class__.__name__} stopped by user')
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            raise
    
    def generate_filename(self, prefix: str, unique_id: str) -> str:
        """
        Generate a unique filename for an action file.
        
        Args:
            prefix: File prefix (e.g., 'EMAIL', 'WHATSAPP', 'FILE')
            unique_id: Unique identifier for the item
            
        Returns:
            Filename with .md extension
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # Sanitize unique_id for filesystem
        safe_id = "".join(c for c in unique_id if c.isalnum() or c in ('-', '_'))[:50]
        return f"{prefix}_{safe_id}_{timestamp}.md"
    
    def log_action(self, action_type: str, details: dict):
        """
        Log an action to the audit log.
        
        Args:
            action_type: Type of action (e.g., 'file_created', 'item_processed')
            details: Dictionary of action details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.__class__.__name__,
            'action_type': action_type,
            **details
        }

        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with open(log_file, 'a') as f:
            import json
            f.write(json.dumps(log_entry) + '\n')
