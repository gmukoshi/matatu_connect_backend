from app import create_app
from app.resources.payment import MpesaHelper
from app.config import Config
import logging

# Configure logging to print to console
logging.basicConfig(level=logging.DEBUG)

def test_mpesa_connection():
    app = create_app()
    with app.app_context():
        print("--- M-Pesa Debug Start ---")
        
        # Check if credentials are placeholders
        key = app.config.get('MPESA_CONSUMER_KEY')
        secret = app.config.get('MPESA_CONSUMER_SECRET')
        
        print(f"Consumer Key: Length={len(key)}, HasWhitespace={any(c.isspace() for c in key)}")
        print(f"Consumer Secret: Length={len(secret)}, HasWhitespace={any(c.isspace() for c in secret)}")
        
        print(f"Consumer Key Set: {key != 'your_consumer_key_here'}")
        print(f"Consumer Secret Set: {secret != 'your_consumer_secret_here'}")
        
        if key == 'your_consumer_key_here':
            print("ERROR: Using default placeholder credentials! Please update .env")
            return

        helper = MpesaHelper()
        
        print("Attempting to generate access token...")
        try:
            token = helper.get_access_token()
            if token:
                print("SUCCESS: Access Token Generated!")
                print(f"Token: {token[:10]}... (truncated)")
            else:
                print("FAILURE: No token returned. Check previous logs for 'M-Pesa Token Error'.")
        except Exception as e:
            print(f"EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_mpesa_connection()
