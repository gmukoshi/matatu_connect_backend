from flask import request, Blueprint # Ensure Blueprint is imported
from flask_restful import Resource, Api # Ensure Api is imported

from ..models.matatu import Matatu
from ..extensions import db
from ..utils.responses import make_response

# 1. DEFINE THE BLUEPRINT (This is what __init__.py is looking for!)
matatu_bp = Blueprint('matatu_bp', __name__)
api = Api(matatu_bp)

class MatatuListResource(Resource):
    # ... your existing GET and POST code ...
    pass

class MatatuResource(Resource):
    # ... your existing GET, PATCH, and DELETE code ...
    pass

# 2. ATTACH THE CLASSES TO THE API
api.add_resource(MatatuListResource, '/')
api.add_resource(MatatuResource, '/<int:matatu_id>')