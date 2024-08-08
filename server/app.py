from flask import Flask
from config import get_config, db, migrate, bcrypt, jwt, api, cors
from flask_migrate import Migrate 
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_restful import  Api
from flask_sqlalchemy import SQLAlchemy

jwt = JWTManager()

def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    api.init_app(app)
    cors.init_app(app)

    from authenticate import authenticate_bp
    from products import product_bp
    from orders import order_bp
    from wishlist import wishlist_bp    
    from search import search_bp

    app.register_blueprint(authenticate_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(search_bp)


    return app



if __name__ == '__main__':
    app = create_app('development')
    app.run(port=5555, debug=True)
