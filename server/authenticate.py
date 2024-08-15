from flask import  request, make_response, jsonify, session, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, current_user
from functools import wraps

# Local imports
from config import db, app, jwt
# Add your model imports
from models import User

authenticate_bp = Blueprint('authenticate_bp',__name__, url_prefix='/user')
auth_api = Api(authenticate_bp)

def init_jwt(app):
    jwt.init_app(app) 

@jwt.user_identity_loader
def user_identity_lookup(user_id):
    return user_id

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.get(User, identity)

def allow(*allowed_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user =  current_user
            user_role = user.role
            for role in allowed_roles:
                if role == user_role:
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
        role= data.get('role')
        if not role:
            role = 'user'
        
        if username and email and password:
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()

            if existing_user:
                return {'error': 'User already exists'}, 400
            new_user = User(username=username, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id
            access_token = create_access_token(identity = new_user.id)
            refresh_token = create_refresh_token(identity=new_user.id)
            return {'access_token': access_token,"refresh_token": refresh_token}


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
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {'user': user.serialize(), "access_token": access_token,"refresh_token":refresh_token}, 200


    @jwt_required(refresh=True)
    def get(self):
        token = create_access_token(identity= current_user.id )
        return {"token":token}

@authenticate_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'msg': 'User not found'}), 404

    return jsonify(user.serialize()), 200

@authenticate_bp.route('/update_user/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    current_user_id = get_jwt_identity()
    if current_user_id != id:
        return jsonify({"msg": "UNauthorized access"}), 403
    
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')

    user = db.session.get(User, current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if email:
        user.email = email
    if username:
        user.username = username

    db.session.commit()

    return jsonify({"msg": "User updated successfully", "user": user.to_dict()}), 200

@authenticate_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return '', 204

# Token refreshing
@authenticate_bp.route('/refresh_token', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify(access_token=new_access_token), 200
# routes
auth_api.add_resource(Register, '/register')
auth_api.add_resource(Login, '/login')
