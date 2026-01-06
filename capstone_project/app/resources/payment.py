from flask import Blueprint, request
from flask_restful import Api, Resource
from app.utils.responses import success_response, error_response
# In a real scenario, you'd import your M-Pesa helper here
# from app.services.mpesa import trigger_stk_push 

# THIS VARIABLE MUST MATCH YOUR __init__.py IMPORT
payment_bp = Blueprint('payment_bp', __name__)
api = Api(payment_bp)

class MpesaPaymentResource(Resource):
    def post(self):
        """Triggers an M-Pesa STK Push to the commuter's phone"""
        data = request.get_json()
        phone_number = data.get('phone_number')
        amount = data.get('amount')
        booking_id = data.get('booking_id')

        if not phone_number or not amount:
            return error_response("Phone number and amount are required", status_code=400)

        try:
            # Here you would call your Daraja API logic
            # response = trigger_stk_push(phone_number, amount, booking_id)
            
            return success_response(
                message="STK Push sent successfully. Please check your phone.",
                data={"checkout_request_id": "ws_CO_123456789"}
            )
        except Exception as e:
            return error_response("Payment trigger failed", error=str(e), status_code=500)

# Add the resource to the API
api.add_resource(MpesaPaymentResource, '/stk-push')