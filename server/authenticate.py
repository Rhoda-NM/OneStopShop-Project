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

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()

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

register_args = reqparse.RequestParser()
register_args.add_argument('email')
register_args.add_argument('password')
register_args.add_argument('username')


login_args = reqparse.RequestParser()
login_args.add_argument('email')
login_args.add_argument('password')

@authenticate_bp.route('/hello')
def index():
    return '<h1>Hey user </h1>'
class Register(Resource):

    def post(self):

        data = register_args.parse_args()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        if username and email and password:
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                return {'error': 'User already exists'}, 400
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            access_token = create_access_token(identity = new_user.id)

            return {'User': new_user.to_dict(), 'access_token': access_token}


        return {'error': '422 Unprocessable Entity'}, 422


class Login(Resource):

    def post(self):
        data = login_args.parse_args()
        password = data.get('password')
        # check if the user exists in our db
        user = User.query.filter_by(email=data.get('email')).first()
        if user and user.authenticate(password):
            session['user_id'] =user.id
            # login
            token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {user.to_dict()}


    @jwt_required(refresh=True)
    def get(self):
        token = create_access_token(identity= current_user.id )
        return {"token":token}



# routes
auth_api.add_resource(Register, '/register')
auth_api.add_resource(Login, '/login')
