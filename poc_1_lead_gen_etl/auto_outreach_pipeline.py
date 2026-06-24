import os
import csv
import smtplib
from email.mime.text import MIMEText
import requests
import time

# ==============================================================================
# ANTIGRAVITY LESSON 8: Full Automation & Integration (SMTP & Discord)
# 1. Environment Configurations (.env): Never hardcode credentials in your code.
#    We store them in a separate .env file that is excluded from Git.
# 2. Discord Webhooks: A fast way to send automated notification messages to a 
#    Discord server using simple HTTP POST requests.
# 3. SMTP (Simple Mail Transfer Protocol): The standard internet protocol for
#    sending email. Python's built-in `smtplib` handles this.
# ==============================================================================

ENV_FILE = ".env"

def load_env():
    """Reads a local .env file and loads variables into system environment."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_paths = [ENV_FILE, os.path.join(script_dir, ENV_FILE)]
    loaded = False
    for path in env_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        os.environ[key.strip()] = val.strip()
            print(f"[+] Environment variables loaded from {path}")
            loaded = True
            break
    if not loaded:
        print("[!] Warning: .env file not found. Running with default configurations.")

def send_discord_notification(message):
    """
    Sends an automated notification message to your Discord server via Webhook.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("[!] Skip Discord: No valid DISCORD_WEBHOOK_URL in environment.")
        return
        
    payload = {"content": f"🤖 **Antigravity Lead Gen Bot:** {message}"}
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            print("[+] Discord notification sent successfully!")
        else:
            print(f"[!] Warning: Discord responded with status: {response.status_code}")
    except Exception as e:
        print(f"[!] Error sending Discord notification: {e}")

def send_outreach_email(to_email, subject, body):
    """
    Connects to the SMTP server and sends a cold outreach email.
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD") # Gmail App Password
    
    if not all([smtp_server, smtp_port, sender_email, sender_password]):
        print(f"[!] Skip Email: SMTP credentials not fully configured for: {to_email}")
        return False
        
    try:
        # Create email structure
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        
        # Connect to SMTP server and send
        print(f"[*] Connecting to SMTP server {smtp_server}:{smtp_port}...")
        with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
            server.starttls() # Secure connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [to_email], msg.as_string())
            
        print(f"[+] Email sent successfully to: {to_email}")
        return True
    except Exception as e:
        print(f"[!] Error sending email to {to_email}: {e}")
        return False

def main():
    print("=========================================================")
    print("      ANTIGRAVITY FULL OUTREACH AUTOMATION PIPELINE       ")
    print("=========================================================\n")
    
    load_env()
    
    # 1. RUN THE LEAD MINER (Dynamic Web Search)
    print("\n--- [Step 1: Running Lead Miner] ---")
    import lead_miner
    lead_miner.main()
    
    # 2. RUN THE DRAFT GENERATOR
    print("\n--- [Step 2: Generating Email Drafts] ---")
    import outreach_generator
    outreach_generator.main()
    
    # 3. PARSE LEADS AND TRIGGER NOTIFICATION & EMAILS
    leads_file = "data/qualified_leads.csv"
    if not os.path.exists(leads_file):
        print("[!] Pipeline aborted: qualified_leads.csv was not created.")
        return
        
    qualified_leads = []
    with open(leads_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qualified_leads.append(row)
            
    if not qualified_leads:
        print("[SUCCESS] Pipeline finished: No qualified leads found today.")
        return
        
    print(f"\n--- [Step 3: Processing {len(qualified_leads)} Qualified Leads] ---")
    discord_summary = f"Scanned leads. Found **{len(qualified_leads)} qualified targets**:\n"
    
    for lead in qualified_leads:
        name = lead.get("Company Name")
        url = lead.get("Website")
        platform = lead.get("Platform")
        
        discord_summary += f"• **{name}** ({platform}) - {url}\n"
        
    # Process outbox based on OUTREACH_MODE (test vs live)
    outreach_mode = os.getenv("OUTREACH_MODE", "test").lower()
    test_recipient = os.getenv("TEST_RECIPIENT_EMAIL", "test@example.com")
    
    print(f"[*] Outreach Mode: {outreach_mode.upper()}")
    
    sent_count = 0
    for lead in qualified_leads:
        name = lead.get("Company Name")
        target_email = lead.get("Email")
        draft_file_name = f"outreach_drafts/{name.lower().replace(' ', '_')}_outreach_pitch.txt"
        
        if not target_email or "@" not in target_email:
            print(f"[!] Warning: Lead {name} has no valid email address. Skipping.")
            continue
            
        try:
            if not os.path.exists(draft_file_name):
                print(f"[!] Warning: Draft file not found for {name} ({draft_file_name}). Skipping.")
                continue
                
            with open(draft_file_name, "r", encoding="utf-8") as d_file:
                email_content = d_file.read().strip()
                
            parsed_subject = None
            if email_content.startswith("Subject:"):
                parts = email_content.split("\n", 1)
                parsed_subject = parts[0].replace("Subject:", "").strip()
                email_body = parts[1].strip()
            else:
                email_body = email_content
                
            if outreach_mode == "live":
                subject = parsed_subject if parsed_subject else f"Quick question about inventory updates for {name}"
                recipient = target_email
                print(f"[*] LIVE OUTREACH: Sending pitch to {name} ({recipient})...")
            else:
                file_subject = parsed_subject if parsed_subject else f"Quick question about inventory updates for {name}"
                subject = f"[TEST MODE] {file_subject}"
                recipient = test_recipient
                print(f"[*] TEST MODE: Routing pitch for {name} to your inbox ({recipient})...")
                
            success = send_outreach_email(recipient, subject, email_body)
            if success:
                sent_count += 1
                
            # Delay between SMTP dispatches to prevent server throttling
            time.sleep(3.0)
        except Exception as e:
            print(f"[!] Error processing email for {name}: {e}")
            
    print(f"\n[SUCCESS] Outbox processing complete. Sent {sent_count} emails.")
            
    # Send Summary Alert to Discord
    send_discord_notification(discord_summary)
    
    print("\n[SUCCESS] Full pipeline execution completed.")

if __name__ == "__main__":
    main()
