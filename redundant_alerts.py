#!/usr/bin/env python3
"""
🐺 REDUNDANT ALERT SYSTEM - Multiple fallback layers

Sends alerts through EVERY available channel to ensure you NEVER miss critical info.

Layers:
1. Email (primary)
2. SMS (if configured)
3. Discord (if configured)
4. File system (always)
5. GitHub issue (emergency fallback)

Author: Brokkr
Date: January 2, 2026
"""

import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

def send_email(subject, body, config):
    """Send email via SMTP - PRIMARY alert channel."""
    try:
        email_config = config.get('alerts', {})
        
        if not email_config.get('email') or not email_config.get('email_from'):
            print("   ⏭️  Email not configured, skipping")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = email_config['email_from']
        msg['To'] = email_config['email']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(email_config.get('smtp_server', 'smtp.gmail.com'), 
                             email_config.get('smtp_port', 587))
        server.starttls()
        server.login(email_config['email_from'], email_config['email_password'])
        server.send_message(msg)
        server.quit()
        
        print("   ✅ Email sent")
        return True
        
    except Exception as e:
        print(f"   ❌ Email failed: {e}")
        return False

def send_sms(subject, body, config):
    """Send SMS via Twilio - SECONDARY alert channel."""
    try:
        email_config = config.get('alerts', {})
        
        if not email_config.get('sms'):
            print("   ⏭️  SMS not configured, skipping")
            return False
        
        # Twilio implementation
        from twilio.rest import Client
        
        client = Client(email_config['twilio_sid'], email_config['twilio_token'])
        
        # Truncate for SMS (160 char limit)
        message = f"{subject}\n\n{body[:120]}..."
        
        client.messages.create(
            body=message,
            from_=email_config['twilio_from'],
            to=email_config['sms']
        )
        
        print("   ✅ SMS sent")
        return True
        
    except ImportError:
        print("   ⏭️  Twilio not installed, skipping SMS")
        return False
    except Exception as e:
        print(f"   ❌ SMS failed: {e}")
        return False

def send_discord(subject, body, config):
    """Send Discord webhook - TERTIARY alert channel."""
    try:
        import requests
        
        email_config = config.get('alerts', {})
        webhook_url = email_config.get('discord_webhook')
        
        if not webhook_url:
            print("   ⏭️  Discord not configured, skipping")
            return False
        
        # Discord embed format
        data = {
            "embeds": [{
                "title": subject,
                "description": body[:2000],  # Discord limit
                "color": 16711680 if "RED" in subject else 16776960 if "YELLOW" in subject else 65280,
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        
        response = requests.post(webhook_url, json=data)
        response.raise_for_status()
        
        print("   ✅ Discord sent")
        return True
        
    except Exception as e:
        print(f"   ❌ Discord failed: {e}")
        return False

def save_to_file(subject, body):
    """Save alert to file system - ALWAYS WORKS fallback."""
    try:
        alerts_dir = Path("logs/alerts")
        alerts_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = alerts_dir / f"alert_{timestamp}.txt"
        
        with open(filename, 'w') as f:
            f.write(f"{subject}\n")
            f.write("=" * 70 + "\n")
            f.write(body)
        
        # Also save to "latest" for easy access
        latest = alerts_dir / "alert_latest.txt"
        with open(latest, 'w') as f:
            f.write(f"{subject}\n")
            f.write("=" * 70 + "\n")
            f.write(body)
        
        print(f"   ✅ Saved to {filename}")
        return True
        
    except Exception as e:
        print(f"   ❌ File save failed: {e}")
        return False

def create_github_issue(subject, body):
    """Create GitHub issue - EMERGENCY fallback if all else fails."""
    try:
        import requests
        
        # Only use if GITHUB_TOKEN environment variable is set
        token = os.environ.get('GITHUB_TOKEN')
        repo = os.environ.get('GITHUB_REPOSITORY', 'alexpayne556-collab/trading-companion-2026')
        
        if not token:
            print("   ⏭️  GitHub token not set, skipping issue creation")
            return False
        
        url = f"https://api.github.com/repos/{repo}/issues"
        
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'title': f'🐺 ALERT: {subject}',
            'body': f'```\n{body}\n```',
            'labels': ['alert', 'automated']
        }
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        issue_url = response.json()['html_url']
        print(f"   ✅ GitHub issue created: {issue_url}")
        return True
        
    except Exception as e:
        print(f"   ❌ GitHub issue failed: {e}")
        return False

def send_redundant_alert(subject, body, config, level="INFO"):
    """
    Send alert through ALL available channels with redundancy.
    
    Strategy:
    - Try all channels in parallel
    - At least ONE must succeed
    - Log all successes and failures
    - Return overall success status
    """
    print(f"\n📢 REDUNDANT ALERT SYSTEM - {level}")
    print(f"   Subject: {subject}")
    print(f"   Trying all channels...\n")
    
    results = {
        'email': False,
        'sms': False,
        'discord': False,
        'file': False,
        'github': False
    }
    
    # Layer 1: Email (primary)
    results['email'] = send_email(subject, body, config)
    
    # Layer 2: SMS (if RED alert)
    if level == "RED":
        results['sms'] = send_sms(subject, body, config)
    
    # Layer 3: Discord
    results['discord'] = send_discord(subject, body, config)
    
    # Layer 4: File system (always)
    results['file'] = save_to_file(subject, body)
    
    # Layer 5: GitHub issue (emergency - only if all others failed)
    if not any([results['email'], results['sms'], results['discord']]):
        print("\n   ⚠️  All network channels failed - creating GitHub issue as emergency backup")
        results['github'] = create_github_issue(subject, body)
    
    # Summary
    successful = sum(results.values())
    total = len(results)
    
    print(f"\n📊 ALERT SUMMARY:")
    print(f"   Successful: {successful}/{total}")
    print(f"   Email: {'✅' if results['email'] else '❌'}")
    print(f"   SMS: {'✅' if results['sms'] else '⏭️  (not sent)' if level != 'RED' else '❌'}")
    print(f"   Discord: {'✅' if results['discord'] else '❌'}")
    print(f"   File: {'✅' if results['file'] else '❌'}")
    print(f"   GitHub: {'✅' if results['github'] else '⏭️  (not needed)' if any([results['email'], results['sms'], results['discord']]) else '❌'}")
    
    # At least file system should always work
    if not results['file']:
        print("\n   🚨 CRITICAL: Even file system failed!")
        print("   This should never happen. Check disk space and permissions.")
        return False
    
    # If file worked, we at least have a record
    print(f"\n   ✅ Alert logged. Check logs/alerts/ directory.")
    return True

def main():
    """Test the redundant alert system."""
    import yaml
    
    print("🐺 REDUNDANT ALERT SYSTEM - TEST\n")
    
    # Load config
    try:
        with open("wolf_den_config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ wolf_den_config.yaml not found")
        config = {'alerts': {}}
    
    # Test alert
    subject = "🐺 Test Alert - System Check"
    body = """This is a test of the redundant alert system.

If you received this, at least one channel is working:
✅ Email
✅ SMS (if configured and RED alert)
✅ Discord (if configured)
✅ File system (always)
✅ GitHub issue (emergency fallback)

Time: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

This is a test. No action needed.
"""
    
    success = send_redundant_alert(subject, body, config, level="YELLOW")
    
    if success:
        print("\n✅ Redundant alert system is operational")
        return 0
    else:
        print("\n❌ Redundant alert system has issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
