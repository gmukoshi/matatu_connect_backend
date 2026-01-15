import base64
from datetime import datetime
import requests
import traceback
from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from requests.auth import HTTPBasicAuth

from app.utils.responses import success_response, error_response
from app.extensions import db

payment_bp = Blueprint('payment_bp', __name__)
api = Api(payment_bp)

def log_debug(msg):
    try:
        with open("payment_debug.log", "a") as f:
            f.write(f"{datetime.now()}: {msg}\n")
    except:
        pass

class MpesaHelper:
    """Helper class to handle Daraja API interactions"""
    
    @staticmethod
    def get_access_token():
        """Fetch OAuth2 access token from Safaricom"""
        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY', '').strip()
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET', '').strip()
        base_url = current_app.config.get('MPESA_API_BASE_URL')
        api_url = f"{base_url}/oauth/v1/generate?grant_type=client_credentials"
        
        try:
            res = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret), timeout=30)
            if res.status_code != 200:
                print(f"M-Pesa Token Error: {res.text}")
                return None
            return res.json().get('access_token')
        except Exception as e:
            log_debug(f"EXCEPTION IN MpesaHelper.get_access_token: {str(e)}")
            log_debug(traceback.format_exc())
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
        callback_url = current_app.config.get('MPESA_CALLBACK_URL', '').strip()
        print(f"DEBUG: Using CallBackURL: {callback_url}")
        log_debug(f"TRIGGERING STK PUSH. Phone: {phone_number}, Amount: {amount}. CallbackURL: {callback_url}")
        
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

        api_url = f"{current_app.config.get('MPESA_API_BASE_URL')}/mpesa/stkpush/v1/processrequest"
        print(f"M-Pesa Request: {payload}")
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
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
            
            # CRITICAL FIX: Update the User's phone number to the one being used for payment.
            # This ensures that when the callback comes (keyed by phone), we verify the correct User/Booking.
            booking = Booking.query.get(booking_id)
            if booking and booking.user:
                print(f"Updating User {booking.user.id} phone from {booking.user.phone_number} to {phone_number} for payment linking.")
                booking.user.phone_number = phone_number
                db.session.commit()

            stk_response = MpesaHelper.trigger_stk_push(phone_number, amount, booking_id)
            
            # Check if Safaricom accepted the request
            if stk_response.get('ResponseCode') == '0':
                checkout_id = stk_response.get('CheckoutRequestID')
                merchant_id = stk_response.get('MerchantRequestID')
                
                # Create Pending Payment Record
                new_payment = Payment(
                    booking_id=booking.id,
                    user_id=booking.user_id,
                    amount=float(amount),
                    method='mpesa',
                    status='pending',
                    checkout_request_id=checkout_id,
                    merchant_request_id=merchant_id
                )
                db.session.add(new_payment)
                db.session.commit()
                print(f"Created Pending Payment: {new_payment.id} | CheckoutID: {checkout_id}")

                return success_response(
                    message="STK Push sent. Please enter your M-Pesa PIN.",
                    data={
                        "CheckoutRequestID": checkout_id,
                        "MerchantRequestID": merchant_id,
                        "payment_id": new_payment.id
                    }
                )
            else:
                error_msg = stk_response.get('CustomerMessage') or \
                            stk_response.get('errorMessage') or \
                            'Unknown error'
                            
                return error_response(
                    message="M-Pesa request rejected", 
                    error=error_msg
                )

                return error_response(
                    message="M-Pesa request rejected", 
                    error=error_msg
                )

        except Exception as e:
            return error_response("Fintech service unavailable", error=str(e), status_code=500)

from ..models.booking import Booking
from ..models.payment import Payment
from ..models.user import User
from ..extensions import socketio

