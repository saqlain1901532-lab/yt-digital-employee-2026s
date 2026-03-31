"""
LinkedIn Automation Skill for AI Employee - Silver Tier

This module provides LinkedIn automation capabilities for posting
business updates to generate sales and engagement.

Uses Playwright for browser automation since LinkedIn API access
is restricted.

IMPORTANT: Be aware of LinkedIn's Terms of Service when automating.
Use responsibly and consider rate limiting.
"""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from playwright.sync_api import sync_playwright, Page, TimeoutError as PlaywrightTimeout


class LinkedInAutomation:
    """
    LinkedIn automation for posting business updates.
    
    Supports:
    - Creating text posts
    - Creating posts with images
    - Scheduling posts (via approval workflow)
    - Analytics retrieval
    """
    
    def __init__(self, session_path: Optional[str] = None):
        """
        Initialize LinkedIn automation.
        
        Args:
            session_path: Path to store browser session (defaults to ./linkedin_session)
        """
        self.session_path = Path(session_path or './linkedin_session')
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logged_in = False
    
    def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn.
        
        Args:
            email: LinkedIn email
            password: LinkedIn password
            
        Returns:
            True if login successful
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,  # Show browser for 2FA if needed
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/login', timeout=60000)
                
                # Check if already logged in
                if 'feed' in page.url:
                    self.logged_in = True
                    browser.close()
                    return True
                
                # Fill login form
                page.fill('#username', email)
                page.fill('#password', password)
                page.click('button[type="submit"]')
                
                # Wait for navigation to feed
                try:
                    page.wait_for_url('**/feed/**', timeout=30000)
                    self.logged_in = True
                    browser.close()
                    return True
                except PlaywrightTimeout:
                    # Check for 2FA or error
                    if 'checkpoint' in page.url:
                        print('⚠️ Two-factor authentication required. Please complete manually.')
                        # Wait for user to complete 2FA
                        try:
                            page.wait_for_url('**/feed/**', timeout=120000)
                            self.logged_in = True
                            browser.close()
                            return True
                        except PlaywrightTimeout:
                            browser.close()
                            return False
                    browser.close()
                    return False
                    
        except Exception as e:
            print(f'Login error: {e}')
            return False
    
    def create_post(self, text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a LinkedIn post.
        
        Args:
            text: Post text content
            image_path: Optional path to image to attach
            
        Returns:
            Dictionary with post result
        """
        if not self.logged_in:
            return {'success': False, 'error': 'Not logged in'}
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    user_data_dir=str(self.session_path),
                    headless=False,
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/feed', timeout=60000)
                time.sleep(3)  # Wait for page to load
                
                # Click on "Start a post"
                try:
                    start_post_btn = page.query_selector('[aria-label="Start a post"]')
                    if not start_post_btn:
                        start_post_btn = page.query_selector('button:has-text("Start a post")')
                    if start_post_btn:
                        start_post_btn.click()
                        time.sleep(2)
                    else:
                        # Alternative: find the post input directly
                        page.click('div[role="textbox"]', timeout=10000)
                except Exception as e:
                    print(f'Error clicking start post: {e}')
                    browser.close()
                    return {'success': False, 'error': 'Could not open post editor'}
                
                # Find the post input field and type text
                try:
                    # LinkedIn uses a contenteditable div
                    post_input = page.query_selector('div[role="textbox"][contenteditable="true"]')
                    if post_input:
                        # Clear existing content
                        post_input.fill('')
                        time.sleep(0.5)
                        # Type new content
                        post_input.fill(text)
                        time.sleep(1)
                except Exception as e:
                    print(f'Error filling post text: {e}')
                    browser.close()
                    return {'success': False, 'error': 'Could not enter post text'}
                
                # Add image if provided
                if image_path:
                    try:
                        # Click on media/photo button
                        media_btn = page.query_selector('button:has-text("Media")')
                        if not media_btn:
                            media_btn = page.query_selector('button[aria-label*="photo"]')
                        if media_btn:
                            media_btn.click()
                            time.sleep(1)
                            
                            # Upload file
                            file_input = page.query_selector('input[type="file"]')
                            if file_input:
                                file_input.set_input_files(str(image_path))
                                time.sleep(2)
                    except Exception as e:
                        print(f'Error adding image: {e}')
                        # Continue without image
                
                # Click Post button
                try:
                    post_button = page.query_selector('button:has-text("Post")')
                    if post_button:
                        post_button.click()
                        time.sleep(3)
                        
                        # Wait for confirmation
                        if 'feed' in page.url:
                            browser.close()
                            return {
                                'success': True,
                                'timestamp': datetime.now().isoformat(),
                                'text_preview': text[:100],
                                'image': image_path is not None
                            }
                except Exception as e:
                    print(f'Error clicking post button: {e}')
                
                browser.close()
                return {'success': False, 'error': 'Post could not be submitted'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get LinkedIn post analytics.
        
        Args:
            days: Number of days to retrieve analytics for
            
        Returns:
            Dictionary with analytics data
        """
        # This is a simplified implementation
        # Full analytics would require more complex scraping
        return {
            'period_days': days,
            'posts': 0,
            'impressions': 0,
            'engagement_rate': 0,
            'note': 'Analytics retrieval requires additional implementation'
        }


def create_linkedin_post_skill(
    text: str,
    image_path: Optional[str] = None,
    requires_approval: bool = True,
    vault_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Skill function for creating LinkedIn posts.
    
    This function is designed to be called by Qwen Code as part of
    the AI Employee workflow.
    
    Args:
        text: Post content
        image_path: Optional image path
        requires_approval: Whether approval is required (default: True)
        vault_path: Path to vault for approval workflow
        
    Returns:
        Result dictionary
    """
    # For Silver Tier, all LinkedIn posts require approval
    if requires_approval and vault_path:
        # Create approval request file
        vault = Path(vault_path)
        approval_file = vault / 'Pending_Approval' / f'LINKEDIN_POST_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        
        content = f'''---
type: linkedin_post
created: {datetime.now().isoformat()}
status: pending_approval
requires_approval: true
---

# LinkedIn Post Approval Request

## Post Content
{text}

## Image
{f'![Image]({image_path})' if image_path else 'No image attached'}

## To Approve
1. Review the post content above
2. Move this file to /Approved/ to post
3. Move to /Rejected/ to cancel

## Auto-Post After Approval
Once approved, the post will be published to LinkedIn.

---
*Generated by LinkedIn Automation Skill v0.1*
'''
        
        approval_file.parent.mkdir(parents=True, exist_ok=True)
        approval_file.write_text(content)
        
        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': str(approval_file),
            'message': 'Approval request created. Move file to /Approved/ to post.'
        }
    
    # Direct post (not recommended for Silver Tier)
    automation = LinkedInAutomation()
    result = automation.create_post(text, image_path)
    
    return result


# Example usage
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Post Automation')
    parser.add_argument('--text', type=str, required=True, help='Post text')
    parser.add_argument('--image', type=str, default=None, help='Image path')
    parser.add_argument('--vault', type=str, default=None, help='Vault path for approval workflow')
    
    args = parser.parse_args()
    
    result = create_linkedin_post_skill(args.text, args.image, vault_path=args.vault)
    print(json.dumps(result, indent=2))
