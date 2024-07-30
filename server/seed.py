from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Product, Order, OrderItem
from datetime import datetime
from app import app

with app.app_context():
    db.drop_all()
    print("Dropping all")
    db.create_all()

    # Create some users
    user1 = User(username='user1', email='user1@example.com', password_hash='password', role='user')
    user2 = User(username='user2', email='user2@example.com', password_hash='password', role='user')
    admin = User(username='admin', email='admin@example.com', password_hash='admin', role='admin')

    db.session.add_all([user1, user2, admin])
    db.session.commit()

    # Create some products
    product1 = Product(name='Laptop', category='Electronics', price=999.99, description='A high performance laptop', stock=10)
    product2 = Product(name='Smartphone', category='Electronics', price=699.99, description='A latest model smartphone', stock=20)
    product3 = Product(name='T-shirt', category='Clothes', price=19.99, description='A comfortable cotton t-shirt', stock=50)

    db.session.add_all([product1, product2, product3])
    db.session.commit()

    # Create some orders
    order1 = Order(user_id=user1.id, total_price=1019.98, status='Completed')
    order2 = Order(user_id=user2.id, total_price=19.99, status='Completed')

    db.session.add_all([order1, order2])
    db.session.commit()

    # Create some order items
    order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=1, price=999.99)
    order_item2 = OrderItem(order_id=order1.id, product_id=product3.id, quantity=1, price=19.99)
    order_item3 = OrderItem(order_id=order2.id, product_id=product3.id, quantity=1, price=19.99)

    db.session.add_all([order_item1, order_item2, order_item3])
    db.session.commit()

    print("Database seeded!")