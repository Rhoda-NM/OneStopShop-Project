# Import necessary modules
from config import db,app
from config import bcrypt
from models import User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement
from datetime import datetime
from app import create_app
from sqlalchemy.exc import IntegrityError

# Function to seed the database
def seed_db():
    # Drop and recreate the database
    db.drop_all()
    db.create_all()

    # Create some users
    user1 = User(username='user1', email='user1@example.com', role='customer')
    user1.set_password('password1')
    user2 = User(username='user2', email='user2@example.com', role='customer')
    user2.set_password('password2')
    user3 = User(username='admin', email='admin@example.com', role='admin')
    user3.set_password('adminpassword')

    # Add users to session
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    # Create some products
    product1 = Product(name='Product 1', category='Category A', image_url='http://example.com/product1.jpg', price=10.99, stock=100, user_id=user1.id)
    product2 = Product(name='Product 2', category='Category B', image_url='http://example.com/product2.jpg', price=20.99, stock=200, user_id=user1.id)
    product3 = Product(name='Product 3', category='Category A', image_url='http://example.com/product3.jpg', price=30.99, stock=300, user_id=user2.id)

    # Add products to session
    db.session.add_all([product1, product2, product3])
    db.session.commit()

    # Add products to wishlists
    user1.wishlists.append(product2)
    user2.wishlists.append(product3)

    # Commit the session to save the wishlist changes
    db.session.commit()

    # Create some orders
    order1 = Order(user_id=user1.id, total_price=31.98, status='Completed')
    order2 = Order(user_id=user2.id, total_price=20.99, status='Pending')

    # Add orders to session
    db.session.add_all([order1, order2])
    db.session.commit()

    # Create some order items
    order_item1 = OrderItem(order_id=order1.id, product_id=product1.id, quantity=1, price=10.99)
    order_item2 = OrderItem(order_id=order1.id, product_id=product2.id, quantity=1, price=20.99)
    order_item3 = OrderItem(order_id=order2.id, product_id=product2.id, quantity=1, price=20.99)

    # Add order items to session
    db.session.add_all([order_item1, order_item2, order_item3])
    db.session.commit()

    # Create some viewing history
    viewing1 = ViewingHistory(user_id=user1.id, product_id=product1.id)
    viewing2 = ViewingHistory(user_id=user2.id, product_id=product2.id)
    viewing3 = ViewingHistory(user_id=user1.id, product_id=product3.id)

    # Add viewing history to session
    db.session.add_all([viewing1, viewing2, viewing3])
    db.session.commit()

    # Create some search queries
    search1 = SearchQuery(user_id=user1.id, search_query='Product 1')
    search2 = SearchQuery(user_id=user2.id, search_query='Category B')
    search3 = SearchQuery(user_id=user3.id, search_query='Product 3')

    # Add search queries to session
    db.session.add_all([search1, search2, search3])
    db.session.commit()

    # Create some engagements
    engagement1 = Engagement(user_id=user1.id, product_id=product1.id, watch_time=120)
    engagement2 = Engagement(user_id=user2.id, product_id=product2.id, watch_time=240)
    engagement3 = Engagement(user_id=user1.id, product_id=product3.id, watch_time=360)

    # Add engagements to session
    db.session.add_all([engagement1, engagement2, engagement3])
    db.session.commit()

    print("Database seeded successfully!")

# Run the seed function within the app context
if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_db()
