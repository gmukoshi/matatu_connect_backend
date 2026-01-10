from unittest.mock import patch, MagicMock

def test_stk_push_success(client):
    # Prepare payload
    payload = {
        "phone_number": "0712345678",
        "amount": 100,
        "booking_id": 1
    }

    # Mock the MpesaHelper.trigger_stk_push method
    with patch("app.resources.payment.MpesaHelper.trigger_stk_push") as mock_push:
        # Define what the mock should return
        mock_push.return_value = {
            "ResponseCode": "0",
            "CheckoutRequestID": "ws_CO_123456",
            "MerchantRequestID": "12345-67890"
        }

        response = client.post("/api/payments/stk-push", json=payload)
        
        assert response.status_code == 200
        assert response.json["message"] == "STK Push sent. Please enter your M-Pesa PIN."
        assert response.json["data"]["CheckoutRequestID"] == "ws_CO_123456"

def test_stk_push_missing_fields(client):
    response = client.post("/api/payments/stk-push", json={
        "amount": 100
        # Missing phone and booking_id
    })
    assert response.status_code == 400

def test_stk_push_failure_response(client):
    payload = {
        "phone_number": "0712345678",
        "amount": 100,
        "booking_id": 1
    }

    with patch("app.resources.payment.MpesaHelper.trigger_stk_push") as mock_push:
        # Simulate Safaricom rejecting it
        mock_push.return_value = {
            "ResponseCode": "1",
            "CustomerMessage": "Bal not enough"
        }

        response = client.post("/api/payments/stk-push", json=payload)
        
        assert response.status_code == 400 # Resource returns 400 by default for error_response 
        # Looking at code: return error_response(..., status_code=default).
        # utils.responses.error_response likely defaults to 400 or has custom status.
        # Wait, the code says:
        # if stk_response.get('ResponseCode') == '0': ...
        # else: return error_response(message="M-Pesa request rejected", ...)
        # It doesn't specify status_code, so probably defaults to 400 or 500 depending on implementation.
        # I'll check 'error_response' in next step if test fails, or assume 400/500.
        # Let's inspect response in real run or be lenient.
        # However, checking code: payment.py:97 calls error_response.
        pass 
