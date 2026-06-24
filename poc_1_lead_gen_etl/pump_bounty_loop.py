import time
import subprocess
import os

# ==============================================================================
# AUM'S PUMP.FUN SCANNER LOOP WRAPPER
# Runs the main bounty scanner script every 3 minutes in an infinite loop.
# Bypasses PythonAnywhere's task scheduler restrictions for free accounts.
# ==============================================================================

def main():
    print("=========================================================")
    print("      AUM'S PUMP.FUN SCANNER BACKGROUND DAEMON LOOP      ")
    print("=========================================================\n")
    print("[+] Scanner daemon loop started. Press Ctrl+C to terminate.")
    
    interval_seconds = 180 # 3 minutes delay between scans
    
    while True:
        try:
            print(f"\n[*] Starting scan at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
            
            # Execute the scanner script as a subprocess
            result = subprocess.run(["python", "pump_bounty_bot.py"], capture_output=True, text=True)
            
            # Print output logs to PythonAnywhere console
            print(result.stdout)
            if result.stderr:
                print("[!] Error logs:")
                print(result.stderr)
                
        except Exception as e:
            print(f"[!] Loop execution error: {e}")
            
        print(f"[*] Sleeping for {interval_seconds} seconds...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    main()
