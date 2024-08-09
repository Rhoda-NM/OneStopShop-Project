# Import necessary modules
from config import db, app
from models import User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement, Rating, Discount, Category, Tag, ProductImage
from datetime import datetime
from app import create_app
import requests
import random
from sqlalchemy.exc import IntegrityError

# Function to seed the database
def seed_db():
    # Drop and recreate the database
    db.drop_all()
    db.create_all()

    # Create some users
    user1 = User(username='user1', email='user1@example.com', role='admin')
    user1.set_password('adminpassword')
    user2 = User(username='user2', email='user2@example.com', role='admin')
    user2.set_password('adminpassword')
    user3 = User(username='admin', email='admin@example.com', role='admin')
    user3.set_password('adminpassword')

    # Add users to session
    db.session.add_all([user1, user2, user3])
    db.session.commit()

    #Products API endpoint
    fetch_url = 'https://dummyjson.com/products?limit=120'
    response = requests.get(fetch_url)
    if response.status_code == 200:
        products = response.json().get('products', [])
        users = User.query.all()

        #Add products to db
        for product_data in products:
            # Add category
            category_name = product_data['category']
            if category_name != 'groceries' and category_name != 'vehicle' and category_name != 'motorcycle':
                category = Category.query.filter_by(name=product_data['category']).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()
                
                stock = product_data['stock']
                if not stock or stock == 0:
                    stock = 20
                
                # Add category
                product = Product(
                    name = product_data['title'],
                    description = product_data['description'],
                    price = product_data['price'],
                    stock=stock,
                    category_id = category.id,
                    image_url=product_data['thumbnail'],
                    sku = product_data['sku'],  # Main image or thumbnail
                    user_id=random.choice(users).id
                )
                db.session.add(product)
                #category.append(product)
                db.session.flush()

                # Add images
                for image_url in product_data['images']:
                    product_image = ProductImage(
                        product_id=product.id,
                        image_url=image_url
                    )
                    db.session.add(product_image)
                

                # Add tags
                for tag_name in product_data.get('tags', []):
                    if tag_name != product_data['category']:
                        tag = Tag.query.filter_by(name=tag_name).first()
                        if not tag:
                            tag = Tag(name=tag_name, category_id=category.id)
                            db.session.add(tag)
                        product.tags.append(tag)
                

                # Add product ratings and reviews
                for review in product_data.get('reviews', []):
                    rating = Rating(
                        product_id=product.id,
                        user_id=random.choice(users).id,  # Assign to a random user
                        rating=review['rating'],
                        comment=review.get('comment')
                    )
                    db.session.add(rating)

        db.session.commit()
        print("Database seeded with products, images, tags, ratings, and reviews from DummyJSON!")
    else:
        print("Failed to fetch products from API")

    """Create some products
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

    # Create some ratings
    rating1 = Rating(product_id=product1.id, user_id=user1.id, rating=5, comment="Excellent product!")
    rating2 = Rating(product_id=product2.id, user_id=user2.id, rating=4, comment="Very good product!")
    rating3 = Rating(product_id=product3.id, user_id=user1.id, rating=3, comment="Average product.")

    # Add ratings to session
    db.session.add_all([rating1, rating2, rating3])
    db.session.commit()

    # Create some discounts
    discount1 = Discount(
        product_id=product1.id,
        discount_percentage=10.0,
        start_date=datetime(2024, 8, 1),
        end_date=datetime(2024, 8, 31)
    )
    discount2 = Discount(
        product_id=product2.id,
        discount_percentage=15.0,
        start_date=datetime(2024, 8, 10),
        end_date=datetime(2024, 8, 20)
    )
    discount3 = Discount(
        product_id=product3.id,
        discount_percentage=5.0,
        start_date=datetime(2024, 8, 15),
        end_date=datetime(2024, 8, 25)
    )

    # Add discounts to session
    db.session.add_all([discount1, discount2, discount3])
    db.session.commit()

    print("Database seeded successfully!")"""

# Run the seed function within the app context
if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_db()
