from flask import Flask, make_response,jsonify,session,request, current_app, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from config import api, jwt, db, app

# Add your model imports
from models import Product, User
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
    user = User.query.get(user_id)
    return jsonify([product.serialize() for product in user.wishlists]), 200

#add to wishlist
@wishlist_bp.route('/wishlist', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    data = request.get_json()
    user_id = get_jwt_identity()
    product_id = data.get('product_id')

    user = User.query.get(user_id)
    product = Product.query.get(product_id)

    if product not in user.wishlists:
        user.wishlists.append(product)
        db.session.commit()
        return jsonify({'message': 'product added to wishlist'}), 201
    else:
        return jsonify({'message': 'Product already in wishlist'}),200

@wishlist_bp.route('/wishlist/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = get_jwt_identity()
    
    user = User.query.get(user_id)
    product = Product.query.get(product_id)
    
    if product in user.wishlists:
        user.wishlists.remove(product)
        db.session.commit()
        return jsonify({'message': 'Product removed from wishlist'}), 200
    else:
        return jsonify({'message': 'Product not in wishlist'}), 404 
"""
@wishlist_bp.route('/wishlist', methods=['POST'])



@wishlist_bp.route('/wishlist/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = get_jwt_identity()
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()

    if not wishlist_item:
        return jsonify({'error': 'Product not found in wishlist'}), 404

    db.session.delete(wishlist_item)
    db.session.commit()

    return '', 204


"""
