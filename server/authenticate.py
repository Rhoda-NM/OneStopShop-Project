from flask import  request, make_response, jsonify, session, Blueprint
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

# Local imports
from config import db, app
# Add your model imports
from models import User

authenticate_bp = Blueprint('authenticate_bp',__name__, url_prefix='/user')

jwt = JWTManager()
auth_api = Api(authenticate_bp)

def allow(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user =  current_user
            roles = [role.name  for role in user.roles]
            for role in allowed_roles:
                if role in roles:
                    return fn(*args, **kwargs)
            else:
                return {"msg":"Access Denied"}, 403

        return decorator

    return wrapper