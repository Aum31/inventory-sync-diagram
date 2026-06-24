import requests
from bs4 import BeautifulSoup
import os
import json
import time

# ==============================================================================
# ANTIGRAVITY LESSON 10: Scraping Protected Sites via RSS Feeds
# 1. Cloudflare Bypass: Major platforms like Upwork block raw web scraping. 
#    However, they expose open XML RSS Feeds for job searches so developers can
#    subscribe to them.
# 2. RSS (Really Simple Syndication): An XML-based format used to deliver 
#    frequently updated web content. We parse the XML to extract active jobs.
# ==============================================================================

ENV_FILE = ".env"
SEEN_JOBS_FILE = "data/seen_jobs.json"

def load_env():
    """Loads environment variables."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def get_seen_jobs():
    """Loads previously seen job URLs to avoid duplicate alerts."""
    if os.path.exists(SEEN_JOBS_FILE):
        try:
            with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_jobs(seen_set):
    """Saves seen job list to prevent spamming Discord."""
    os.makedirs("data", exist_ok=True)
    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_set), f)

def send_discord_job_alert(title, desc_snippet, link):
    """
    Sends a structured, clickable job alert to Aum's Discord channel.
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"[!] Skip Discord Alert: {title}")
        return
        
    payload = {
        "embeds": [{
            "title": f"💼 New Upwork Job: {title}",
            "description": f"{desc_snippet}\n\n[**Click here to apply on Upwork**]({link})",
            "color": 65280, # Green color for business alerts
            "footer": {"text": "Upwork Job RSS Tracker"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 204:
            print(f"[+] Discord job alert sent: {title}")
        else:
            print(f"[!] Discord warning: status {response.status_code}")
    except Exception as e:
        print(f"[!] Error notifying Discord: {e}")

def parse_upwork_rss(rss_url):
    """
    Fetches the Upwork RSS XML feed, parses the jobs, and alerts
    on new, unseen job postings.
    """
    print(f"[*] Fetching Upwork jobs from RSS Feed...")
    headers = {
        # A standard RSS reader User-Agent to ensure Upwork doesn't block the connection
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(rss_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[!] RSS Feed fetch failed with status: {response.status_code}")
            return
            
        # Parse XML using BeautifulSoup (html.parser is perfectly fine for basic tags)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all("item")
        
        seen_jobs = get_seen_jobs()
        new_jobs_found = 0
        
        print(f"[+] Found {len(items)} active jobs in feed.")
        
        for item in items:
            title = item.find("title").text.strip() if item.find("title") else "Untitled Job"
            link = item.find("link").text.strip() if item.find("link") else ""
            desc = item.find("description").text.strip() if item.find("description") else ""
            
            # Clean up raw HTML tags inside descriptions
            clean_desc = BeautifulSoup(desc, "html.parser").get_text()
            desc_snippet = clean_desc[:300] + "..." if len(clean_desc) > 300 else clean_desc
            
            # Skip if we already alerted this job
            if link and link not in seen_jobs:
                send_discord_job_alert(title, desc_snippet, link)
                seen_jobs.add(link)
                new_jobs_found += 1
                time.sleep(1) # Delay between webhook calls to avoid rate limits
                
        save_seen_jobs(seen_jobs)
        print(f"[✓] RSS Scan complete. Dispatched {new_jobs_found} new job alerts.")
        
    except Exception as e:
        print(f"[!] Error parsing Upwork RSS feed: {e}")

def simulate_mock_jobs_feed():
    """
    Simulates a couple of active Upwork jobs in a mock format so the user
    can verify the scraper immediately without setting up their RSS URL first.
    """
    print("[*] Mock Mode: Generating mock Upwork job listings...")
    
    mock_jobs = [
        {
            "title": "Shopify Developer Needed to Sync Products with Supplier CSV",
            "desc": "We are looking for a developer to write a Python script that will read our supplier's inventory CSV file and automatically update our Shopify store stock levels every hour. Budget: $400 one-time.",
            "link": "https://www.upwork.com/jobs/mock-shopify-sync-12345"
        },
        {
            "title": "WooCommerce Price Update Automation Script",
            "desc": "Our manufacturers send us daily price sheets. We need a freelancer to write an integration that reads these sheets and updates prices via WooCommerce API. Budget: $250.",
            "link": "https://www.upwork.com/jobs/mock-wc-sync-67890"
        }
    ]
    
    seen_jobs = get_seen_jobs()
    new_count = 0
    for job in mock_jobs:
        if job["link"] not in seen_jobs:
            send_discord_job_alert(job["title"], job["desc"], job["link"])
            seen_jobs.add(job["link"])
            new_count += 1
            
    save_seen_jobs(seen_jobs)
    print(f"[SUCCESS] Mock scan complete. Dispatched {new_count} mock alerts to Discord.")

def main():
    print("=========================================================")
    print("         ANTIGRAVITY UPWORK JOB ALERTER BOT              ")
    print("=========================================================\n")
    
    load_env()
    
    # Check if the user has added their custom Upwork search feed URL
    upwork_rss_url = os.getenv("UPWORK_RSS_URL")
    
    if not upwork_rss_url or upwork_rss_url == "YOUR_UPWORK_RSS_URL_HERE":
        print("[!] No UPWORK_RSS_URL found in .env.")
        simulate_mock_jobs_feed()
    else:
        parse_upwork_rss(upwork_rss_url)

if __name__ == "__main__":
    main()
