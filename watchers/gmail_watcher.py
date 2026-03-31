"""
Gmail Watcher for AI Employee - Silver Tier

This watcher monitors Gmail for new unread/important emails and creates
action files in the Needs_Action folder for Qwen Code to process.

Setup Requirements:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json
4. Run authentication flow once to generate token.json
"""

import os
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from email import message_from_bytes

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from base_watcher import BaseWatcher


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """
    Watcher that monitors Gmail for new unread/important emails.
    
    Creates markdown action files in Needs_Action folder with
    email content and suggested actions.
    """
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str,
        token_path: Optional[str] = None,
        check_interval: int = 120
    ):
        """
        Initialize the Gmail watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root directory
            credentials_path: Path to Gmail OAuth credentials.json
            token_path: Path to store token.json (defaults to credentials path dir)
            check_interval: Time in seconds between checks (default: 120)
        """
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path) if token_path else self.credentials_path.parent / 'token.json'
        
        # Keywords that indicate urgent emails
        self.urgent_keywords = ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'emergency']
        
        # Known contacts (can be extended)
        self.known_contacts = set()
        self._load_known_contacts()
        
        # Initialize Gmail service
        self.service = self._authenticate()
        
        # Track processed message IDs
        self.processed_ids = self._load_processed_ids()
    
    def _load_known_contacts(self):
        """Load known contacts from Company Handbook or config."""
        # In production, parse from Company_Handbook.md or separate config
        self.known_contacts = {
            # Add your known contacts here
            # 'client@example.com',
            # 'partner@company.com',
        }
    
    def _load_processed_ids(self) -> set:
        """Load previously processed message IDs from file."""
        cache_file = self.logs_path / 'gmail_processed_ids.txt'
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def _save_processed_id(self, message_id: str):
        """Save a processed message ID to file."""
        self.processed_ids.add(message_id)
        cache_file = self.logs_path / 'gmail_processed_ids.txt'
        with open(cache_file, 'a') as f:
            f.write(message_id + '\n')
    
    def _authenticate(self):
        """
        Authenticate with Gmail API.
        
        Returns:
            Authorized Gmail API service instance
        """
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new unread/important emails.
        
        Returns:
            List of new email message dictionaries
        """
        try:
            # Search for unread messages
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
            
            return new_messages
            
        except HttpError as error:
            self.logger.error(f'Gmail API error: {error}')
            return []
    
    def create_action_file(self, message: Dict[str, Any]) -> Optional[Path]:
        """
        Create a markdown action file for a new email.
        
        Args:
            message: Gmail message dictionary
            
        Returns:
            Path to the created action file
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            
            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            to_email = headers.get('To', '')
            date = headers.get('Date', '')
            
            # Extract body
            body = self._extract_body(msg)
            
            # Determine priority
            priority = self._determine_priority(subject, body, from_email)
            
            # Check if from known contact
            is_known = self._is_known_contact(from_email)
            
            # Generate unique ID
            unique_id = message['id'][:8]
            
            # Create action file content
            content = f'''---
type: email
from: {from_email}
to: {to_email}
subject: {subject}
date: {date}
received: {datetime.now().isoformat()}
priority: {priority}
status: unread
is_known_contact: {str(is_known).lower()}
gmail_id: {message['id']}
---

# Email: {subject}

## Sender Information
- **From**: {from_email}
- **Known Contact**: {'✅ Yes' if is_known else '❌ No'}
- **Priority**: {priority.upper()}

## Email Content
{body}

## Suggested Actions

### Quick Reply Template
```
Dear {from_email.split('@')[0]},

Thank you for your email regarding "{subject}".

[Your response here]

Best regards,
[Your Name]
```

### Action Checklist
- [ ] Read and understand email content
- [ ] Determine if response is needed
- [ ] Draft response (if needed)
- [ ] Get approval if sending to new contact
- [ ] Send response via Email MCP
- [ ] Mark email as read in Gmail
- [ ] Move to /Done when complete

## Approval Required
{'⚠️ **YES** - Sender is NOT a known contact. Approval required before sending reply.' if not is_known else '✅ **NO** - Known contact, can auto-reply'}

## Notes
*Add your analysis and response draft here*

---
*Generated by GmailWatcher v0.1 (Silver Tier)*
'''
            
            # Generate filename and write file
            filename = self.generate_filename('EMAIL', unique_id)
            filepath = self.needs_action / filename
            filepath.write_text(content)
            
            # Log the action
            self.log_action('email_action_created', {
                'gmail_id': message['id'],
                'from': from_email,
                'subject': subject,
                'priority': priority,
                'action_file': str(filepath)
            })
            
            # Mark as processed
            self._save_processed_id(message['id'])
            
            self.logger.info(f'Created action file for email: {subject}')
            return filepath
            
        except Exception as e:
            self.logger.error(f'Error creating action file: {e}', exc_info=True)
            return None
    
    def _extract_body(self, msg: Dict[str, Any]) -> str:
        """
        Extract the plain text body from a Gmail message.
        
        Args:
            msg: Gmail message dictionary
            
        Returns:
            Email body text
        """
        def get_payload(msg):
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif 'parts' in part:
                        return get_payload(part)
            elif msg['payload']['body'].get('data'):
                data = msg['payload']['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
            return ''
        
        body = get_payload(msg)
        return body[:2000] + '...' if len(body) > 2000 else body
    
    def _determine_priority(self, subject: str, body: str, from_email: str) -> str:
        """
        Determine email priority based on content.
        
        Args:
            subject: Email subject
            body: Email body
            from_email: Sender email address
            
        Returns:
            Priority level: 'high', 'normal', or 'low'
        """
        text = (subject + ' ' + body).lower()
        
        # Check for urgent keywords
        if any(keyword in text for keyword in self.urgent_keywords):
            return 'high'
        
        # Check if from known contact
        if self._is_known_contact(from_email):
            return 'normal'
        
        # Default to normal for unknown contacts
        return 'normal'
    
    def _is_known_contact(self, email: str) -> bool:
        """
        Check if email is from a known contact.
        
        Args:
            email: Email address to check
            
        Returns:
            True if known contact
        """
        # Extract just the email address (in case it's "Name <email@domain.com>")
        if '<' in email and '>' in email:
            email = email.split('<')[1].split('>')[0].strip()
        
        return email in self.known_contacts
    
    def mark_as_read(self, gmail_id: str):
        """
        Mark a Gmail message as read.
        
        Args:
            gmail_id: Gmail message ID
        """
        try:
            self.service.users().messages().modify(
                userId='me',
                id=gmail_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            self.logger.info(f'Marked message {gmail_id} as read')
        except HttpError as error:
            self.logger.error(f'Error marking message as read: {error}')


def main():
    """Main entry point for running the Gmail watcher."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Employee Gmail Watcher')
    parser.add_argument(
        '--vault',
        type=str,
        default='../AI_Employee_Vault',
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        default='credentials.json',
        help='Path to Gmail OAuth credentials.json'
    )
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help='Path to token.json (optional)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=120,
        help='Check interval in seconds (default: 120)'
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    script_dir = Path(__file__).parent.absolute()
    vault_path = Path(args.vault)
    credentials_path = Path(args.credentials)
    
    if not vault_path.is_absolute():
        vault_path = script_dir / vault_path
    if not credentials_path.is_absolute():
        credentials_path = script_dir / credentials_path
    
    # Check credentials exist
    if not credentials_path.exists():
        print(f'Error: Credentials file not found: {credentials_path}')
        print('Please download credentials.json from Google Cloud Console')
        return 1
    
    watcher = GmailWatcher(
        str(vault_path),
        str(credentials_path),
        args.token,
        args.interval
    )
    watcher.run()
    
    return 0


if __name__ == '__main__':
    exit(main())
