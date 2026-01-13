
import os
from dotenv import load_dotenv

def verify_callback_url():
    print("--- Verifying MPESA_CALLBACK_URL ---")
    
    # 1. Force reload from file (bypass OS cache if possible)
    load_dotenv(override=True)
    
    url = os.getenv("MPESA_CALLBACK_URL")
    
    if not url:
        print("❌ ERROR: MPESA_CALLBACK_URL is missing from .env")
        return

    print(f"Current Value: '{url}'")
    
    if "your-domain.com" in url:
        print("❌ ERROR: You are still using the default placeholder domain.")
        print("-> Please replace 'your-domain.com' with your Ngrok ID.")
        
    elif "localhost" in url or "127.0.0.1" in url:
        print("❌ ERROR: You are using localhost. Safaricom cannot access this.")
        print("-> Use the Ngrok URL (e.g., https://xyz.ngrok-free.app)")
        
    elif url.startswith("http://"):
        print("❌ ERROR: You are using 'http://'. Safaricom requires 'https://'.")
        print("-> Change to 'https://'")
        
    elif not url.startswith("https://"):
        print("❌ ERROR: Invalid protocol. Must start with 'https://'")
        
    elif " " in url:
        print("❌ ERROR: The URL contains spaces. Please remove them.")
        
    else:
        print("✅ Checks Passed: format looks correct.")
        print("If it still fails, ensure the Ngrok tunnel is actually running.")
        
if __name__ == "__main__":
    verify_callback_url()
