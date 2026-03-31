"""
WhatsApp Watcher for AI Employee - Silver Tier

This watcher monitors WhatsApp Web for new messages containing
keywords that indicate action is needed (urgent, invoice, payment, etc.).

Uses Playwright for browser automation to interact with WhatsApp Web.

IMPORTANT: WhatsApp Web requires QR code authentication on first run.
The session is persisted in a user data directory for subsequent runs.
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout

from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """
    Watcher that monitors WhatsApp Web for new messages.
    
    Uses Playwright to automate WhatsApp Web and detect messages
    containing keywords that require action.
    """
    
    def __init__(
        self,
        vault_path: str,
        session_path: Optional[str] = None,
        check_interval: int = 60,
        keywords: Optional[List[str]] = None
    ):
        """
        Initialize the WhatsApp watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            session_path: Path to store browser session (defaults to vault/whatsapp_session)
            check_interval: Time in seconds between checks (default: 60)
            keywords: List of keywords that trigger action file creation
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path / 'whatsapp_session'
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        # Keywords that indicate action needed
        self.keywords = keywords or [
            'urgent', 'asap', 'invoice', 'payment', 'help',
            'deadline', 'meeting', 'call', 'review', 'approve',
            'question', 'need', 'please', 'can you'
        ]
        
        # Track processed messages
        self.processed_messages = self._load_processed_messages()
    
    def _load_processed_messages(self) -> set:
        """Load previously processed message IDs from file."""
        cache_file = self.logs_path / 'whatsapp_processed.txt'
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def _save_processed_message(self, msg_id: str):
        """Save a processed message ID to file."""
        self.processed_messages.add(msg_id)
        cache_file = self.logs_path / 'whatsapp_processed.txt'
        with open(cache_file, 'a') as f:
            f.write(msg_id + '\n')
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of new message dictionaries
        """
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list to load (or QR code if not authenticated)
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except PlaywrightTimeout:
                    # Check if QR code is displayed (needs authentication)
                    if page.query_selector('[data-testid="qr-code"]'):
                        self.logger.warning('WhatsApp Web requires QR code authentication')
                        self.logger.warning('Please scan QR code with WhatsApp mobile app')
                        self.logger.warning('Session will be saved for future runs')
                        # Wait for user to scan (max 2 minutes)
                        try:
                            page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                        except PlaywrightTimeout:
                            self.logger.error('QR code scan timeout')
                            browser.close()
                            return []
                
                # Small delay for page to fully load
                time.sleep(2)
                
                # Find unread chats
                unread_chats = self._get_unread_chats(page)
                
                for chat in unread_chats:
                    try:
                        # Click on chat to open it
                        chat.click()
                        time.sleep(1)
                        
                        # Get chat name
                        chat_name = self._get_chat_name(page)
                        
                        # Get recent messages
                        chat_messages = self._get_recent_messages(page)
                        
                        for msg in chat_messages:
                            msg_id = f"{chat_name}_{msg.get('text', '')[:20]}_{msg.get('timestamp', '')}"
                            
                            # Skip if already processed
                            if msg_id in self.processed_messages:
                                continue
                            
                            # Check for keywords
                            text_lower = msg.get('text', '').lower()
                            if any(keyword in text_lower for keyword in self.keywords):
                                msg['chat_name'] = chat_name
                                msg['id'] = msg_id
                                messages.append(msg)
                                self._save_processed_message(msg_id)
                        
                        # Go back to chat list
                        page.click('[data-testid="chat-list"]')
                        time.sleep(0.5)
                        
                    except Exception as e:
                        self.logger.debug(f'Error processing chat: {e}')
                        continue
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f'WhatsApp watcher error: {e}', exc_info=True)
        
        return messages
    
    def _get_unread_chats(self, page: Page) -> List:
        """
        Get list of unread chats from the chat list.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of chat element handles
        """
        try:
            # Look for chats with unread indicator
            unread_selector = '[aria-label*="unread"], [data-testid="unread-chat-title"]'
            return page.query_selector_all(unread_selector)
        except:
            return []
    
    def _get_chat_name(self, page: Page) -> str:
        """
        Get the name of the current chat.
        
        Args:
            page: Playwright page object
            
        Returns:
            Chat name string
        """
        try:
            name_element = page.query_selector('[data-testid="conversation-info-header-chat-title"]')
            if name_element:
                return name_element.inner_text()
            
            # Fallback selector
            name_element = page.query_selector('span[title]')
            if name_element:
                return name_element.get_attribute('title')
            
            return 'Unknown'
        except:
            return 'Unknown'
    
    def _get_recent_messages(self, page: Page) -> List[Dict[str, str]]:
        """
        Get recent messages from the current chat.
        
        Args:
            page: Playwright page object
            
        Returns:
            List of message dictionaries with text and timestamp
        """
        messages = []
        
        try:
            # Find message elements
            message_elements = page.query_selector_all('[data-testid="message"]')
            
            # Get last 5 messages
            for msg_elem in message_elements[-5:]:
                try:
                    # Get message text
                    text_elem = msg_elem.query_selector('span[data-testid="message-text"]')
                    text = text_elem.inner_text() if text_elem else ''
                    
                    # Get timestamp
                    time_elem = msg_elem.query_selector('span[data-testid="message-meta-predate"]')
                    timestamp = time_elem.get_attribute('content') if time_elem else datetime.now().isoformat()
                    
                    # Get sender (for group chats)
                    sender_elem = msg_elem.query_selector('span[data-testid="message-sender"]')
                    sender = sender_elem.inner_text() if sender_elem else 'Unknown'
                    
                    if text:  # Only add non-empty messages
                        messages.append({
                            'text': text,
                            'timestamp': timestamp,
                            'sender': sender
                        })
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f'Error getting messages: {e}')
        
        return messages
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for a WhatsApp message.
        
        Args:
            message: Message dictionary with text, chat_name, timestamp
            
        Returns:
            Path to the created action file
        """
        try:
            # Determine priority based on keywords
            text_lower = message.get('text', '').lower()
            priority = 'high' if any(kw in text_lower for kw in ['urgent', 'asap', 'emergency']) else 'normal'
            
            # Generate unique ID
            unique_id = message.get('id', str(datetime.now().timestamp()))[:8]
            
            # Create action file content
            content = f'''---
type: whatsapp
from: {message.get('chat_name', 'Unknown')}
sender: {message.get('sender', 'Unknown')}
received: {datetime.now().isoformat()}
whatsapp_timestamp: {message.get('timestamp', '')}
priority: {priority}
status: pending
keywords_detected: {[kw for kw in self.keywords if kw in text_lower]}
---

# WhatsApp Message: {message.get('chat_name', 'Unknown')}

## Message Details
- **From**: {message.get('chat_name', 'Unknown')}
- **Sender**: {message.get('sender', 'Unknown')}
- **Received**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Priority**: {priority.upper()}

## Message Content
> {message.get('text', '')}

## Keywords Detected
{', '.join([kw for kw in self.keywords if kw in text_lower]) or 'None'}

## Suggested Actions

### Reply Template
```
Hi {message.get('chat_name', 'there')},

I received your message: "{message.get('text', '')[:50]}..."

[Your response here]

Best regards,
[Your Name]
```

### Action Checklist
- [ ] Read and understand message
- [ ] Determine appropriate response
- [ ] Draft reply
- [ ] Get approval if needed
- [ ] Send reply via WhatsApp MCP or manually
- [ ] Mark as processed
- [ ] Move to /Done when complete

## Approval Required
⚠️ **YES** - All WhatsApp replies require human approval before sending

## Notes
*Add your analysis and response draft here*

---
*Generated by WhatsAppWatcher v0.1 (Silver Tier)*

**Note**: This watcher uses WhatsApp Web automation. Be aware of WhatsApp's Terms of Service.
For production use, consider the official WhatsApp Business API.
'''
            
            # Generate filename and write file
            filename = self.generate_filename('WHATSAPP', unique_id)
            filepath = self.needs_action / filename
            filepath.write_text(content)
            
            # Log the action
            self.log_action('whatsapp_action_created', {
                'chat_name': message.get('chat_name', 'Unknown'),
                'text_preview': message.get('text', '')[:100],
                'priority': priority,
                'action_file': str(filepath)
            })
            
            self.logger.info(f'Created action file for WhatsApp message from {message.get("chat_name", "Unknown")}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}', exc_info=True)
            return None


def main():
    """Main entry point for running the WhatsApp watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee WhatsApp Watcher')
    parser.add_argument(
        '--vault',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--session',
        type=str,
        default=None,
        help='Path to browser session folder'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        default=None,
        help='Keywords to watch for'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent.absolute()
    vault_path = Path(args.vault)
    
    if not vault_path.is_absolute():
        vault_path = script_dir / vault_path
    
    # Install Playwright browsers if needed
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.install()
    except Exception as e:
        print(f'Note: Playwright browsers may need manual installation')
        print(f'Run: playwright install chromium')
    
    watcher = WhatsAppWatcher(
        str(vault_path),
        args.session,
        args.interval,
        args.keywords
    )
    watcher.run()
    
    return 0


if __name__ == '__main__':
    exit(main())
