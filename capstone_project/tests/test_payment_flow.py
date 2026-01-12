from app.models.booking import Booking
from app.models.matatu import Matatu
from app.models.user import User
from app.extensions import db

def test_driver_initiates_payment(client):
    # 1. Setup: Create Driver, Matatu, Commuter, Booking
    # Register Driver
    res = client.post("/api/auth/register", json={
        "email": "driver_pay@test.com", "password": "pass", 
        "name": "Driver Pay", "role": "driver", "licence": "DL-PAY"
    })
    driver_token = res.json["access_token"]
    driver_id = res.json["user"]["id"]
    
    # Create Matatu (Need Sacco Manager or Admin usually, but direct DB for speed)
    matatu = Matatu(plate_number="KBB 111B", capacity=14, driver_id=driver_id, sacco_id=1)
    db.session.add(matatu)
    db.session.commit()
    
    # Register Commuter
    res = client.post("/api/auth/register", json={
        "email": "commuter_pay@test.com", "password": "pass", "name": "Commuter Pay"
    })
    commuter_token = res.json["access_token"]
    
    # Create Booking
    res = client.post("/api/bookings/", headers={"Authorization": f"Bearer {commuter_token}"}, json={
        "matatu_id": matatu.id, "seat_number": "1A"
    })
    booking_id = res.json["data"]["id"]

    # 2. Driver triggers payment
    # Mocking external requests to Safaricom is tricky without a library, 
    # but our endpoint calls requests.post. Use unittest.mock or just check failure if no creds.
    # For now, let's just check the endpoint validates and tries.
    
    # Note: Authorization isn't strictly enforced on /stk-push for now based on code (it's public?),
    # but let's assume valid data.
    
    # Using a fake shortcode in config usually implies failure or mock. 
    # Let's see how MpesaHelper behaves.
    
    payment_data = {
        "phone_number": "0712345678",
        "amount": 100,
        "booking_id": booking_id
    }
    
    # We expect this to likely fail 500 or 400 because of missing credentials/network in test env,
    # UNLESS we mock `app.resources.payment.MpesaHelper.get_access_token` and `trigger_stk_push`.
    
    from unittest.mock import patch
    with patch('app.resources.payment.MpesaHelper.get_access_token') as mock_token:
        with patch('app.resources.payment.MpesaHelper.trigger_stk_push') as mock_push:
            mock_token.return_value = "fake_access_token"
            mock_push.return_value = {
                "ResponseCode": "0", "CheckoutRequestID": "ws_CO_123", "MerchantRequestID": "12345"
            }
            
            res = client.post("/api/payments/stk-push", json=payment_data)
            
            assert res.status_code == 200
            assert res.json["status"] == "success"
            assert "Please enter your M-Pesa PIN" in res.json["message"]
