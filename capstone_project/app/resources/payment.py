import base64
from datetime import datetime
import requests
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from requests.auth import HTTPBasicAuth

from app.utils.responses import success_response, error_response
from app.extensions import db

payment_bp = Blueprint('payment_bp', __name__)
api = Api(payment_bp)

class MpesaHelper:
    """Helper class to handle Daraja API interactions"""
    
    @staticmethod
    def get_access_token():
        """Fetch OAuth2 access token from Safaricom"""
        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        
        try:
            res = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            print(f"M-Pesa Token Error: {res.text}")
            return res.json().get('access_token')
        except Exception as e:
            print(f"M-Pesa Token Exception: {e}")
            return None

    @staticmethod
    def trigger_stk_push(phone_number, amount, booking_id):
        """Send the actual STK Push request"""
        access_token = MpesaHelper.get_access_token()
        if not access_token:
            print("Failed to generate M-Pesa access token")
            raise Exception("Failed to generate M-Pesa access token")

        # Configuration from your app config
        business_short_code = current_app.config.get('MPESA_SHORTCODE')
        passkey = current_app.config.get('MPESA_PASSKEY')
        callback_url = current_app.config.get('MPESA_CALLBACK_URL')
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(
            (business_short_code + passkey + timestamp).encode()
        ).decode('utf-8')

        headers = {"Authorization": f"Bearer {access_token}"}
        
        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number, # Commuter's phone
            "PartyB": business_short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": f"BK-{booking_id}",
            "TransactionDesc": f"Payment for Booking {booking_id}"
        }

        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        print(f"M-Pesa Request: {payload}")
        response = requests.post(api_url, json=payload, headers=headers)
        print(f"M-Pesa Response: {response.text}")
        return response.json()

class MpesaPaymentResource(Resource):
    def post(self):
        """API Endpoint to trigger STK Push"""
        data = request.get_json() or {}
        phone_number = data.get('phone_number') # Format: 2547XXXXXXXX
        amount = data.get('amount')
        booking_id = data.get('booking_id')

        if not all([phone_number, amount, booking_id]):
            return error_response("Missing phone_number, amount, or booking_id", status_code=400)

        try:
            # Normalize phone number to Safaricom format
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif phone_number.startswith('+'):
                phone_number = phone_number[1:]

            stk_response = MpesaHelper.trigger_stk_push(phone_number, amount, booking_id)
            
            # Check if Safaricom accepted the request
            if stk_response.get('ResponseCode') == '0':
                return success_response(
                    message="STK Push sent. Please enter your M-Pesa PIN.",
                    data={
                        "CheckoutRequestID": stk_response.get('CheckoutRequestID'),
                        "MerchantRequestID": stk_response.get('MerchantRequestID')
                    }
                )
            else:
                return error_response(
                    message="M-Pesa request rejected", 
                    error=stk_response.get('CustomerMessage', 'Unknown error')
                )

        except Exception as e:
            return error_response("Fintech service unavailable", error=str(e), status_code=500)

api.add_resource(MpesaPaymentResource, '/stk-push')