import csv
import os
import time
import audit_miner

LEADS_FILE = "data/qualified_leads.csv"
DRAFTS_DIR = "outreach_drafts"
REPORTS_DIR = "reports"

os.makedirs(DRAFTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def main():
    print("=========================================================")
    print("      ANTIGRAVITY VALUE-FIRST AUDIT & OUTREACH GEN       ")
    print("=========================================================\n")
    
    if not os.path.exists(LEADS_FILE):
        print(f"[!] Error: Leads file '{LEADS_FILE}' not found. Please run lead_scraper.py or lead_miner.py first.")
        return
        
    generated_count = 0
    
    # Load environment variables for Gemini API key
    import auto_outreach_pipeline
    auto_outreach_pipeline.load_env()
    
    with open(LEADS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            name = row.get("Company Name")
            url = row.get("Website")
            platform = row.get("Platform")
            
            if not name or not platform:
                continue
                
            print(f"[*] Generating margin audit and pitch for: {name} ({platform})")
            
            # Generate the personalized audit and pitch using audit_miner
            try:
                audit_part, email_part = audit_miner.generate_price_audit(name, url, platform)
                
                if email_part:
                    # Save the draft to the outreach drafts folder for the pipeline to send
                    file_name = f"{name.lower().replace(' ', '_')}_outreach_pitch.txt"
                    file_path = os.path.join(DRAFTS_DIR, file_name)
                    
                    with open(file_path, "w", encoding="utf-8") as draft_file:
                        draft_file.write(email_part)
                        
                    print(f"[+] Saved outreach pitch to: {file_path}")
                    generated_count += 1
                else:
                    print(f"[!] Warning: Email pitch was empty for {name}")
            except Exception as e:
                print(f"[!] Error generating audit/pitch for {name}: {e}")
                
            # Politeness delay between API requests to respect rate limits
            time.sleep(2.0)
            
    print(f"\n[SUCCESS] Completed generation. Created {generated_count} value-first pitches in: '{DRAFTS_DIR}/'")

if __name__ == "__main__":
    main()
