from datetime import datetime
from app import app
from models import db, User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement, Wishlist

with app.app_context():
    db.drop_all()
    # Create all tables
    db.create_all()

    # Add users
    user1 = User(username='johndoe', email='johndoe@example.com', password_hash='password123', role='customer')
    user2 = User(username='janedoe', email='janedoe@example.com', password_hash='password123', role='admin')

    db.session.add_all([user1, user2])
    db.session.commit()

    # Add products
    product1 = Product(name='Laptop', category='Electronics', price=999.99, description='High performance laptop', stock=10)
    product2 = Product(name='Headphones', category='Electronics', price=199.99, description='Noise cancelling headphones', stock=50)
    product3 = Product(name='Coffee Mug', category='Home & Kitchen', price=12.99, description='Ceramic coffee mug', stock=100)

    db.session.add_all([product1, product2, product3])
    db.session.commit()

    # Add orders
    order1 = Order(user_id=user1.id, total_price=1199.98, status='completed')
    order2 = Order(user_id=user2.id, total_price=12.99, status='pending')

    db.session.add_all([order1, order2])
    db.session.commit()

    # Add order items
    order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=1, price=999.99)
    order_item2 = OrderItem(order_id=order1.id, product_id=product2.id, quantity=1, price=199.99)
    order_item3 = OrderItem(order_id=order2.id, product_id=product3.id, quantity=1, price=12.99)

    db.session.add_all([order_item1, order_item2, order_item3])
    db.session.commit()

    # Add viewing history
    view_history1 = ViewingHistory(user_id=user1.id, product_id=product1.id, viewed_at=datetime.now())
    view_history2 = ViewingHistory(user_id=user2.id, product_id=product2.id, viewed_at=datetime.now())

    db.session.add_all([view_history1, view_history2])
    db.session.commit()

    # Add search queries
    search_query1 = SearchQuery(user_id=user1.id, query='best laptops 2024', searched_at=datetime.now())
    search_query2 = SearchQuery(user_id=user2.id, query='noise cancelling headphones', searched_at=datetime.now())

    db.session.add_all([search_query1, search_query2])
    db.session.commit()

    # Add engagements
    engagement1 = Engagement(user_id=user1.id, product_id=product1.id, watch_time=300, engaged_at=datetime.now())
    engagement2 = Engagement(user_id=user2.id, product_id=product2.id, watch_time=150, engaged_at=datetime.datetime.now())

    db.session.add_all([engagement1, engagement2])
    db.session.commit()

    # Add wishlist items
    wishlist1 = Wishlist(user_id=user1.id, product_id=product3.id)
    wishlist2 = Wishlist(user_id=user2.id, product_id=product1.id)

    db.session.add_all([wishlist1, wishlist2])
    db.session.commit()

    print("Sample data added successfully!")
