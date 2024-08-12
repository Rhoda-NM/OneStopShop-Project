from flask import Flask, make_response, jsonify, session, request, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import api, jwt, db, app
from models import Product, User,Category, Tag, ViewingHistory, SearchQuery, Engagement,wishlist_table, Rating, Discount
from authenticate import allow

product_bp = Blueprint('product_bp', __name__, url_prefix='/api')

# Initialize JWT
def init_jwt(app):
    jwt.init_app(app)

# get products
@product_bp.route('/products', methods=['GET'])
def get_products():
    limit = request.args.get('limit',default=None,type=int)
    if limit is None:
        products = [product.serialize() for product in Product.query.all()]
    elif limit is not None:
        products = [product.serialize() for product in Product.query.limit(limit).all()]
    
    return jsonify(products), 200

# Route to fetch products by category name
@product_bp.route('/products/category/<string:category_name>', methods=['GET'])
def get_products_by_category_name(category_name):
    # Query the database to find the category by name
    category = Category.query.filter_by(name=category_name).first()
    
    if not category:
        abort(404, description="Category not found")
    
    # Fetch all products belonging to this category
    products = Product.query.filter_by(category_id=category.id).all()
    
    # Serialize the list of products
    serialized_products = [product.serialize() for product in products]
    
    return jsonify(serialized_products), 200


#Add a product
@product_bp.route('/products', methods=['POST'])
@jwt_required()
@allow('admin', 'seller')
def create_product():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    product = Product(
        name=data['name'], 
        category=data['category'],
        image_url=data['image_url'],   
        price=data['price'], 
        description=data['description'], 
        stock=data['stock'], 
        user_id=current_user_id
    )
    db.session.add(product)
    db.session.commit()
    return jsonify(product.serialize()), 201

# get a product
@product_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    product_data = product.serialize()

    # Fetch ratings
    ratings = Rating.query.filter_by(product_id=product_id).all()
    product_data['ratings'] = [rating.serialize() for rating in ratings]

    # Fetch discounts
    discounts = Discount.query.filter_by(product_id=product_id).all()
    product_data['discounts'] = [discount.serialize() for discount in discounts]

    return jsonify(product_data), 200

# patch a product
@product_bp.route('/products/<int:product_id>', methods=['PATCH'])
@jwt_required()
@allow('admin','seller')
def update_product(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.filter(User.id == current_user_id).first()
    role = user.role
    product = Product.query.filter_by(id=product_id).first()
    data = request.get_json()
    if not product:
        return jsonify({"message": "Product not found"}), 404
    
    if role == 'seller':
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

# delete a product
@product_bp.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
@allow('admin','seller')
def delete_product(product_id):
    current_user_id = get_jwt_identity()
    user = User.query.filter(User.id == current_user_id).first()
    role = user.role
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found"}), 404
    if role == 'seller':
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

# products by seller
@product_bp.route('/user_products', methods=['GET'])
@jwt_required()
def get_user_products():
    current_user_id = get_jwt_identity()
    products = Product.query.filter_by(user_id=current_user_id).all()
    return jsonify([product.to_dict() for product in products]), 200


# Ratings
@product_bp.route('/ratings', methods=['GET'])
def get_ratings():
    ratings = [rating.serialize() for rating in Rating.query.all()]
    return jsonify(ratings), 200

@product_bp.route('/ratings/<int:id>',methods=['GET'])
def get_rating(id):
    ratings = [rating.serialize() for rating in Rating.query.filter(Rating.product_id == id).all()]
    return jsonify(ratings), 200
@product_bp.route('/ratings', methods=['POST'])
def create_rating():
    data = request.get_json()
    new_rating = Rating(
        product_id=data.get('product_id'),
        user_id=data.get('user_id'),
        rating=data.get('rating'),
        comment=data.get('comment')
    )
    db.session.add(new_rating)
    db.session.commit()
    return jsonify(new_rating.serialize()), 201

@product_bp.route('/ratings/<int:id>', methods=['DELETE'])
def delete_rating(id):
    rating = Rating.query.get_or_404(id)
    db.session.delete(rating)
    db.session.commit()
    return jsonify({'message': 'Rating deleted successfully'}), 200

@product_bp.route('/ratings/<int:id>', methods=['PATCH'])
def update_rating(id):
    data = request.get_json()
    rating = Rating.query.get_or_404(id)
    if 'rating' in data:
        rating.rating = data['rating']
    if 'comment' in data:
        rating.comment = data['comment']
    db.session.commit()
    return jsonify(rating.serialize()), 200

# Discounts
@product_bp.route('/discounts', methods=['GET'])
def get_discounts():
    discounts = [discount.serialize() for discount in Discount.query.all()]
    return jsonify(discounts), 200

@product_bp.route('discounts/<int:id>',methods=['GET'])
def get_discount(id):
    discount =Discount.query.filter(Discount.product_id == id).first()
    if not discount:
        return jsonify({"message": "Discount not found"}), 404
    return jsonify(discount.serialize()), 200


@product_bp.route('/discounts', methods=['POST'])
def create_discount():
    data = request.get_json()
    new_discount = Discount(
        product_id=data.get('product_id'),
        discount_percentage=data.get('discount_percentage'),
        start_date=data.get('start_date'),
        end_date=data.get('end_date')
    )
    db.session.add(new_discount)
    db.session.commit()
    return jsonify(new_discount.serialize()), 201

@product_bp.route('/discounts/<int:id>', methods=['DELETE'])
def delete_discount(id):
    discount = Discount.query.get_or_404(id)
    db.session.delete(discount)
    db.session.commit()
    return jsonify({'message': 'Discount deleted successfully'}), 200

@product_bp.route('/discounts/<int:id>', methods=['PATCH'])
def update_discount(id):
    data = request.get_json()
    discount = Discount.query.get_or_404(id)
    if 'discount_percentage' in data:
        discount.discount_percentage = data['discount_percentage']
    if 'start_date' in data:
        discount.start_date = data['start_date']
    if 'end_date' in data:
        discount.end_date = data['end_date']
    db.session.commit()
    return jsonify(discount.serialize()), 200