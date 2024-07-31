from flask import Flask
from config import app, db, api
from flask_migrate import Migrate 
from flask import Flask, make_response,jsonify,session,request, current_app
from flask_restful import Resource, Api
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import datetime, timedelta

from models import Product,OrderItem,Order
from authenticate import authenticate_bp

app.register_blueprint(authenticate_bp)

@app.route('/')
def index():
    return '<h1>Project Server </h1>'
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
    
class WishlistItems(Resource):
    def get(self):
        user_id = get_jwt_identity()
        products = [product.to_dict() for product in Product.query.all() if product.user_id == user_id ]
        if not products:
            return jsonify({"message": "Product not found"}), 404
        return products, 200
    def delete(self):
        data = request.get_json()
        wishlist = Wishlist.query.filter(Wishlist.id == data['wishlist_id']).first()
        if not wishlist:
            return jsonify({"message": "Wishlist not found"}), 404
        db.session.delete(wishlist)
        return wishlist.to_dict(), 204
    def post(self,product_id):
        user_id = get_jwt_identity()
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        wishlist = Wishlist(user_id=user_id, product_id=product_id)
        db.session.add(wishlist)
        db.session.commit()
        return wishlist.to_dict(), 201

class UserSpecific(Resource):
    def get(self):
        user_id = get_jwt_identity()

        # Fetch user data
        user_views = ViewingHistory.query.filter_by(user_id=user_id).order_by(ViewingHistory.viewed_at.desc()).all()
        user_searches = SearchQuery.query.filter_by(user_id=user_id).order_by(SearchQuery.searched_at.desc()).all()
        user_engagements = Engagement.query.filter_by(user_id=user_id).order_by(Engagement.engaged_at.desc()).all()

        # Initialize a dictionary to score products
        product_scores = {}

        # Add scores for recently viewed products
        for view in user_views:
            if view.product_id not in product_scores:
                product_scores[view.product_id] = 0
            product_scores[view.product_id] += 1  # Add a basic score, can be weighted based on recency

        # Add scores for products related to recent search queries
        for search in user_searches:
            related_products = Product.query.filter(Product.name.ilike(f"%{search.query}%")).all()
            for product in related_products:
                if product.id not in product_scores:
                    product_scores[product.id] = 0
                product_scores[product.id] += 2  # Higher weight for search relevance

        # Add scores for highly engaged products
        for engagement in user_engagements:
            if engagement.product_id not in product_scores:
                product_scores[engagement.product_id] = 0
            product_scores[engagement.product_id] += engagement.watch_time / 60  # Score based on watch time in minutes

        # Sort products by score in descending order and get top N products
        top_product_ids = sorted(product_scores, key=product_scores.get, reverse=True)#[:10]
        top_products = Product.query.filter(Product.id.in_(top_product_ids)).all()

        return {'recommended_products': [product.to_dict() for product in top_products]}, 200


api.add_resource(UserSpecific,'/recommended_products',endpoint='recommended_products')
api.add_resource(WishlistItems,'/wishlists',endpoint='wishlists')            
api.add_resource(ProductResource,'/products',endpoint='products')
api.add_resource(ProductById,'/products/<int:product_id>',endpoint='product_by_id')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
