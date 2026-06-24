import requests
import sys
import json
import os

# ==============================================================================
# ANTIGRAVITY LESSON 4: Databases and Bioinformatics / Cheminformatics
# 1. PubChem: A massive, free database of chemical molecules maintained by the
#    US National Institutes of Health (NIH).
# 2. PUG REST API: PubChem's gateway that lets developers query molecules by 
#    name or structure to get data (weight, formula, patents) automatically.
# ==============================================================================

# API Base URL for PubChem
PUBCHEM_API_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

DATA_DIR = "reports"
os.makedirs(DATA_DIR, exist_ok=True)

def get_compound_properties(name):
    """
    Queries PubChem to retrieve chemical properties (Formula, IUPAC Name, Weight, SMILES structure).
    """
    url = f"{PUBCHEM_API_URL}/compound/name/{name}/property/IUPACName,MolecularFormula,MolecularWeight,CanonicalSMILES/JSON"
    print(f"[*] Fetching properties for '{name}' from PubChem database...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract the properties dictionary from the JSON response
            properties = data.get("PropertyTable", {}).get("Properties", [])
            if properties:
                return properties[0] # Return the first matching compound's details
        print(f"[!] Error: Could not find compound '{name}' in PubChem.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return None

def get_associated_patents(cid):
    """
    Queries PubChem to find patent IDs linked to the compound ID (CID).
    """
    url = f"{PUBCHEM_API_URL}/compound/cid/{cid}/xrefs/PatentID/JSON"
    print(f"[*] Checking patent database for Compound ID (CID): {cid}...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract list of patent numbers
            patent_ids = data.get("InformationList", {}).get("Information", [])[0].get("PatentID", [])
            return patent_ids
        # If no patents are found or API doesn't return 200
        return []
    except requests.exceptions.RequestException as e:
        print(f"[!] Warning: Failed to retrieve patent records: {e}")
        return []

def generate_clearance_report(compound_name, properties, patents):
    """
    Combines chemical properties and patent counts into a structured report
    that an IP (Intellectual Property) lawyer or R&D chemist can use.
    """
    cid = properties.get("CID")
    formula = properties.get("MolecularFormula")
    weight = properties.get("MolecularWeight")
    iupac = properties.get("IUPACName")
    smiles = properties.get("CanonicalSMILES") or properties.get("ConnectivitySMILES") or properties.get("IsomericSMILES")
    
    report_content = f"""# IP PATENT CLEARANCE REPORT: {compound_name.upper()}
--------------------------------------------------
Report Target: {compound_name}
PubChem Compound ID (CID): {cid}

## Chemical Structure Details
*   **IUPAC Name:** {iupac}
*   **Molecular Formula:** {formula}
*   **Molecular Weight:** {weight} g/mol
*   **SMILES Representation:** {smiles}

## Intellectual Property (IP) Analysis
*   **Total Associated Patents Found:** {len(patents)}
*   **Clearance Status:** {"POTENTIAL CONFLICT (Patented)" if patents else "CLEARED (No Patents Found)"}

## Sample Active Patents (Top 10):
"""
    if patents:
        for p in patents[:10]:
            report_content += f"  - Patent ID: {p}\n"
    else:
        report_content += "  - No registered patents found in PubChem database.\n"
        
    report_content += "\n--------------------------------------------------\n"
    
    # Save the report to a text file
    filename = f"{DATA_DIR}/{compound_name.lower()}_clearance_report.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(report_content)
    print(f"[SUCCESS] Patent clearance report saved to: {filename}")

def main():
    print("=========================================================")
    print("      ANTIGRAVITY IP PATENT & CHEMICAL CLEARANCE        ")
    print("=========================================================\n")
    
    # Allow passing compound name as command argument, defaults to "aspirin"
    compound_name = sys.argv[1] if len(sys.argv) > 1 else "aspirin"
    
    # 1. Fetch chemical formula and ID
    properties = get_compound_properties(compound_name)
    if not properties:
        print("[!] Pre-clearance aborted: Compound properties unavailable.")
        return
        
    # 2. Fetch associated patent numbers using the Compound ID (CID)
    cid = properties.get("CID")
    patents = get_associated_patents(cid)
    
    # 3. Compile report
    generate_clearance_report(compound_name, properties, patents)

if __name__ == "__main__":
    main()
