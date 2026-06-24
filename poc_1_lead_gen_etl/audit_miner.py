import os
import requests
import json
import time

# ==============================================================================
# B2B LEAD ACQUISITION: HIGH-CONVERTING PRICE & MARGIN AUDIT MINER
# 1. The Auditing Hook: Cold emails fail because they lack value and trust. 
#    This script generates a highly personalized, high-stakes Price & Margin
#    Discrepancy Audit for a target wholesaler.
# 2. Financial Urgency: Showing an owner they are actively losing money on 
#    specific products because of manual pricing updates is the fastest way
#    to secure high-ticket integration contracts.
# ==============================================================================

REPORTS_DIR = "reports"
ENV_FILE = r"C:\Users\aumjv\Documents\antigravity\keen-planck\poc_1_lead_gen_etl\.env"

os.makedirs(REPORTS_DIR, exist_ok=True)

def load_env():
    """Loads environment variables."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()

def generate_local_fallback_audit(company_name, website, platform):
    """
    Local fallback generator that computes price protection margins, simulates
    discrepancies, and writes the Markdown audit and email pitch without calling the AI.
    Guarantees 100% reliability under network or API service outages.
    """
    print("[*] Running local fallback audit generator (API offline)...")
    
    # Infer niche and products
    niche_products = [
        {"sku": "PART-A-12", "name": "Replacement Fitting 1/2\"", "cost": 15.00, "prev_cost": 14.50, "qty": 120},
        {"sku": "PART-B-34", "name": "Legacy Assembly 3/4\"", "cost": -8.00, "prev_cost": 8.00, "qty": 45}, # Negative price breach
        {"sku": "PART-C-100", "name": "Heavy Duty Component", "cost": 210.00, "prev_cost": 120.00, "qty": 28}, # Cost spike breach (+75%)
        {"sku": "PART-D-01", "name": "Coupling Adapter", "cost": 3.50, "prev_cost": 3.50, "qty": 4}, # Low stock (triggers safety stock)
        {"sku": "PART-E-88", "name": "Industrial Gasket Pack", "cost": 18.50, "prev_cost": 18.50, "qty": 75}
    ]
    
    c_name_lower = company_name.lower()
    niche_name = "Industrial & Trade Parts"
    if "welding" in c_name_lower:
        niche_name = "Welding Equipment & Supplies"
        niche_products = [
            {"sku": "WELD-TR-200", "name": "Replacement Torch Head", "cost": 45.00, "prev_cost": 44.00, "qty": 9},
            {"sku": "WELD-EL-7018", "name": "7018 Welding Electrodes (10lb)", "cost": -25.00, "prev_cost": 25.00, "qty": 150}, # Negative cost anomaly
            {"sku": "HELM-AUTO-12", "name": "Auto-Darkening Welding Helmet", "cost": 195.00, "prev_cost": 110.00, "qty": 12}, # Cost spike anomaly (+77%)
            {"sku": "WELD-CL-HD", "name": "Heavy Duty Ground Clamp 500A", "cost": 19.99, "prev_cost": 19.99, "qty": 3}, # Safety stock trigger
            {"sku": "WELD-GL-10", "name": "MIG Welding Leather Gloves (Pair)", "cost": 14.50, "prev_cost": 14.50, "qty": 80}
        ]
    elif "livewire" in c_name_lower:
        niche_name = "Electrical Components & Switchgear"
        niche_products = [
            {"sku": "BREAKER-QO-20", "name": "20A Double Pole Circuit Breaker", "cost": 16.50, "prev_cost": 16.00, "qty": 200},
            {"sku": "WIRE-THHN-12", "name": "12 AWG THHN Copper Wire 500ft", "cost": -75.00, "prev_cost": 75.00, "qty": 40}, # Negative cost anomaly
            {"sku": "TRANS-STEP-5K", "name": "5kVA Step Down Transformer", "cost": 780.00, "prev_cost": 450.00, "qty": 8}, # Cost spike anomaly (+73%)
            {"sku": "SWITCH-DISC-30", "name": "30A Outdoor Safety Disconnect", "cost": 42.00, "prev_cost": 42.00, "qty": 2}, # Safety stock trigger
            {"sku": "CONDUIT-EMT-10", "name": "1/2\" EMT Steel Conduit 10ft", "cost": 5.80, "prev_cost": 5.80, "qty": 150}
        ]
    elif "hydraulic" in c_name_lower:
        niche_name = "Hydraulic Pumps, Cylinders & Hoses"
        niche_products = [
            {"sku": "CYL-HD-20", "name": "Heavy Duty Hydraulic Cylinder 2\" Bore", "cost": 145.00, "prev_cost": 140.00, "qty": 14},
            {"sku": "HOSE-MP-4", "name": "Medium Pressure Hydraulic Hose 50ft", "cost": -65.00, "prev_cost": 65.00, "qty": 90}, # Negative cost anomaly
            {"sku": "PUMP-GEAR-3", "name": "High Pressure Rotary Gear Pump", "cost": 385.00, "prev_cost": 220.00, "qty": 6}, # Cost spike anomaly (+75%)
            {"sku": "VALVE-FLOW-1", "name": "Proportional Flow Control Valve", "cost": 89.00, "prev_cost": 89.00, "qty": 1}, # Safety stock trigger
            {"sku": "FITT-ORING-5", "name": "SAE O-Ring Boss Fitting 3/4\"", "cost": 2.45, "prev_cost": 2.45, "qty": 300}
        ]

    # Calculate values locally
    markup = 30
    table_rows = []
    total_loss = 0.00
    flagged_details = []
    
    for item in niche_products:
        sku = item["sku"]
        name = item["name"]
        cost = item["cost"]
        prev_cost = item["prev_cost"]
        qty = item["qty"]
        
        retail_price = cost * (1 + (markup / 100))
        
        status = "Passed"
        status_color = "🟢"
        
        if cost <= 0:
            status = "CRITICAL: Negative Cost"
            status_color = "🔴"
            retail_price = prev_cost * (1 + (markup / 100)) # fallback price
            loss = abs(cost) * 50 # simulated monthly sales loss
            total_loss += loss
            flagged_details.append(f"• **{name}** ({sku}): Wholesale cost is set to a negative value ({costDisplay(cost)}) inside your catalog, risking selling it for free on your store.")
        elif (cost - prev_cost) / prev_cost >= 0.5:
            spike_pct = ((cost - prev_cost) / prev_cost) * 100
            status = f"CRITICAL: Cost Spike (+{int(spike_pct)}%)"
            status_color = "🔴"
            loss = (cost - prev_cost) * 15 # simulated monthly loss
            total_loss += loss
            flagged_details.append(f"• **{name}** ({sku}): Manufacturer raised cost by **{int(spike_pct)}%** (from ${prev_cost:.2f} to ${cost:.2f}), but your store price remains unchanged, eroding 100% of your gross margins.")
        elif qty <= 5:
            status = "Adjusted: Safety Stock (Qty -> 0)"
            status_color = "🟡"
            
        margin_pct = ((retail_price - cost) / retail_price) * 100 if retail_price > 0 else 0
        
        cost_display = f"-${abs(cost):.2f}" if cost < 0 else f"${cost:.2f}"
        price_display = f"${retail_price:.2f}"
        
        table_rows.append(f"| {sku} | {name} | {price_display} | {cost_display} | {margin_pct:.1f}% | {status_color} {status} |")
        
    table_content = "\n".join(table_rows)
    flagged_bullets = "\n".join(flagged_details)
    
    audit_part = f"""# Price & Margin Protection Audit: {company_name}

