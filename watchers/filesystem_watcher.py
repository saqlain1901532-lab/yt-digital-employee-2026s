"""
File System Watcher for AI Employee

This watcher monitors a designated "drop folder" for new files.
When files are added, it creates corresponding action files in the
Needs_Action folder for Claude to process.

This is the simplest watcher to set up and test for Bronze Tier.
"""

import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from base_watcher import BaseWatcher


class FileDropHandler(FileSystemEventHandler):
    """
    Event handler for file system watcher.
    
    Monitors for new files in the drop folder and triggers
    action file creation.
    """
    
    def __init__(self, watcher: 'FileSystemWatcher'):
        """
        Initialize the handler.
        
        Args:
            watcher: Parent FileSystemWatcher instance
        """
        super().__init__()
        self.watcher = watcher
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def on_created(self, event):
        """
        Handle file creation events.
        
        Args:
            event: File system event object
        """
        if event.is_directory:
            return
        
        self.logger.info(f'New file detected: {event.src_path}')
        self.watcher.process_new_file(Path(event.src_path))


class FileSystemWatcher(BaseWatcher):
    """
    Watcher that monitors a drop folder for new files.
    
    When files are added to the drop folder, this watcher creates
    markdown action files in the Needs_Action folder with metadata
    about the new file.
    """
    
    def __init__(self, vault_path: str, drop_folder: Optional[str] = None):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            drop_folder: Path to the drop folder (defaults to vault/Drop)
        """
        super().__init__(vault_path, check_interval=1)  # 1 second for real-time
        
        self.drop_folder = Path(drop_folder) if drop_folder else self.vault_path / 'Drop'
        self.drop_folder.mkdir(parents=True, exist_ok=True)
        
        # Track file hashes to detect new files
        self.known_files: Dict[str, str] = {}
        self._load_existing_files()
        
        # Setup observer for real-time monitoring
        self.observer = Observer()
        self.handler = FileDropHandler(self)
        self.observer.schedule(self.handler, str(self.drop_folder), recursive=False)
    
    def _load_existing_files(self):
        """Load hashes of existing files to avoid processing old files on startup."""
        self.logger.info('Loading existing files in drop folder...')
        for file_path in self.drop_folder.iterdir():
            if file_path.is_file():
                file_hash = self._calculate_hash(file_path)
                self.known_files[str(file_path)] = file_hash
                self.logger.debug(f'Known file: {file_path.name}')
        
        self.logger.info(f'Loaded {len(self.known_files)} existing files')
    
    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string
        """
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def check_for_updates(self) -> List[Path]:
        """
        Check for new files in the drop folder.
        
        Returns:
            List of new file paths
        """
        new_files = []
        
        for file_path in self.drop_folder.iterdir():
            if not file_path.is_file():
                continue
            
            file_str = str(file_path)
            if file_str not in self.known_files:
                # New file detected
                file_hash = self._calculate_hash(file_path)
                self.known_files[file_str] = file_hash
                new_files.append(file_path)
                self.logger.info(f'New file found: {file_path.name}')
        
        return new_files
    
    def process_new_file(self, file_path: Path):
        """
        Process a newly detected file.
        
        Args:
            file_path: Path to the new file
        """
        # Verify it's actually new
        file_str = str(file_path)
        if file_str in self.known_files:
            return
        
        # Calculate hash and track
        file_hash = self._calculate_hash(file_path)
        self.known_files[file_str] = file_hash
        
        # Create action file
        self.create_action_file(file_path)
    
    def create_action_file(self, file_path: Path) -> Optional[Path]:
        """
        Create a markdown action file for a new file.
        
        Args:
            file_path: Path to the new file
            
        Returns:
            Path to the created action file
        """
        try:
            # Get file metadata
            stat = file_path.stat()
            file_size = stat.st_size
            created_time = datetime.fromtimestamp(stat.st_ctime)
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            
            # Generate unique ID from file hash
            file_hash = self._calculate_hash(file_path)
            unique_id = file_hash[:8]
            
            # Create action file content
            content = f'''---
type: file_drop
original_name: {file_path.name}
original_path: {file_path.absolute()}
size: {self._format_size(file_size)}
size_bytes: {file_size}
created: {created_time.isoformat()}
modified: {modified_time.isoformat()}
received: {datetime.now().isoformat()}
priority: normal
status: pending
file_hash: {file_hash}
---

# File Drop for Processing

## File Information
- **Original Name**: {file_path.name}
- **Size**: {self._format_size(file_size)}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## File Location
- **Drop Folder**: `{file_path.absolute()}`
- **Vault**: `{self.vault_path}`

## Suggested Actions
- [ ] Review file contents
- [ ] Determine appropriate action
- [ ] Process and move to /Done
- [ ] Archive if no action needed

## Notes
*Add your analysis and actions here*

---
*Generated by FileSystemWatcher v0.1*
'''
            
            # Generate filename and write file
            filename = self.generate_filename('FILE', unique_id)
            filepath = self.needs_action / filename
            filepath.write_text(content)
            
            # Log the action
            self.log_action('file_created', {
                'source_file': str(file_path),
                'action_file': str(filepath),
                'file_size': file_size
            })
            
            self.logger.info(f'Created action file: {filepath.name}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}', exc_info=True)
            return None
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def run_with_observer(self):
        """
        Run the watcher using the real-time observer.
        
        This is more efficient than polling and provides instant
        detection of new files.
        """
        self.logger.info(f'Starting FileSystemWatcher with real-time monitoring')
        self.logger.info(f'Drop folder: {self.drop_folder}')
        
        try:
            # Start the observer
            self.observer.start()
            self.logger.info('File observer started - watching for new files...')
            
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info('Watcher stopped by user')
            self.observer.stop()
        except Exception as e:
            self.logger.error(f'Fatal error: {e}', exc_info=True)
            self.observer.stop()
        
        self.observer.join()
        self.logger.info('Observer stopped')


def main():
    """Main entry point for running the file system watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee File System Watcher')
    parser.add_argument(
        '--vault',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--drop-folder',
        type=str,
        default=None,
        help='Path to drop folder (defaults to vault/Drop)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths relative to script location
    script_dir = Path(__file__).parent.absolute()
    vault_path = Path(args.vault)
    if not vault_path.is_absolute():
        vault_path = script_dir / vault_path
    
    watcher = FileSystemWatcher(str(vault_path), args.drop_folder)
    watcher.run_with_observer()


if __name__ == '__main__':
    main()
