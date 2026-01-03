from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from app.models.payment import Payment
from app.services.mpesa_service import MpesaService
from app.utils.responses import api_response
from app.extensions import db

class InitiatePayment(Resource):
    @jwt_required()
    def post(self):
        data = request.get_json()
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        booking_id = data.get('booking_id')

        if not all([phone_number, amount, booking_id]):
            return api_response("Missing required payment fields", status="error", status_code=400)

        # Trigger STK Push
        response, status_code = MpesaService.initiate_stk_push(
            phone_number=phone_number,
            amount=amount,
            booking_reference=f"BK-{booking_id}"
        )

        if status_code == 200 and response.get('ResponseCode') == '0':
            new_payment = Payment(
                booking_id=booking_id,
                amount=amount,
                phone_number=phone_number,
                checkout_request_id=response.get('CheckoutRequestID'),
                status='pending'
            )
            db.session.add(new_payment)
            db.session.commit()
            
            return api_response(
                message="STK Push initiated. Check your phone.",
                data={"checkout_id": response.get('CheckoutRequestID')},
                status_code=200
            )
        
        return api_response("M-Pesa request failed", data=response, status="error", status_code=400)