class MpesaCallbackResource(Resource):
    def post(self):
        """Handle M-Pesa IPN Callback"""
        try:
            data = request.get_json()
            log_debug(f"CALLBACK RECEIVED: {data}")
            if not data or 'Body' not in data:
                return error_response("Invalid callback data", status_code=400)

            stk_callback = data['Body']['stkCallback']
            result_code = stk_callback['ResultCode']
            
            # Extract basic info
            checkout_request_id = stk_callback['CheckoutRequestID']
            
            if result_code != 0:
                print(f"M-Pesa Transaction Failed: {stk_callback.get('ResultDesc')}")
                # We still return success to Safaricom to acknowledge receipt of callback
                return success_response(None, message="Callback received (failed tx)")

            # Successful Transaction
            meta_data = stk_callback['CallbackMetadata']['Item']
            log_debug("TRACE: Metadata extracted")
            
            # ... (unchanged lines) ...
            

            
            # Extract values from generic metadata list
            amount = next((item['Value'] for item in meta_data if item['Name'] == 'Amount'), 0)
            receipt_number = next((item['Value'] for item in meta_data if item['Name'] == 'MpesaReceiptNumber'), None)
            phone_number_raw = next((item['Value'] for item in meta_data if item['Name'] == 'PhoneNumber'), None)
            phone_number = str(phone_number_raw) if phone_number_raw else None
            log_debug(f"TRACE: Extracted Phone: {phone_number}, Amount: {amount}")
            
            # NEW LOGIC: Match by CheckoutRequestID first
            payment = Payment.query.filter_by(checkout_request_id=checkout_request_id).first()
            booking = None
            
            if payment:
                log_debug(f"Matched Pending Payment: {payment.id} for Booking {payment.booking_id}")
                payment.status = 'completed'
                payment.reference = receipt_number
                
                booking = Booking.query.get(payment.booking_id)
                if booking:
                    booking.status = 'confirmed'
                
                db.session.commit()
                # Ensure we have the latest state
                db.session.refresh(payment)
                if booking: db.session.refresh(booking)
                
                new_payment = payment
                
            else:
                log_debug("No pending payment found by CheckoutRequestID. Falling back to Phone Matching.")
                
                # FALLBACK LOGIC (Existing phone matching)
                # Let's try to find the User by phone first (existing logic)
                log_debug("TRACE: Attempting User Loopup now...")
                user = User.query.filter_by(phone_number=phone_number).first()
                if user:
                    log_debug(f"User matched: {user.name} (ID: {user.id})")
                else:
                     # Try adding/removing country code
                     if phone_number.startswith('254'):
                         alt_phone = '0' + phone_number[3:]
                         user = User.query.filter_by(phone_number=alt_phone).first()
                         if user: log_debug(f"User matched via alt phone: {user.name} (ID: {user.id})")
                
                if user:
                    # Find latest pending/confirmed booking
                    booking = Booking.query.filter_by(user_id=user.id).filter(
                        Booking.status.in_(['pending', 'confirmed'])
                    ).order_by(Booking.id.desc()).first()
                    
                    if booking:
                        log_debug(f"Initial booking found: ID {booking.id} | Status: {booking.status} | HasPayment: {bool(booking.payment)}")
                    else:
                        log_debug("No initial booking found for user.")

                    # If the booking is already paid, ignore it to prevent overwrites
                    if booking and booking.payment and booking.payment.status == 'completed':
                         log_debug(f"Booking {booking.id} already paid. Ignoring to prevent duplicate linking.")
                         booking = None
    
                if not booking:
                    log_debug(f"FAILED TO LINK: Phone {phone_number}. User: {user}")
                    print(f"Could not link payment {receipt_number} to a booking. Phone: {phone_number}. User Found: {user}")
                    return success_response(None, message="Callback received but no matching booking found")
                
                # Found booking! Update it.
                booking.status = 'confirmed'
                
                # Create Payment Record (Since none existed)
                new_payment = Payment(
                    booking_id=booking.id,
                    user_id=booking.user_id,
                    amount=float(amount),
                    method='mpesa',
                    status='completed',
                    reference=receipt_number,
                    checkout_request_id=checkout_request_id
                )
                db.session.add(new_payment)
                db.session.commit()
                
                payment = new_payment
                
                # Force SQLAlchemy to reload the 'payment' relationship on next access
                db.session.expire(booking, ['payment'])
                db.session.refresh(booking)
            
            # Force SQLAlchemy to reload the 'payment' relationship on next access
            db.session.expire(booking, ['payment'])
            db.session.refresh(booking)
            
            print(f"Payment Confirmed: {receipt_number} for Booking {booking.id}. Amount: {booking.payment.amount}")

            # 1. Emit to Commuter (User Room)
            socketio.emit('payment_received', {
                'id': new_payment.id,
                'booking_id': booking.id,
                'status': 'completed',
                'reference': receipt_number,
                'amount': amount,
                'date': new_payment.created_at.isoformat()
            }, room=f"user_{booking.user_id}")
            
            # 2. Emit to Matatu (Driver Room) - so they see the seat turn Red/Green tick
            socketio.emit('booking_updated', booking.to_dict(), room=f"matatu_{booking.matatu_id}")
            
            # 3. Emit to Sacco Managers for Revenue Update
            sacco_id = booking.matatu.sacco_id
            if sacco_id:
                print(f"Emitting payment update to Sacco {sacco_id}")
                socketio.emit('sacco_update', {'type': 'payment_received'}, room=f"sacco_{sacco_id}")

            return success_response(None, message="Payment processed successfully")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            log_debug(f"EXCEPTION IN CALLBACK: {str(e)}")
            log_debug(error_details)
            print(f"Callback Error: {e}")
            traceback.print_exc()
            return error_response("Processing failed", error=str(e), status_code=500)


class MpesaConfigCheckResource(Resource):
    def get(self):
        """Debug endpoint to verify M-Pesa Configuration"""
        consumer_key = current_app.config.get('MPESA_CONSUMER_KEY')
        consumer_secret = current_app.config.get('MPESA_CONSUMER_SECRET')
        shortcode = current_app.config.get('MPESA_SHORTCODE')
        passkey = current_app.config.get('MPESA_PASSKEY')
        callback_url = current_app.config.get('MPESA_CALLBACK_URL')
        
        status = {
            "MPESA_CONSUMER_KEY": "SET" if consumer_key and "your_" not in consumer_key else "MISSING/DEFAULT",
            "MPESA_CONSUMER_SECRET": "SET" if consumer_secret and "your_" not in consumer_secret else "MISSING/DEFAULT",
            "MPESA_SHORTCODE": shortcode,
            "MPESA_PASSKEY": "SET" if passkey else "MISSING",
            "MPESA_CALLBACK_URL": callback_url
        }
        
        # Test Token Generation
        try:
            token = MpesaHelper.get_access_token()
            status["access_token_generation"] = "SUCCESS" if token else "FAILED"
        except Exception as e:
            status["access_token_generation"] = f"ERROR: {str(e)}"
            
        return success_response(status, message="M-Pesa Config Status")

api.add_resource(MpesaPaymentResource, '/stk-push')
api.add_resource(MpesaCallbackResource, '/callback')
api.add_resource(MpesaConfigCheckResource, '/debug-config')