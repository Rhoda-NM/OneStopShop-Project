from flask import Flask, make_response, jsonify, session, request, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import api, jwt, db, app
from models import Product, User, ViewingHistory, SearchQuery, Engagement
from authenticate import allow

product_bp = Blueprint('product_bp', __name__, url_prefix='/api')

# Initialize JWT
def init_jwt(app):
    jwt.init_app(app)

# Products
@product_bp.route('/products', methods=['GET'])
def get_products():
    products = [product.serialize() for product in Product.query.all()]
    return jsonify(products), 200

@product_bp.route('/products', methods=['POST'])
@jwt_required()
@allow('admin')
def create_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product = Product(
        name=data['name'], 
        category=data['category'], 
        price=data['price'], 
        description=data['description'], 
        stock=data['stock'], 
        user_id=current_user_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.serialize()), 201

@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404
    return jsonify(product.serialize()), 200

@product_bp.route('/products/<int:product_id>', methods=['PATCH'])
@jwt_required()
def update_product(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.filter_by(id=product_id).first()
    data = request.get_json()
    if not product:
        return jsonify({"message": "Product not found"}), 404
    if product.user_id != current_user_id:
        return jsonify({"message": "User not authorized"}), 401
    
    for key, value in data.items():
        if key != 'id' and hasattr(product, key):
            setattr(product, key, value)
    try:
        db.session.commit()
        return jsonify(product.serialize()), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404
    if product.user_id != current_user_id:
        return jsonify({"message": "User not authorized"}), 401
    db.session.delete(product)
    db.session.commit()
    return '', 204


# Recommended Products
@product_bp.route('/recommended_products', methods=['GET'])
@jwt_required()
def get_recommended_products():
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
    top_product_ids = sorted(product_scores, key=product_scores.get, reverse=True)
    top_products = Product.query.filter(Product.id.in_(top_product_ids)).all()

    return jsonify({'recommended_products': [product.serialize() for product in top_products]}), 200

