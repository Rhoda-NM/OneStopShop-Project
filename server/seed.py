from config import db, app
from models import User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement, Rating, Discount, Category, Tag, ProductImage, BillingDetail
from datetime import datetime, timedelta
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
    users_data = [
        {'username': 'user1', 'email': 'user1@example.com', 'role': 'admin', 'password': 'adminpassword', 'full_name': 'User One', 'address': '123 Main St', 'city': 'City A', 'state': 'State A', 'postal_code': '12345', 'country': 'Country A', 'phone_number': '111-222-3333'},
        {'username': 'user2', 'email': 'user2@example.com', 'role': 'seller', 'password': 'adminpassword', 'full_name': 'User Two', 'address': '456 Market St', 'city': 'City B', 'state': 'State B', 'postal_code': '67890', 'country': 'Country B', 'phone_number': '444-555-6666'},
        {'username': 'admin', 'email': 'admin@example.com', 'role': 'seller', 'password': 'adminpassword', 'full_name': 'Admin User', 'address': '789 Broadway', 'city': 'City C', 'state': 'State C', 'postal_code': '54321', 'country': 'Country C', 'phone_number': '777-888-9999'}
    ]

    users = []
    for user_data in users_data:
        user = User(username=user_data['username'], email=user_data['email'], role=user_data['role'])
        user.set_password(user_data['password'])
        users.append(user)
        db.session.add(user)
        db.session.flush()  # Ensure the user ID is available for related data

        # Create billing details for each user
        billing_detail = BillingDetail(
            user_id=user.id,
            full_name=user_data['full_name'],
            address_line_1=user_data['address'],
            city=user_data['city'],
            state=user_data['state'],
            postal_code=user_data['postal_code'],
            country=user_data['country'],
            phone_number=user_data['phone_number'],
            email=user.email
        )
        db.session.add(billing_detail)

    db.session.commit()

    # Products API endpoint
    fetch_url = 'https://dummyjson.com/products?limit=200'
    response = requests.get(fetch_url)
    if response.status_code == 200:
        products_data = response.json().get('products', [])

        # Add products to db
        for product_data in products_data:
            category_name = product_data['category']
            if category_name not in ['groceries', 'vehicle', 'motorcycle']:
                # Get or create category
                category = Category.query.filter_by(name=category_name).first()
                if not category:
                    category = Category(name=category_name)
                    db.session.add(category)
                    db.session.flush()

                # Add product
                product = Product(
                    name=product_data['title'],
                    description=product_data['description'],
                    price=product_data['price'],
                    stock=product_data['stock'] or 20,
                    category_id=category.id,
                    image_url=product_data['thumbnail'],
                    sku=product_data['sku'],
                    user_id=random.choice(users).id
                )
                db.session.add(product)
                db.session.flush()

                # Add images
                for image_url in product_data['images']:
                    product_image = ProductImage(product_id=product.id, image_url=image_url)
                    db.session.add(product_image)

                # Add tags
                for tag_name in product_data.get('tags', []):
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name, category_id=category.id)
                        db.session.add(tag)
                    product.tags.append(tag)

                # Add ratings
                for _ in range(random.randint(1, 5)):
                    rating = Rating(
                        product_id=product.id,
                        user_id=random.choice(users).id,
                        rating=random.uniform(3, 5),
                        comment="Sample review comment"
                    )
                    db.session.add(rating)

                # Add discount
                if random.choice([True, False]):  # Randomly decide if a product should have a discount
                    discount = Discount(
                        product_id=product.id,
                        discount_percentage=random.uniform(5, 25),
                        start_date=datetime.now() - timedelta(days=random.randint(1, 10)),
                        end_date=datetime.now() + timedelta(days=random.randint(5, 15))
                    )
                    db.session.add(discount)

        db.session.commit()

        # Create Orders and OrderItems
        for _ in range(10):  # Create 10 random orders
            user = random.choice(users)
            products = Product.query.order_by(db.func.random()).limit(3).all()  # Get 3 random products
            order = Order(
                user_id=user.id,
                total_price=sum(product.price for product in products),
                status=random.choice(['completed', 'pending', 'shipped']),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(order)
            db.session.flush()

            for product in products:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=random.randint(1, 5),
                    price=product.price
                )
                db.session.add(order_item)

        db.session.commit()

        # Add Search Queries
        product_names = [product.name for product in Product.query.all()]  # Use product names as potential search terms
        categories = [category.name for category in Category.query.all()]  # Use category names as search terms

        for _ in range(30):  # Create 30 random search queries
            search_term = random.choice(product_names + categories)  # Mix product names and categories for search terms
            search_query = SearchQuery(
                user_id=random.choice(users).id,
                search_query=search_term,
                searched_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(search_query)

        db.session.commit()

        # Add Viewing History
        for _ in range(50):  # Create 50 random viewing history records
            viewing_history = ViewingHistory(
                user_id=random.choice(users).id,
                product_id=random.choice(Product.query.all()).id,
                viewed_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(viewing_history)

        db.session.commit()

        # Add Engagements
        for _ in range(40):  # Create 40 random engagements
            engagement = Engagement(
                user_id=random.choice(users).id,
                product_id=random.choice(Product.query.all()).id,
                watch_time=random.randint(10, 300),
                engaged_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(engagement)

        db.session.commit()

        print("Database seeded with products, orders, order items, billing details, viewing history, search queries, engagements, ratings, discounts, and more from DummyJSON!")
    else:
        print("Failed to fetch products from API")

# Run the seed function within the app context
if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_db()