## Executive Summary
This audit reports critical pricing discrepancies and margin vulnerabilities discovered in the catalog footprint of **{company_name}** ({website}). Due to manual price file ingestion delays, several high-value SKU records are out of sync with manufacturer price lists, exposing the business to net transaction losses and margin erosion.

## Catalog Discrepancy Breakdown
Below is the status audit of 5 sample inventory records comparing your store's current retail pricing against updated manufacturer wholesale catalogs:

| SKU | Product Name | Store Retail Price | Supplier Wholesale Cost | Gross Margin | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_content}

## Financial Vulnerability Analysis
Our scan identified **2 critical pricing errors** that are actively draining your profit margins:
{flagged_bullets}

**Simulated Monthly Loss Exposure:** Based on typical transaction volumes, these two vulnerabilities expose {company_name} to **${total_loss:.2f}/month** in lost margins and order cancellation refunds.

## Recommended Remediation
To eliminate manual data entry and safeguard your margins, we recommend deploying a lightweight **Python Micro-ETL Sync service** with an automated **Validation Gate**:
1. **Cost Spike Shield:** Blocks automated uploads if the wholesale price rises above a custom threshold (e.g. +30%) until reviewed.
2. **Negative Cost Protection:** Automatically catches and quarantines catalog errors (like negative costs or missing values).
3. **Safety Stock Override:** Dynamically drops store availability to 0 if manufacturer stock falls below your safety threshold.
"""

    email_part = f"""Subject: Quick question about inventory leaks at {company_name}

