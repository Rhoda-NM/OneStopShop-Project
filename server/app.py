from flask import Flask
from config import app, db, api
from flask_migrate import Migrate 
from flask import Flask, make_response,jsonify,session,request, current_app
from flask_restful import Resource, Api
from functools import wraps
import bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta

from models import Product,OrderItem,Order



class ProductResource(Resource):
    def get(self):
        products = [product.to_dict() for product in Product.query.all()]
        return products,200 
    
    def post(self):
        data = request.get_json()
        product = Product(name=data['name'], category=data['category'], price=data['price'], description=data['description'], stock=data['stock'])
        db.session.add(product)
        db.session.commit()
        return product.to_dict(), 201
    
class ProductById(Resource):
    def get(self, product_id):
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        return product.to_dict(), 200
    
    def patch(self, product_id):
        product = Product.query.filter(product_id == product_id).first()
        data=request.get_json()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        for key, value in data.items():
            if key != 'id' and hasattr(product, key):
                setattr(product, key, value)
            try:
                db.session.commit()
                return product.to_dict(), 200
            except Exception as e:
                return jsonify({"message": str(e)}), 400
    def delete(self, product_id):
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        db.session.delete(product)
        return product.to_dict(), 204
    
            
api.add_resource(ProductResource,'/products',endpoint='products')
api.add_resource(ProductById,'/products/<int:product_id>',endpoint='product_by_id')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

