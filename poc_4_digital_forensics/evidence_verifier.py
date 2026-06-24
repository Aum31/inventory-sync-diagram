import hashlib
import os
import json
import time
from datetime import datetime
import sys

# ==============================================================================
# ANTIGRAVITY LESSON 5: Cyber Forensics & Cryptographic Hashing
# 1. Cryptographic Hash (SHA-256): A mathematical algorithm that takes any file 
#    (image, document, database log) and generates a unique 64-character text 
#    "fingerprint" (hash). 
#    - It is one-way: you cannot reverse the hash back into the file.
#    - It is collision-resistant: no two different files will ever produce the same hash.
#    - If even a single letter, comma, or space is changed in a file, its hash changes entirely.
# 2. Chain of Custody: The legal process of tracking evidence from the moment it is
#    collected to prove in court that it has not been altered or tampered with.
# ==============================================================================

DATA_DIR = "evidence_store"
MANIFEST_DIR = "evidence_manifests"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MANIFEST_DIR, exist_ok=True)

def calculate_sha256(file_path):
    """
    Reads a file in binary mode and calculates its SHA-256 cryptographic hash.
    We read in chunks (4096 bytes) so that the script can handle massive files
    (like gigabyte-sized database dumps) without running out of RAM.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"[!] Error calculating hash for {file_path}: {e}")
        return None

def extract_file_metadata(file_path):
    """
    Extracts system-level metadata (file size, creation time, modification time).
    """
    try:
        stats = os.stat(file_path)
        # Convert timestamps into human-readable strings
        created_time = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
        modified_time = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        file_size = stats.st_size
        
        return {
            "file_size_bytes": file_size,
            "created_time": created_time,
            "modified_time": modified_time
        }
    except Exception as e:
        print(f"[!] Error extracting metadata: {e}")
        return {}

def lock_evidence(file_path, investigator_name="Investigator A"):
    """
    Logs the evidence file, calculates its hash, extracts metadata, 
    and saves a secure verification manifest (Chain of Custody record).
    """
    if not os.path.exists(file_path):
        print(f"[!] Error: Target file {file_path} does not exist.")
        return
        
    print(f"[*] Locking evidence: {file_path}...")
    
    # 1. Calculate the cryptographic fingerprint
    file_hash = calculate_sha256(file_path)
    if not file_hash:
        return
        
    # 2. Get metadata
    metadata = extract_file_metadata(file_path)
    
    # 3. Create the manifest dictionary
    manifest = {
        "filename": os.path.basename(file_path),
        "absolute_path": os.path.abspath(file_path),
        "sha256_hash": file_hash,
        "file_size_bytes": metadata.get("file_size_bytes"),
        "system_creation_date": metadata.get("created_time"),
        "system_modification_date": metadata.get("modified_time"),
        "locked_by": investigator_name,
        "lock_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save the manifest as a JSON file
    manifest_filename = f"{MANIFEST_DIR}/{os.path.basename(file_path)}.manifest.json"
    with open(manifest_filename, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
        
    print(f"\n================ FORENSIC LOCK REPORT ================")
    print(f"  File Locked:      {manifest['filename']}")
    print(f"  SHA-256 Hash:     {manifest['sha256_hash']}")
    print(f"  Size:             {manifest['file_size_bytes']} bytes")
    print(f"  Locked By:        {manifest['locked_by']}")
    print(f"  Lock Timestamp:   {manifest['lock_timestamp']}")
    print(f"======================================================\n")
    print(f"[SUCCESS] Forensic manifest created at: {manifest_filename}")
    return manifest_filename

def verify_evidence(file_path, manifest_path):
    """
    Verifies a file against its forensic manifest to check if it has been tampered with.
    """
    if not os.path.exists(file_path):
        print(f"[!] Verification Failed: File {file_path} does not exist.")
        return False
        
    if not os.path.exists(manifest_path):
        print(f"[!] Verification Failed: Manifest {manifest_path} does not exist.")
        return False
        
    # 1. Load the manifest
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    original_hash = manifest.get("sha256_hash")
    print(f"[*] Auditing integrity of: {file_path}...")
    print(f"    - Original Lock Timestamp: {manifest.get('lock_timestamp')}")
    print(f"    - Expected Hash:           {original_hash}")
    
    # 2. Recalculate current hash
    current_hash = calculate_sha256(file_path)
    print(f"    - Current Hash:            {current_hash}")
    
    # 3. Compare hashes
    if original_hash == current_hash:
        print("\n[SUCCESS] INTEGRITY VERIFIED: Evidence matches the original record exactly. Untampered.")
        return True
    else:
        print("\n[WARNING] SECURITY ALERT: EVIDENCE TAMPERING DETECTED!")
        print("    --> The file has been modified since it was forensic locked.")
        print("    --> THIS EVIDENCE IS INADMISSIBLE IN COURT.")
        return False

def create_sample_evidence():
    """Generates a dummy text file to act as our forensic evidence."""
    file_path = os.path.join(DATA_DIR, "chat_log_suspect.txt")
    evidence_text = """[2026-06-03 14:02:11] Suspect: "I was not at the location."
[2026-06-03 14:03:45] Suspect: "Wait, don't tell anyone I wrote that contract."
[2026-06-03 14:04:12] Accomplice: "Understood, deleting logs."
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(evidence_text)
    print(f"[+] Created mock evidence file at: {file_path}")
    return file_path

def main():
    print("=========================================================")
    print("      ANTIGRAVITY CYBER FORENSICS EVIDENCE LOCKER        ")
    print("=========================================================\n")
    
    # 1. Create a dummy evidence file to test
    evidence_file = create_sample_evidence()
    
    # 2. Forensic Lock the file (creates a secure manifest)
    manifest_file = lock_evidence(evidence_file, investigator_name="Aum (Forensic Investigator)")
    
    # 3. Verify the file right now (should pass, because it hasn't changed)
    print("\n--- Running Test 1: Immediate Verification ---")
    verify_evidence(evidence_file, manifest_file)
    
    # 4. TAMPER WITH THE EVIDENCE
    # We will simulate a hacker or malicious party editing the file by appending a tiny detail
    print("\n--- Simulating Tampering (Modifying one character) ---")
    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write(" ") # We just added a single space character at the end of the file!
    print("[!] TAMPERED: Added a single space character to the evidence file.")
    
    # 5. Verify the file again (should FAIL now!)
    print("\n--- Running Test 2: Verification After Tampering ---")
    verify_evidence(evidence_file, manifest_file)

if __name__ == "__main__":
    main()
