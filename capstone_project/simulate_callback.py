
import requests
import json
from app import create_app, db
from app.models.user import User
from app.models.booking import Booking
from app.models.matatu import Matatu

app = create_app()

def run_simulation():
    with app.app_context():
        # 1. Setup Data
        print("--- 1. Setting up Test Data ---")
        
        # Get a user (Commuter)
        user = User.query.filter_by(role='passenger').first()
        if not user:
            print("No passenger found. Falling back to ANY user...")
            user = User.query.first()
            
        if not user:
            print("CRITICAL: No users found in DB. Cannot simulate.")
            return

        # Ensure user has a phone number (crucial for matching)
        import random
        phone_suffix = random.randint(100000000, 999999999)
        test_phone = f"254{phone_suffix}"
            
        if user:
            user.phone_number = test_phone
            db.session.commit()
            print(f"Updated User {user.name} with unique phone {user.phone_number}")
        
        # Get a matatu
        matatu = Matatu.query.first()
        if not matatu:
            print("No matatu found.")
            return

        # Create a PENDING booking
        booking = Booking(
            user_id=user.id,
            matatu_id=matatu.id,
            seat_number="1",
            status="pending"
        )
        db.session.add(booking)
        db.session.commit()
        print(f"Created Pending Booking ID: {booking.id} for User: {user.name} ({user.phone_number})")

        # 2. Simulate Callback Payload
        print("\n--- 2. Sending Fake M-Pesa Callback ---")
        
        # Generate random receipt
        import random
        import string
        receipt_no = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

        payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "29115-34620542-1",
                    "CheckoutRequestID": "ws_CO_191220191020363925",
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 50.00},
                            {"Name": "MpesaReceiptNumber", "Value": receipt_no},
                            {"Name": "TransactionDate", "Value": 20191219102115},
                            {"Name": "PhoneNumber", "Value": int(test_phone)} 
                        ]
                    }
                }
            }
        }

        # 3. POST to Backend
        try:
            # Assuming backend is running on 5000
            url = "http://localhost:5000/api/payments/callback"
            headers = {'Content-Type': 'application/json'}
            
            print(f"POSTing to {url}...")
            response = requests.post(url, json=payload, headers=headers)
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                print("\n✅ Success! The backend accepted the callback.")
                print(">>> CHECK YOUR DASHBOARDS NOW <<<")
                print("If they updated, your code works but your 'Callback URL' is likely not reachable by Safaricom.")
            else:
                print("\n❌ Backend rejected the callback.")
                    
        except Exception as e:
            print(f"\n❌ Request Failed: {e}")
            print("Make sure your Flask server is running on port 5000!")

if __name__ == "__main__":
    run_simulation()
