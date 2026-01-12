from flask import Blueprint, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.rating import Rating
from ..extensions import db
from ..utils.responses import success_response, error_response

rating_bp = Blueprint('rating_bp', __name__)
api = Api(rating_bp)

class RatingListResource(Resource):
    @jwt_required()
    def get(self):
        user_info = get_jwt_identity()
        role = user_info.get('role')
        
        if role == 'sacco_manager':
            # Manager sees all ratings involved with their Sacco (for now all ratings to simplify)
            ratings = Rating.query.all()
        else:
            ratings = Rating.query.filter_by(user_id=user_info['id']).all()
            
        return success_response(data=[r.to_dict() for r in ratings], message="Ratings retrieved")

    @jwt_required()
    def post(self):
        user_info = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('matatu_id') or not data.get('score'):
            return error_response("matatu_id and score required", 400)

        try:
            rating = Rating(
                user_id=user_info['id'],
                matatu_id=data['matatu_id'],
                score=data['score'],
                comment=data.get('comment')
            )
            rating.save()
            return success_response(data=rating.to_dict(), message="Rating submitted", status_code=201)
        except ValueError as e:
             return error_response(str(e), 400)
        except Exception as e:
            return error_response(str(e), 500)

api.add_resource(RatingListResource, '/')
