from flask import request
from flask_restful import Resource
from ..models.matatu import Matatu
from ..extensions import db
from ..utils.responses import make_response


class MatatuListResource(Resource):
    def get(self):
        try:
            matatus = Matatu.query.all()
            data = [m.to_dict() for m in matatus]
            return make_response(data=data, message="Matatus fetched successfully", status=200)
        except Exception as e:
            return make_response(message="Error fetching matatus", error=str(e), status=500)

    def post(self):
        data = request.get_json() or {}

        if not data.get("plate_number"):
            return make_response(
                message="Validation Error",
                error="Missing fields: plate_number",
                status=400
            )

        new_matatu = Matatu(
            plate_number=data["plate_number"],
            capacity=data.get("capacity"),
            route_id=data.get("route_id")
        )

        try:
            db.session.add(new_matatu)
            db.session.commit()
            return make_response(
                message="Matatu created successfully",
                data=new_matatu.to_dict(),
                status=201
            )
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)


class MatatuResource(Resource):
    def get(self, matatu_id):
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status=404)
        return make_response(message="Matatu fetched successfully", data=matatu.to_dict(), status=200)

    def patch(self, matatu_id):
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status=404)

        body = request.get_json() or {}
        allowed_fields = {"plate_number", "capacity", "route_id"}
        updates = {k: v for k, v in body.items() if k in allowed_fields}

        if not updates:
            return make_response(message="Validation Error", error="No valid fields to update", status=400)

        for key, value in updates.items():
            setattr(matatu, key, value)

        try:
            db.session.commit()
            return make_response(message="Matatu updated successfully", data=matatu.to_dict(), status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)

    def delete(self, matatu_id):
        matatu = Matatu.query.get(matatu_id)
        if not matatu:
            return make_response(message="Not found", error="Matatu not found", status=404)

        try:
            db.session.delete(matatu)
            db.session.commit()
            return make_response(message="Matatu deleted successfully", status=200)
        except Exception as e:
            db.session.rollback()
            return make_response(message="Database Error", error=str(e), status=500)
