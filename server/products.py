from flask import  request, make_response, jsonify, session, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, current_user
from functools import wraps

# Local imports
from config import db, app
# Add your model imports
from models import User

authenticate_bp = Blueprint('authenticate_bp',__name__, url_prefix='/user')
auth_api = Api(authenticate_bp)

jwt = JWTManager()
auth_api = Api(authenticate_bp)

def init_jwt(app):
    jwt.init_app(app) 
