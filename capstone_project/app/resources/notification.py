from flask import Blueprint, request
from flask_restful import Resource, Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.notification import Notification
from ..extensions import db
from ..utils.responses import success_response, error_response

notification_bp = Blueprint('notification_bp', __name__)
api = Api(notification_bp)

class NotificationListResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user_id = current_user_id
        
        # specific to user, ordered by newest
        notes = Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc()).all()
            
        return success_response(data=[n.to_dict() for n in notes])

class NotificationReadResource(Resource):
    @jwt_required()
    def put(self, notification_id):
        current_user_id = get_jwt_identity()
        note = db.session.get(Notification, notification_id)
        
        if not note:
            return error_response("Notification not found", 404)
            
        if note.user_id != int(current_user_id):
             return error_response("Unauthorized", 403)
             
        note.is_read = True
        db.session.commit()
        
        return success_response(data=note.to_dict(), message="Marked as read")

api.add_resource(NotificationListResource, '/')
api.add_resource(NotificationReadResource, '/<int:notification_id>/read')
