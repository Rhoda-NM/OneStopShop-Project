from flask import Flask
from config import app, db, api
from flask_migrate import Migrate 
from flask import Flask, make_response,jsonify,session,request, current_app
from flask_restful import Resource, Api
from functools import wraps

from authenticate import authenticate_bp
from products import product_bp
from orders import order_bp

app.register_blueprint(authenticate_bp)
app.register_blueprint(product_bp)
app.register_blueprint(order_bp)

@app.route('/')
def index():
    return '<h1>Project Server </h1>'

if __name__ == '__main__':
    app.run(port=5555, debug=True)
