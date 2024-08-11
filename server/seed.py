# Import necessary modules
from config import db, app
from config import bcrypt
from models import User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement, Rating, Discount
from datetime import datetime
from app import create_app
from sqlalchemy.exc import IntegrityError

# Function to seed the database
def seed_db():
    # Drop and recreate the database
    db.drop_all()
    db.create_all()

    # Create users
    users = []
    for i in range(1, 11):
        user = User(username=f'user{i}', email=f'user{i}@example.com', role='customer')
        user.set_password(f'password{i}')
        users.append(user)
    
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('adminpassword')
    users.append(admin)
    
    db.session.add_all(users)
    db.session.commit()

    # Create products
    products = [
        Product(name='Dog Food', category='Pet Supplies', image_url='https://example.com/dogfood.jpg', price=10.99, stock=100, user_id=users[0].id),
        Product(name='CANON EOS DSLR Camera', category='Electronics', image_url='https://example.com/canon-camera.jpg', price=360.00, stock=200, user_id=users[0].id),
        Product(name='ASUS FHD Gaming Laptop', category='Electronics', image_url='https://example.com/asus-laptop.jpg', price=700.00, stock=300, user_id=users[1].id),
        Product(name='Curology Product Set', category='Beauty', image_url='https://example.com/curology-set.jpg', price=500.00, stock=400, user_id=users[1].id),
        Product(name='Apple iPhone 13', category='Phones', image_url='https://example.com/iphone13.jpg', price=999.00, stock=150, user_id=users[2].id),
        Product(name='Samsung Galaxy S21', category='Phones', image_url='https://example.com/galaxy-s21.jpg', price=899.00, stock=250, user_id=users[2].id),
        Product(name='Sony WH-1000XM4 Headphones', category='Electronics', image_url='https://example.com/sony-headphones.jpg', price=350.00, stock=200, user_id=users[3].id),
        Product(name='Nintendo Switch', category='Gaming', image_url='https://example.com/switch.jpg', price=299.00, stock=100, user_id=users[3].id),
        Product(name='Instant Pot Duo', category='Home Appliances', image_url='https://example.com/instant-pot.jpg', price=89.99, stock=500, user_id=users[4].id),
        Product(name='Fitbit Versa 3', category='Wearables', image_url='https://example.com/fitbit.jpg', price=229.95, stock=250, user_id=users[4].id)
    ]

    db.session.add_all(products)
    db.session.commit()

    # Add products to wishlists
    users[0].wishlists.extend([products[1], products[3]])
    users[1].wishlists.append(products[2])
    users[2].wishlists.append(products[4])
    users[3].wishlists.append(products[5])

    db.session.commit()

    # Create orders
    orders = [
        Order(user_id=users[0].id, total_price=31.98, status='Completed'),
        Order(user_id=users[1].id, total_price=20.99, status='Pending'),
        Order(user_id=users[2].id, total_price=56.99, status='Shipped'),
        Order(user_id=users[3].id, total_price=120.00, status='Completed'),
        Order(user_id=users[4].id, total_price=450.00, status='Canceled')
    ]

    db.session.add_all(orders)
    db.session.commit()

    # Create order items
    order_items = [
        OrderItem(order_id=orders[0].id, product_id=products[0].id, quantity=1, price=10.99),
        OrderItem(order_id=orders[0].id, product_id=products[1].id, quantity=1, price=20.99),
        OrderItem(order_id=orders[1].id, product_id=products[2].id, quantity=1, price=20.99),
        OrderItem(order_id=orders[2].id, product_id=products[4].id, quantity=1, price=56.99),
        OrderItem(order_id=orders[3].id, product_id=products[5].id, quantity=2, price=60.00),
        OrderItem(order_id=orders[4].id, product_id=products[6].id, quantity=3, price=150.00)
    ]

    db.session.add_all(order_items)
    db.session.commit()

    # Create viewing history
    viewings = [
        ViewingHistory(user_id=users[0].id, product_id=products[0].id),
        ViewingHistory(user_id=users[1].id, product_id=products[1].id),
        ViewingHistory(user_id=users[0].id, product_id=products[2].id),
        ViewingHistory(user_id=users[2].id, product_id=products[3].id),
        ViewingHistory(user_id=users[3].id, product_id=products[4].id)
    ]

    db.session.add_all(viewings)
    db.session.commit()

    # Create search queries
    search_queries = [
        SearchQuery(user_id=users[0].id, search_query='Dog Food'),
        SearchQuery(user_id=users[1].id, search_query='Cameras'),
        SearchQuery(user_id=users[2].id, search_query='Gaming Laptop'),
        SearchQuery(user_id=users[3].id, search_query='Skin Care Set'),
        SearchQuery(user_id=users[4].id, search_query='iPhone 13')
    ]

    db.session.add_all(search_queries)
    db.session.commit()

    # Create engagements
    engagements = [
        Engagement(user_id=users[0].id, product_id=products[0].id, watch_time=120),
        Engagement(user_id=users[1].id, product_id=products[1].id, watch_time=240),
        Engagement(user_id=users[0].id, product_id=products[2].id, watch_time=360),
        Engagement(user_id=users[2].id, product_id=products[3].id, watch_time=180),
        Engagement(user_id=users[3].id, product_id=products[4].id, watch_time=300)
    ]

    db.session.add_all(engagements)
    db.session.commit()

    # Create ratings
    ratings = [
        Rating(product_id=products[0].id, user_id=users[0].id, rating=5, comment="Excellent product!"),
        Rating(product_id=products[1].id, user_id=users[1].id, rating=4, comment="Very good product!"),
        Rating(product_id=products[2].id, user_id=users[2].id, rating=3, comment="Average product."),
        Rating(product_id=products[3].id, user_id=users[3].id, rating=4, comment="Good value for money."),
        Rating(product_id=products[4].id, user_id=users[4].id, rating=2, comment="Not as expected.")
    ]

    db.session.add_all(ratings)
    db.session.commit()

    # Create discounts
    discounts = [
        Discount(product_id=products[0].id, discount_percentage=10.0, start_date=datetime(2024, 8, 1), end_date=datetime(2024, 8, 31)),
        Discount(product_id=products[1].id, discount_percentage=15.0, start_date=datetime(2024, 8, 10), end_date=datetime(2024, 8, 20)),
        Discount(product_id=products[2].id, discount_percentage=5.0, start_date=datetime(2024, 8, 15), end_date=datetime(2024, 8, 25)),
        Discount(product_id=products[3].id, discount_percentage=20.0, start_date=datetime(2024, 9, 1), end_date=datetime(2024, 9, 30)),
        Discount(product_id=products[4].id, discount_percentage=25.0, start_date=datetime(2024, 8, 5), end_date=datetime(2024, 8, 15))
    ]

    db.session.add_all(discounts)
    db.session.commit()

    print("Database seeded successfully!")

# Run the seed function within the app context
if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_db()
