from flask import Flask, make_response,jsonify,session,request, current_app, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from config import api, jwt, db, app

# Add your model imports
from models import Product, User, Tag
from authenticate import allow

wishlist_bp = Blueprint('wishlist_bp',__name__, url_prefix='/api')
wishlist_api = Api(wishlist_bp)

def init_jwt(app):
    jwt.init_app(app)

#view wishlist
@wishlist_bp.route('/wishlist', methods=['GET'])
@jwt_required()
def view_wishlist():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id) 
    return jsonify([product.serialize() for product in user.wishlists]), 200

#add to wishlist
@wishlist_bp.route('/wishlist', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        product_id = data.get('product_id')
        print("User ID:", user_id, "Product ID:", product_id)

        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"message": "User not found"}), 404

        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        if product not in user.wishlists:
            user.wishlists.append(product)
            db.session.commit()
            return jsonify({'message': 'Product added to wishlist'}), 201
        else:
            return jsonify({'message': 'Product already in wishlist'}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 422 

#remove from wishlist
@wishlist_bp.route('/wishlist/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = get_jwt_identity()
    
    user = db.session.get(User, user_id) 
    product = db.session.get(Product, product_id) 
    
    if product in user.wishlists:
        user.wishlists.remove(product)
        db.session.commit()
        return jsonify({'message': 'Product removed from wishlist'}), 200
    else:
        return jsonify({'message': 'Product not in wishlist'}), 404 

@wishlist_bp.route('/wishlist/recommendations', methods=['GET'])
@jwt_required()
def recommend_products():
    user = User.query.get(current_user.id)
    wishlist_product_ids = [product.id for product in user.wishlists]
    wishlist_tags = {tag.id for product in user.wishlists for tag in product.tags}

    # Get products that share the same tags and are not in the user's wishlist
    recommended_products = Product.query.filter(
        ~Product.id.in_(wishlist_product_ids),
        Product.tags.any(Tag.id.in_(wishlist_tags))
    ).limit(10).all()
    
    return jsonify([product.serialize() for product in recommended_products])
