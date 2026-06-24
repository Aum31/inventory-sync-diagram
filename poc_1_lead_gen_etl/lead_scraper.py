import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# ==============================================================================
# ANTIGRAVITY LESSON 1: What is a Web Scraper?
# A scraper does three things:
# 1. Sends an HTTP request to a website (acting like a web browser requesting a page).
# 2. Receives the raw HTML code of the page.
# 3. Parses the HTML to extract specific data (e.g., website links, company names, emails).
# ==============================================================================

# List of target sites to scan for our proof of concept.
# In a full-scale scraper, we would search Google or Yelp to generate this list automatically.
TARGET_SITES = [
    {"name": "Industrial Automation Co.", "url": "https://industrialautomationco.com"},
    {"name": "Triumph Industrial Supply", "url": "https://triumphindustrialsupply.com"},
    {"name": "21Supply Wholesale", "url": "https://21supply.com"},
    {"name": "H2O Bath and Plumbing Supplies", "url": "https://h2obathandplumbingsupplies.com"}
]

def check_ecommerce_platform(url):
    """
    Scrapes a target website and checks if it runs on Shopify or WooCommerce
    by searching for specific signatures in the HTML source code.
    """
    headers = {
        # We send a "User-Agent" header so the website thinks we are a normal Chrome browser,
        # preventing it from blocking our request as a bot.
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"[*] Scanning website: {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        
        # If the request fails (e.g. 404 Not Found, 403 Forbidden), return Unknown
        if response.status_code != 200:
            return "Unknown (Status Code: {})".format(response.status_code)
            
        html_content = response.text
        
        # Shopify Signatures in HTML:
        # - Shopify stores store assets on cdn.shopify.com
        # - They define a global javascript variable window.Shopify
        if "cdn.shopify.com" in html_content or "window.Shopify" in html_content:
            return "Shopify"
            
        # WooCommerce Signatures in HTML:
        # - WooCommerce is a WordPress plugin, so assets are under wp-content/plugins/woocommerce
        # - The HTML often contains classes like class="woocommerce"
        if "wp-content/plugins/woocommerce" in html_content or "woocommerce" in html_content:
            return "WooCommerce"
            
        return "Custom/Other"
        
    except requests.exceptions.RequestException as e:
        # If the website is offline or blocks the request, handle the error gracefully
        return f"Offline/Blocked ({type(e).__name__})"

def main():
    print("=========================================================")
    print("       ANTIGRAVITY MOCK LEAD GENERATION AGENT            ")
    print("=========================================================\n")
    
    qualified_leads = []
    
    for site in TARGET_SITES:
        platform = check_ecommerce_platform(site["url"])
        print(f"[+] Result: {site['name']} is running on: {platform}\n")
        
        # We only want to target stores running Shopify or WooCommerce
        # because those are the stores we know how to connect our inventory sync scripts to!
        if platform in ["Shopify", "WooCommerce"]:
            qualified_leads.append({
                "Company Name": site["name"],
                "Website": site["url"],
                "Platform": platform,
                "Status": "Qualified Lead (Ready for Outreach)"
            })
        
        # Polite scraping practice: wait 1 second between requests so we don't overload the servers
        time.sleep(1)
        
    # Save our leads list to a CSV file
    csv_file_path = "data/qualified_leads.csv"
    import os
    os.makedirs("data", exist_ok=True)
    
    with open(csv_file_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Company Name", "Website", "Platform", "Status"])
        writer.writeheader()
        writer.writerows(qualified_leads)
        
    print(f"[SUCCESS] Lead generation run complete! Saved {len(qualified_leads)} leads to: {csv_file_path}")

if __name__ == "__main__":
    main()