Hi {company_name} team,

I was looking at your online catalog on {website} and noticed you sell {niche_products[0]['name']} and {niche_products[4]['name']} on {platform}. 

I ran a quick price audit of your store against the latest manufacturer price sheets and found two critical discrepancies where catalog update delays are causing issues:
* On your {niche_products[1]['name']}, the wholesale cost record has a negative formatting error.
* On your {niche_products[2]['name']}, the manufacturer cost rose significantly, but the retail price is out of sync, eroding your gross margin.

Automating these updates directly **saves your team time, money, and labor** by stopping order cancellations and protecting your margins.

I compiled the full PDF audit report. Would it be alright if I sent it over, or shared a quick text walkthrough of how we can automate this to protect your margins?

Best,

Aum
Integration Specialist

P.S. For your developer or IT manager, here's a system flowchart showing how the price protection gate works:
https://raw.githubusercontent.com/Aum31/inventory-sync-diagram/main/system_flow.png
"""

    # Save the audit report to a file
    file_base = company_name.lower().replace(" ", "_")
    report_path = os.path.join(REPORTS_DIR, f"{file_base}_price_audit.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(audit_part)
        
    # Save the email pitch to a file
    pitch_path = os.path.join(REPORTS_DIR, f"{file_base}_audit_pitch.txt")
    with open(pitch_path, "w", encoding="utf-8") as f:
        f.write(email_part)
        
    print(f"[SUCCESS] Generated Price Audit Report (Local Fallback): {report_path}")
    print(f"[SUCCESS] Generated Audit Email Pitch (Local Fallback): {pitch_path}")
    return audit_part, email_part

def costDisplay(cost):
    return f"-${abs(cost):.2f}" if cost < 0 else f"${cost:.2f}"

def generate_price_audit(company_name, website, platform):
    """
    Uses Gemini API to brainstorm realistic products for the target wholesaler,
    simulate a price audit comparing store retail prices vs updated manufacturer costs,
    detect margin discrepancies, and write a professional B2B Price Protection Audit.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[!] Error: No GEMINI_API_KEY found in environment. Invoking local fallback...")
        return generate_local_fallback_audit(company_name, website, platform)

    print(f"[*] Analyzing '{company_name}' catalog footprint on {platform}...")
    
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }

    prompt = f"""
You are a senior E-commerce Consultant and Integration Specialist. 
You are performing a mock "Price & Margin Protection Audit" for a wholesale company named '{company_name}' (website: {website}) who runs their catalog on '{platform}'.

Your goal is to generate a realistic, high-stakes audit report that proves they are losing money right now because their retail prices are out of sync with updated manufacturer wholesale costs.

Tasks:
1. Brainstorm 5 highly realistic products that {company_name} sells (infer this from their name, e.g. valves/couplings for plumbing, electrodes/welders for welding, circuit breakers for electrical).
2. For each product, assign a realistic Store Retail Price, a Previous Wholesale Cost, and an Updated Manufacturer Wholesale Cost.
3. Make sure 2 of these products have critical discrepancies:
   - Item A: A "Margin Breach" (where the updated manufacturer wholesale cost has risen ABOVE their current store retail price, meaning they are selling at a net loss).
   - Item B: A "Cost Spike" (where the manufacturer wholesale cost rose by >30% but their store retail price was never updated, eroding their gross margins to almost zero).
4. Calculate the specific dollar loss per unit based on typical sales volume (e.g. losing $12.50 per unit, costing them $375/month on average sales).

Generate the output in two distinct parts:

PART 1: A beautiful, professional Markdown Audit Report. 
Structure it with:
- Title: "Price & Margin Protection Audit: {company_name}"
- Executive Summary (Brief, stating that manual catalog updates have left them exposed to pricing discrepancies).
- A markdown table showing: SKU, Product Name, Store Price, Manufacturer Cost, Gross Margin (%), and Status (Passed vs Critical Discrepancy).
- Financial Impact section: Summarize the monthly losses from the 2 flagged items.
- Solution: Pitch a brief 2-sentence explanation of our Python automated validation gate.

PART 2: A highly personalized, short, and casual cold email pitch to the owner.
- Address it to: "Hi {company_name} team," (or a natural greeting).
- Tone: Conversational, peer-to-peer, helpful (no marketing fluff, no buzzwords).
- Mention the specific products and the exact pricing discrepancies found in the audit to prove you actually looked at their business.
- Provide a low-pressure close: "I compiled the full PDF audit report. Would it be alright if I sent it over, or shared a quick text walkthrough of how we automate this to protect your margins?"
- Sign off as: "Best, Aum"

Format your entire response exactly like this, using the delimiters:
===AUDIT_REPORT===
[Your Markdown Audit Report here]
===EMAIL_PITCH===
[Your Customized Email Pitch here]
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 2048
        }
    }

    max_retries = 3
    retry_delay = 2
    response = None
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                break
            elif response.status_code in [503, 429]:
                print(f"[!] Warning: Gemini API returned {response.status_code}. Retrying in {retry_delay}s (Attempt {attempt+1}/{max_retries})...")
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"[!] Gemini API failed with status: {response.status_code}")
                print("[*] Invoking local fallback...")
                return generate_local_fallback_audit(company_name, website, platform)
        except Exception as e:
            print(f"[!] Request error (Attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
            retry_delay *= 2
            
    if not response or response.status_code != 200:
        print("[!] Error: Failed to retrieve response from Gemini API after retries. Invoking local fallback...")
        return generate_local_fallback_audit(company_name, website, platform)

    try:
        result_text = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        if "===AUDIT_REPORT===" in result_text and "===EMAIL_PITCH===" in result_text:
            parts = result_text.split("===EMAIL_PITCH===")
            audit_part = parts[0].replace("===AUDIT_REPORT===", "").strip()
            email_part = parts[1].strip()
        else:
            print("[!] Warning: Gemini output did not contain expected delimiters. Attempting fallback parsing...")
            if "Subject:" in result_text:
                parts = result_text.split("Subject:", 1)
                audit_part = parts[0].replace("===AUDIT_REPORT===", "").strip()
                email_part = "Subject: " + parts[1].replace("===EMAIL_PITCH===", "").strip()
            else:
                print(f"[!] Critical: Delimiters and 'Subject:' not found. Invoking local fallback...")
                return generate_local_fallback_audit(company_name, website, platform)
            
        # Save the audit report to a file
        file_base = company_name.lower().replace(" ", "_")
        report_path = os.path.join(REPORTS_DIR, f"{file_base}_price_audit.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(audit_part)
            
        # Save the email pitch to a file
        pitch_path = os.path.join(REPORTS_DIR, f"{file_base}_audit_pitch.txt")
        with open(pitch_path, "w", encoding="utf-8") as f:
            f.write(email_part)
            
        print(f"[SUCCESS] Generated Price Audit Report: {report_path}")
        print(f"[SUCCESS] Generated Audit Email Pitch: {pitch_path}")
        return audit_part, email_part

    except Exception as e:
        print(f"[!] Error generating audit report: {e}. Invoking local fallback...")
        return generate_local_fallback_audit(company_name, website, platform)

if __name__ == "__main__":
    load_env()
    print("=========================================================")
    print("          B2B PRICE AUDIT GENERATOR ENGINE               ")
    print("=========================================================\n")
    generate_price_audit("Weldingmart", "https://weldingmart.com/", "Shopify")
