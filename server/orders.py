from flask import Flask, make_response,jsonify,session,request, current_app, Blueprint
from flask_restful import Resource, Api, reqparse
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from config import api, jwt, db, app

# Add your model imports
from models import Product, Order, OrderItem
from authenticate import allow

order_bp = Blueprint('order_bp',__name__, url_prefix='/api')
order_api = Api(order_bp)

def init_jwt(app):
    jwt.init_app(app)

#view items in cart
@order_bp.route('/cart', methods=['GET'])
@jwt_required()
def view_cart():
    user_id = get_jwt_identity()
    order = Order.query.filter_by(user_id=user_id, status='cart').first()
    if not order:
        return jsonify({'message': 'No items in the cart'}), 200
    return jsonify(order.serialize()), 200

#vremove items from cart
@order_bp.route('/cart/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(user_id=user_id, status='cart').first()
    if not order:
        return jsonify({'error': 'No active cart found'}), 400

    order_item = OrderItem.query.filter_by(order_id=order.id, product_id=product_id).first()
    if not order_item:
        return jsonify({'error': 'Item not found in cart'}), 404

    order.total_price -= order_item.price * order_item.quantity  # Adjust the total price
    db.session.delete(order_item)
    db.session.commit()

    # Check if the cart is empty
    if not order.order_items:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'message': 'Cart is now empty'}), 200
    
    return jsonify(order.serialize()), 200

#Adding items to cart
@order_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    # Check if the user already has an active cart
    order = Order.query.filter_by(user_id=user_id, status='cart').first()
    if not order:
        # Create a new cart
        order = Order(user_id=user_id, status='cart', total_price=0)
        db.session.add(order)
        db.session.commit()
    
    # Add items to the cart
    for item_data in data['order_items']:
        product = Product.query.get(item_data['product_id'])
        if product:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data['quantity'],
                price=product.price
            )
            db.session.add(order_item)
            order.total_price += product.price * item_data['quantity']
    
    db.session.commit()
    
    return jsonify(order.serialize()), 201

@order_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    user_id = get_jwt_identity()
    order = Order.query.filter_by(user_id=user_id, status='cart').first()
    if not order:
        return jsonify({'error': 'No active cart found'}), 400

    # Update the order status to 'pending'
    order.status = 'pending'
    db.session.commit()
    
    return jsonify(order.serialize()), 200

@order_bp.route('/complete_order/<int:order_id>', methods=['POST'])
@jwt_required()
def complete_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.get_or_404(order_id)
    if order.user_id != user_id or order.status != 'pending':
        return jsonify({'error': 'Order cannot be completed'}), 400

    # process payment    
    # If payment is successful, update the order status to 'completed'
    order.status = 'completed'
    db.session.commit()
    
    return jsonify(order.serialize()), 200

#View all previous orders by a customer/user
@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    current_user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=current_user_id, status='cart').all()
    return jsonify([order.serialize() for order in orders])


