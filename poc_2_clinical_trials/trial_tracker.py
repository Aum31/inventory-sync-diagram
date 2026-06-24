import os
import json
import requests
import sys

# ==============================================================================
# ANTIGRAVITY LESSON 3: What is a REST API & JSON?
# 1. REST API: A way for systems to talk over the web. We send a request (URL) 
#    and get back data (usually in JSON format) instead of an HTML webpage.
# 2. JSON: JavaScript Object Notation. A standard data format representing lists 
#    and key-value pairs, which is easy for computers to read and write.
# ==============================================================================

# ClinicalTrials.gov API v2 Endpoint
API_BASE_URL = "https://clinicaltrials.gov/api/v2/studies/"

DATA_DIR = "data/studies"
os.makedirs(DATA_DIR, exist_ok=True)

# We will use this study ID for testing.
# NCT06000000 is a real NCT ID or we can use another stable active ID (e.g., NCT04500000)
DEFAULT_NCT_ID = "NCT06459180"

def get_study_filepaths(nct_id):
    """Returns the absolute file paths for current and historical JSON files."""
    current_path = os.path.join(DATA_DIR, f"{nct_id}.json")
    old_path = os.path.join(DATA_DIR, f"{nct_id}_previous.json")
    return current_path, old_path

def fetch_trial_data(nct_id):
    """
    Fetches clinical trial data from the public ClinicalTrials.gov API.
    """
    url = f"{API_BASE_URL}{nct_id}"
    print(f"[*] Fetching trial {nct_id} from ClinicalTrials.gov API...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"[!] Error: Trial ID {nct_id} not found on ClinicalTrials.gov.")
            return None
        else:
            print(f"[!] Error: API responded with status code {response.status_code}.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return None

def extract_key_fields(study_json):
    """
    Extracts relevant clinical metrics from the massive study JSON
    so they are easy to compare and analyze.
    """
    if not study_json:
        return {}
        
    protocol = study_json.get("protocolSection", {})
    
    # Extract status
    status = protocol.get("statusModule", {}).get("overallStatus", "UNKNOWN")
    
    # Extract sponsor
    sponsor = protocol.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "UNKNOWN")
    
    # Extract eligibility age limits
    eligibility = protocol.get("eligibilityModule", {})
    min_age = eligibility.get("minimumAge", "No Limit")
    max_age = eligibility.get("maximumAge", "No Limit")
    
    # Extract primary outcomes list
    outcomes = protocol.get("outcomesModule", {}).get("primaryOutcomes", [])
    primary_outcomes_summarized = [out.get("measure", "") for out in outcomes if out.get("measure")]
    
    # Extract conditions / diseases being studied
    conditions = protocol.get("conditionsModule", {}).get("conditions", [])
    
    return {
        "status": status,
        "sponsor": sponsor,
        "min_age": min_age,
        "max_age": max_age,
        "primary_outcomes": primary_outcomes_summarized,
        "conditions": conditions
    }

def find_differences(old_data, new_data):
    """
    Compares two versions of a study and lists the differences.
    """
    diffs = {}
    
    # 1. Check Status
    if old_data.get("status") != new_data.get("status"):
        diffs["Status"] = {
            "old": old_data.get("status"),
            "new": new_data.get("status")
        }
        
    # 2. Check Age range changes
    if old_data.get("min_age") != new_data.get("min_age") or old_data.get("max_age") != new_data.get("max_age"):
        diffs["Age Criteria"] = {
            "old": f"Min: {old_data.get('min_age')}, Max: {old_data.get('max_age')}",
            "new": f"Min: {new_data.get('min_age')}, Max: {new_data.get('max_age')}"
        }
        
    # 3. Check Primary Outcomes
    old_outcomes = set(old_data.get("primary_outcomes", []))
    new_outcomes = set(new_data.get("primary_outcomes", []))
    if old_outcomes != new_outcomes:
        diffs["Primary Outcomes"] = {
            "removed": list(old_outcomes - new_outcomes),
            "added": list(new_outcomes - old_outcomes)
        }
        
    # 4. Check Conditions list
    old_conds = set(old_data.get("conditions", []))
    new_conds = set(new_data.get("conditions", []))
    if old_conds != new_conds:
        diffs["Conditions"] = {
            "removed": list(old_conds - new_conds),
            "added": list(new_conds - old_conds)
        }
        
    return diffs

def simulate_historical_diff(nct_id):
    """
    Helper function to generate dummy historical data so the user
    can see the diff engine running immediately without waiting.
    """
    current_path, old_path = get_study_filepaths(nct_id)
    
    # Create a dummy historical version of the trial data
    # simulating an older status and different inclusion age limit
    dummy_old_study = {
        "protocolSection": {
            "statusModule": {
                "overallStatus": "RECRUITING" # Old Status
            },
            "sponsorCollaboratorsModule": {
                "leadSponsor": {"name": "Example Pharma Corp"}
            },
            "eligibilityModule": {
                "minimumAge": "18 Years", # Old Age Limit
                "maximumAge": "65 Years"
            },
            "outcomesModule": {
                "primaryOutcomes": [
                    {"measure": "Overall Survival Rate"},
                    {"measure": "Incidence of Adverse Events"}
                ]
            },
            "conditionsModule": {
                "conditions": ["Type 2 Diabetes", "Obesity"]
            }
        }
    }
    
    with open(old_path, "w", encoding="utf-8") as f:
        json.dump(dummy_old_study, f, indent=4)
    print(f"[+] Mock Mode: Generated historical baseline file at: {old_path}")

def main():
    print("=========================================================")
    print("         ANTIGRAVITY CLINICAL TRIAL DIFF TRACKER         ")
    print("=========================================================\n")
    
    # We allow the user to type a specific NCT ID from the terminal if they want, e.g.:
    # python trial_tracker.py NCT05000000
    nct_id = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NCT_ID
    
    current_path, old_path = get_study_filepaths(nct_id)
    
    # For demonstration purposes, if the historical baseline file doesn't exist,
    # we simulate one to guarantee we have a comparison target.
    if not os.path.exists(old_path):
        simulate_historical_diff(nct_id)
        
    # 1. Fetch current study data from API
    current_json = fetch_trial_data(nct_id)
    if not current_json:
        print("[!] Execution terminated: Failed to fetch study data.")
        return
        
    # Save the current JSON to disk
    with open(current_path, "w", encoding="utf-8") as f:
        json.dump(current_json, f, indent=4)
    print(f"[+] Saved latest study JSON to: {current_path}")
    
    # 2. Load the old JSON for comparison
    try:
        with open(old_path, "r", encoding="utf-8") as f:
            old_json = json.load(f)
    except Exception as e:
        print(f"[!] Error loading previous study baseline: {e}")
        return
        
    # 3. Extract key metrics
    old_metrics = extract_key_fields(old_json)
    new_metrics = extract_key_fields(current_json)
    
    # 4. Compare and print Diffs
    diffs = find_differences(old_metrics, new_metrics)
    
    print("\n=================== DIFF REPORT ===================")
    if not diffs:
        print("[SUCCESS] No changes found. Trial protocols match exactly.")
    else:
        print(f"[!] ALERT: Protocol changes detected in {nct_id}!")
        for field, change in diffs.items():
            print(f"\n[*] Change in field: {field}")
            if "old" in change:
                print(f"    - WAS: {change['old']}")
                print(f"    - IS:  {change['new']}")
            if "added" in change or "removed" in change:
                if change.get("added"):
                    print(f"    - ADDED:   {change['added']}")
                if change.get("removed"):
                    print(f"    - REMOVED: {change['removed']}")
    print("===================================================\n")
    
    # Rotate files: the current file becomes the baseline for the next run
    try:
        # Save current as previous
        with open(old_path, "w", encoding="utf-8") as f:
            json.dump(current_json, f, indent=4)
        print(f"[+] Rotation: Latest version saved as historical baseline for next run.")
    except Exception as e:
        print(f"[!] Warning: Failed to save baseline for next iteration: {e}")

if __name__ == "__main__":
    main()
