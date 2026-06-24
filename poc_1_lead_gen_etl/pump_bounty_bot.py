import os
import sys
import json
import time
import requests
from bs4 import BeautifulSoup

# ==============================================================================
# AUM'S PUMP.FUN AI-FILTERED BOUNTY BOT
# Uses Google Gemini API to filter tasks dynamically based on true capabilities.
# ==============================================================================

ENV_FILE = ".env"
SEEN_BOUNTIES_FILE = "data/seen_bounties.json"

def load_env():
    """Loads environment configurations."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def get_seen_bounties():
    """Loads history of dispatched alerts."""
    if os.path.exists(SEEN_BOUNTIES_FILE):
        try:
            with open(SEEN_BOUNTIES_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_bounties(seen_set):
    """Persists seen bounty IDs to prevent duplicates."""
    os.makedirs("data", exist_ok=True)
    with open(SEEN_BOUNTIES_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_set), f)

def query_gemini_filter(title, description, api_key):
    """
    Asks Gemini to evaluate if the task is doable entirely on a computer 
    (coding, scripts, writing, excel, design) and excludes physical stunts or video dares.
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    prompt = f"""
Analyze the following bounty task description from a crypto platform. 
Determine if this task is a DIGITAL task that can be performed entirely on a computer (such as writing code, building scripts, database work, Excel spreadsheets, copy/paste data tasks, writing technical articles, or creating graphic logos).

Exclude tasks that require:
- Physical stunts or dares (e.g. tattoos, eating/drinking, going outside).
- Taking photos or recording videos of a person (e.g. face verification, video diaries, singing, dancing).
- Social media engagement spam (e.g. commenting on X posts, following/liking, raiding token groups).

Bounty Title: {title}
Bounty Description: {description}

Reply with exactly one word: 'YES' if it is a doable digital/coding/writing task, or 'NO' if it is a physical stunt, video dare, or social media spam task.
"""
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 5
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip().upper()
            return "YES" in result_text
        else:
            print(f"[!] Gemini API warning: status {response.status_code} ({response.text})")
            return False
    except Exception as e:
        print(f"[!] Error querying Gemini Filter API: {e}")
        return False

def send_discord_bounty_alert(title, description, reward_amount, task_id):
    """Dispatches a formatted alert card to Discord."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url or webhook_url == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print(f"[!] Skip Alert: {title} (Webhook missing)")
        return
        
    link = "https://pump.fun/go"
    payload = {
        "embeds": [{
            "title": f"🎯 New Matching Bounty: {title}",
            "description": f"{description}\n\n[**View on Pump.fun GO**]({link})",
            "color": 9442302, # Deep violet theme
            "fields": [
                {
                    "name": "💰 Est. Reward",
                    "value": f"{reward_amount} SOL",
                    "inline": True
                },
                {
                    "name": "🔑 Task ID",
                    "value": f"`{task_id}`",
                    "inline": True
                }
            ],
            "footer": {"text": "Pump.fun GO AI-Filtered Tracker"}
        }]
    }
    
    try:
        requests.post(webhook_url, json=payload, timeout=10)
        print(f"[+] Alert dispatched: {title}")
    except Exception as e:
        print(f"[!] Error notifying Discord: {e}")

def parse_bounties_from_html(html_text):
    """Extracts raw bounties list from client state scripts in the HTML page."""
    soup = BeautifulSoup(html_text, "html.parser")
    bounties_list = []
    
    scripts = soup.find_all("script")
    for script in scripts:
        content = script.string
        if not content:
            continue
            
        if '\\"' in content:
            content_cleaned = content.replace('\\"', '"')
        else:
            content_cleaned = content
            
        if "taskId" in content_cleaned and "bodyMarkdown" in content_cleaned:
            idx = 0
            while True:
                idx = content_cleaned.find('"taskId"', idx)
                if idx == -1:
                    break
                    
                start = content_cleaned.rfind("{", 0, idx)
                if start == -1:
                    idx += 1
                    continue
                    
                depth = 0
                end = start
                found_match = False
                while end < len(content_cleaned):
                    if content_cleaned[end] == "{":
                        depth += 1
                    elif content_cleaned[end] == "}":
                        depth -= 1
                        if depth == 0:
                            found_match = True
                            break
                    end += 1
                    
                if found_match:
                    task_json_str = content_cleaned[start:end+1]
                    try:
                        task_data = json.loads(task_json_str)
                        if "taskId" in task_data:
                            if task_data["taskId"] not in [b["taskId"] for b in bounties_list]:
                                bounties_list.append(task_data)
                    except Exception:
                        pass
                idx += 1
                
    return bounties_list

def run_scan():
    """Fetches, parses, filters and alerts on matching bounties."""
    load_env()
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("[!] Aborted: No GEMINI_API_KEY set in .env. Cannot run AI filter.")
        sys.exit(1)
        
    print("[*] Contacting pump.fun/go...")
    url = "https://pump.fun/go"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"[!] Fetch failed: status {response.status_code}")
            return
            
        bounties = parse_bounties_from_html(response.text)
        print(f"[+] Loaded {len(bounties)} raw bounties.")
        
        seen_bounties = get_seen_bounties()
        new_alerts = 0
        
        for b in bounties:
            task_id = b.get("taskId")
            title = b.get("title", "Untitled Bounty")
            desc = b.get("bodyMarkdown", "")
            
            amount_atomic = 0
            legs = b.get("rewardLegs", [])
            if legs:
                amount_atomic = int(legs[0].get("amountAtomic", 0))
            reward_sol = amount_atomic / 10**9 if amount_atomic > 0 else 0.0
            
            if task_id in seen_bounties:
                continue
                
            # Filter via Gemini AI
            print(f"[*] AI analyzing: {title}...")
            if query_gemini_filter(title, desc, gemini_key):
                send_discord_bounty_alert(title, desc, reward_sol, task_id)
                new_alerts += 1
                time.sleep(1) # Delay between alerts
                
            seen_bounties.add(task_id)
            
        save_seen_bounties(seen_bounties)
        print(f"[SUCCESS] Scanned. Found {new_alerts} matching digital tasks.")
        
    except Exception as e:
        print(f"[!] Scan error: {e}")

if __name__ == "__main__":
    run_scan()
