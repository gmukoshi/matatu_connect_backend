import requests
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.matatu import Matatu
import uuid

app = create_app()

def verify_fix():
    with app.app_context():
        print("--- SETUP: Creating Test Data ---")
        # 1. Get a user and matatu
        user = User.query.first()
        matatu = Matatu.query.first()
        
        if not user or not matatu:
            print("Error: Need at least one user and matatu.")
            return

        # 2. Create a Booking
        booking = Booking(
            user_id=user.id,
            matatu_id=matatu.id,
            seat_number="1A",
            status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        print(f"Created Booking: {booking.id}")

        # 3. Create a Pending Payment (Simulate STK Push)
        checkout_id = f"ws_CO_{uuid.uuid4()}"
        payment = Payment(
            booking_id=booking.id,
            user_id=user.id,
            amount=100,
            method='mpesa',
            status='pending',
            checkout_request_id=checkout_id,
            merchant_request_id=f"MR_{uuid.uuid4()}"
        )
        db.session.add(payment)
        db.session.commit()
        print(f"Created Pending Payment: {payment.id} with CheckoutID: {checkout_id}")

        # 4. Simulate Callback
        print("\n--- ACTION: Simulating Callback ---")
        callback_payload = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": payment.merchant_request_id,
                    "CheckoutRequestID": checkout_id,
                    "ResultCode": 0,
                    "ResultDesc": "The service request is processed successfully.",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "Amount", "Value": 100},
                            {"Name": "MpesaReceiptNumber", "Value": "QWE123456"},
                            {"Name": "TransactionDate", "Value": 20231212121212},
                            {"Name": "PhoneNumber", "Value": 254712345678}
                        ]
                    }
                }
            }
        }
        
        # Use test client to post to callback
        client = app.test_client()
        response = client.post('/api/payments/callback', json=callback_payload)
        
        print(f"Callback Response: {response.status_code} - {response.get_json()}")

        # 5. Verify Results
        print("\n--- VERIFICATION ---")
        # Refresh objects
        db.session.expire_all()
        payment = Payment.query.get(payment.id)
        booking = Booking.query.get(booking.id)
        
        print(f"Payment Status: {payment.status} (Expected: completed)")
        print(f"Payment Reference: {payment.reference} (Expected: QWE123456)")
        print(f"Booking Status: {booking.status} (Expected: confirmed)")

        if payment.status == 'completed' and booking.status == 'confirmed':
            print("\n>>> SUCCESS: Fix Verified! Payment linked by ID. <<<")
        else:
            print("\n>>> FAILURE: Payment not linked correctly. <<<")

        # Cleanup
        db.session.delete(payment)
        db.session.delete(booking)
        db.session.commit()

if __name__ == "__main__":
    verify_fix()
