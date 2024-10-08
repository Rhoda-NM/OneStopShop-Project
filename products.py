from flask import Flask, abort, make_response, jsonify, session, request, current_app, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import api, jwt, db, app
from models import Product, User,Category, Tag, ViewingHistory, SearchQuery, Engagement,wishlist_table, Rating, Discount
from authenticate import allow
from Search import search_products

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
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Get recent search queries, views, and engagements
    search_queries = SearchQuery.query.filter_by(user_id=user_id).order_by(SearchQuery.searched_at.desc()).limit(10).all()
    viewing_history = ViewingHistory.query.filter_by(user_id=user_id).order_by(ViewingHistory.viewed_at.desc()).limit(10).all()
    engagements = Engagement.query.filter_by(user_id=user_id).order_by(Engagement.engaged_at.desc()).limit(10).all()

    # Gather product IDs from these interactions
    product_ids = set()
    for sq in search_queries:
        products = Product.query.filter(Product.name.ilike(f"%{sq.search_query}%")).all()
        product_ids.update([p.id for p in products])

    product_ids.update([vh.product_id for vh in viewing_history])
    product_ids.update([e.product_id for e in engagements])

    # Fetch the products based on these IDs
    recommended_products = Product.query.filter(Product.id.in_(list(product_ids))).limit(4).all()

    # If not enough products, fetch some random ones to fill the gap
    if len(recommended_products) < 4:
        additional_products = Product.query.filter(Product.id.notin_(product_ids)).order_by(db.func.random()).limit(4 - len(recommended_products)).all()
        recommended_products.extend(additional_products)

    return jsonify([product.serialize() for product in recommended_products])


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

@product_bp.route('/search_details', methods=['GET'])
def search_product_details():
    query = request.args.get('query')
    product_data=[product.serialize() for product in Product.query.all()]
    results = search_products(query,product_data)
    return jsonify(results),200
