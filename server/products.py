from flask import Flask, make_response,jsonify,session,request, current_app, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from config import api, jwt, db, app

# Add your model imports
from models import Product, Wishlist, ViewingHistory, SearchQuery, Engagement, ViewingHistory, SearchQuery, Engagement, Wishlist
from authenticate import allow

product_bp = Blueprint('product_bp',__name__, url_prefix='/api')
product_api = Api(product_bp)

def init_jwt(app):
    jwt.init_app(app) 

class ProductResource(Resource):
    def get(self):
        products = [product.to_dict() for product in Product.query.all()]
        return products,200 
    
    @jwt_required
    @allow('admin')
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()
        product = Product(name=data['name'], category=data['category'], price=data['price'], description=data['description'], stock=data['stock'], user_id=current_user_id)
        db.session.add(product)
        db.session.commit()
        return product.to_dict(), 201
    
class ProductById(Resource):
    def get(self, product_id):
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        return product.to_dict(), 200
    @jwt_required
    def patch(self, product_id):
        current_user_id = get_jwt_identity()
        product = Product.query.filter(product_id == product_id).first()
        data=request.get_json()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        if product.user_id != current_user_id:
            for key, value in data.items():
                if key != 'id' and hasattr(product, key):
                    setattr(product, key, value)
                try:
                    db.session.commit()
                    return product.to_dict(), 200
                except Exception as e:
                    return jsonify({"message": str(e)}), 400
        else:
            return jsonify({"message": "User not authorized"}), 401

    @jwt_required      
    def delete(self, product_id):
        current_user_id = get_jwt_identity
        product = Product.query.filter(Product.id == product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        if product.user_id !=current_user_id:
            return jsonify({"message": "User not authorized"}), 401
        db.session.delete(product)
        return product.to_dict(), 204
    
class WishlistItems(Resource):
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        products = [product.to_dict() for product in Wishlist.query.all() if product.user_id == current_user_id ]
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
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()

        # Fetch user data
        user_views = ViewingHistory.query.filter_by(user_id=current_user_id).order_by(ViewingHistory.viewed_at.desc()).all()
        user_searches = SearchQuery.query.filter_by(user_id=current_user_id).order_by(SearchQuery.searched_at.desc()).all()
        user_engagements = Engagement.query.filter_by(user_id=current_user_id).order_by(Engagement.engaged_at.desc()).all()

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


product_api.add_resource(UserSpecific,'/recommended_products',endpoint='recommended_products')
product_api.add_resource(WishlistItems,'/wishlists',endpoint='wishlists')            
product_api.add_resource(ProductResource,'/products',endpoint='products')
product_api.add_resource(ProductById,'/products/<int:product_id>',endpoint='product_by_id')

