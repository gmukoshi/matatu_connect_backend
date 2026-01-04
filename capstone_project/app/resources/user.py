from flask_restful import Resource
from ..models.user import User
from ..extensions import db
from ..utils.responses import make_response


class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return make_response(
            message="Users fetched successfully",
            data=[u.to_dict() for u in users],
            status=200,
        )


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status=404)
        return make_response(message="User fetched successfully", data=user.to_dict(), status=200)

    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return make_response(message="Not found", error="User not found", status=404)

        try:
            db.session.delete(user)
            db.session.commit()
            return make_response(message="User deleted successfully", status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)
