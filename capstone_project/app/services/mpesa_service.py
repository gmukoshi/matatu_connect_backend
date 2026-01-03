import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
import base64
from flask import current_app

class MpesaService:
    @staticmethod
    def get_access_token():
        """Generates the OAuth2 access token from Daraja."""
        url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        consumer_key = current_app.config['MPESA_CONSUMER_KEY']
        consumer_secret = current_app.config['MPESA_CONSUMER_SECRET']
        
        try:
            response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
            response.raise_for_status()
            return response.json().get('access_token')
        except Exception as e:
            current_app.logger.error(f"M-Pesa Token Error: {str(e)}")
            return None

    @staticmethod
    def initiate_stk_push(phone_number, amount, booking_reference):
        """Triggers the STK Push popup on the user's phone."""
        access_token = MpesaService.get_access_token()
        if not access_token:
            return {"error": "Failed to authenticate with M-Pesa"}, 500

        # M-Pesa requires phone in format: 2547XXXXXXXX
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        shortcode = current_app.config['MPESA_SHORTCODE']
        passkey = current_app.config['MPESA_PASSKEY']
        
        # Password = base64(shortcode + passkey + timestamp)
        data_to_encode = f"{shortcode}{passkey}{timestamp}"
        password = base64.b64encode(data_to_encode.encode()).decode('utf-8')

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": current_app.config['MPESA_CALLBACK_URL'],
            "AccountReference": booking_reference,
            "TransactionDesc": f"Payment for {booking_reference}"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json(), response.status_code
        except Exception as e:
            return {"error": str(e)}, 500