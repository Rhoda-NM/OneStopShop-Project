from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, Order, OrderItem
from datetime import datetime
from app import app
import bcrypt
from sqlalchemy.exc import IntegrityError

# Function to seed the database
def seed_db():
    # Ensure the tables are created
    with app.app_context():
        db.create_all()
        
        # Create sample users
        users = [
            {'username': 'john_doe', 'email': 'john@example.com', 'password': 'password', 'role': 'customer'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'password': 'password', 'role': 'customer'},
            {'username': 'admin', 'email': 'admin@example.com', 'password': 'adminpassword', 'role': 'admin'},
        ]
        
        # Add users to the session
        for user_data in users:
            try:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=user_data['password'],
                    role=user_data['role']
                )
                db.session.add(user)
            except IntegrityError:
                # Handle the case where the user already exists
                db.session.rollback()
        
        # Create sample products
        products = [
            # Electronics
            Product(name='Laptop', category='Electronics', image_url='http://example.com/laptop.jpg', price=999.99, description='High performance laptop', stock=50),
            Product(name='Smart TV', category='Electronics', image_url='http://example.com/smart_tv.jpg', price=599.99, description='55 inch 4K Smart TV', stock=30),
            Product(name='Bluetooth Speaker', category='Electronics', image_url='http://example.com/bluetooth_speaker.jpg', price=49.99, description='Portable Bluetooth speaker', stock=100),
            
            # Mobiles
            Product(name='Smartphone A', category='Mobiles', image_url='http://example.com/smartphone_a.jpg', price=699.99, description='Latest model smartphone', stock=200),
            Product(name='Smartphone B', category='Mobiles', image_url='http://example.com/smartphone_b.jpg', price=399.99, description='Affordable smartphone with great features', stock=150),
            
            # Clothes
            Product(name='Men\'s T-Shirt', category='Clothes', image_url='http://example.com/mens_tshirt.jpg', price=19.99, description='Cotton t-shirt', stock=300),
            Product(name='Women\'s Dress', category='Clothes', image_url='http://example.com/womens_dress.jpg', price=49.99, description='Stylish summer dress', stock=200),
            Product(name='Men\'s Jeans', category='Clothes', image_url='http://example.com/mens_jeans.jpg', price=39.99, description='Comfortable jeans', stock=150),
            
            # Books
            Product(name='Book A', category='Books', image_url='http://example.com/book_a.jpg', price=14.99, description='Bestselling novel', stock=500),
            Product(name='Book B', category='Books', image_url='http://example.com/book_b.jpg', price=9.99, description='Inspirational self-help book', stock=400),
        ]
        
        # Add products to the session
        for product in products:
            db.session.add(product)

        # Commit the changes to the database
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

        # Create sample orders
        orders = [
            Order(user_id=1, total_price=59.97, status='completed'),
            Order(user_id=2, total_price=29.99, status='pending'),
        ]
        
        # Add orders to the session
        for order in orders:
            db.session.add(order)
        
        # Create sample order items
        order_items = [
            OrderItem(order_id=1, product_id=1, quantity=1, price=999.99),
            OrderItem(order_id=1, product_id=2, quantity=1, price=599.99),
            OrderItem(order_id=1, product_id=3, quantity=1, price=49.99),
            OrderItem(order_id=2, product_id=4, quantity=1, price=699.99),
            OrderItem(order_id=2, product_id=5, quantity=1, price=399.99),
        ]
        
        # Add order items to the session
        for order_item in order_items:
            db.session.add(order_item)

        # Commit the changes to the database
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

# Run the seed function within the app context
if __name__ == '__main__':
    with app.app_context():
        seed_db()
