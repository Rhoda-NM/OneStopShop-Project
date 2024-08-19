import os
import tempfile
import unittest
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from app import create_app
from flask import session
from config import app, db, bcrypt
from datetime import datetime
from models import User, Product, Order, OrderItem, ViewingHistory, SearchQuery, Engagement,Rating,Discount
from seed import seed_db


class TestCaseWithAppContext(unittest.TestCase):
    def setUp(self):
        # Set up test app and database
        self.app = create_app('testing')
        
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()
        self.populate_db()
        
        self.test_client = self.app.test_client()

        # Initialize JWT
        self.jwt = JWTManager(self.app)
        
        #Define and register the user lookup callback
        @self.jwt.user_lookup_loader
        def user_lookup_callback(_jwt_header, jwt_data):
            identity = jwt_data["sub"]
            return User.query.filter_by(id=identity).one_or_none() 

    def tearDown(self):
        # Clean up the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        

    def populate_db(self):
        # Create sample users
        seed_db()

    def get_access_token(self, user_id):
        return create_access_token(identity=user_id)

    def get_refresh_token(self, user_id):
        return create_refresh_token(identity=user_id)
    

class TestUserModel(TestCaseWithAppContext):
    def test_create_user(self):
        user = User(username="testuser", email="testuser@example.com", role="buyer")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        self.assertIsNotNone(user.id)
        self.assertTrue(user.authenticate("password123"))

    def test_unique_username(self):
        user1 = User(username="uniqueuser", email="user1@example.com", role="seller")
        user2 = User(username="uniqueuser", email="user2@example.com", role="buyer")
        db.session.add(user1)
        db.session.commit()

        db.session.add(user2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_validate_user_fields(self):
        with self.assertRaises(ValueError):
            User(username="", email="invaliduser@example.com", role="buyer")

        with self.assertRaises(ValueError):
            User(username="validuser", email="", role="buyer")


class TestProductModel(TestCaseWithAppContext):
    def test_create_product(self):
        user = User(username="seller", email="seller@example.com", role="seller")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Test Product",
            category="Electronics",
            image_url="http://example.com/product.jpg",
            price=100.0,
            stock=10,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        self.assertIsNotNone(product.id)
        self.assertEqual(product.seller, user)

    def test_validate_product_fields(self):
        user = User(username="seller2", email="seller2@example.com", role="seller")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        with self.assertRaises(ValueError):
            Product(name="", category="Electronics", image_url="http://example.com/product.jpg", price=100.0, stock=10, seller=user)

        with self.assertRaises(ValueError):
            Product(name="Valid Name", category="", image_url="http://example.com/product.jpg", price=100.0, stock=10, seller=user)


class TestOrderModel(TestCaseWithAppContext):
    def test_create_order(self):
        user = User(username="buyer", email="buyer@example.com", role="buyer")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        order = Order(user_id=user.id, total_price=200.0, status="Pending")
        db.session.add(order)
        db.session.commit()

        self.assertIsNotNone(order.id)
        self.assertEqual(order.user, user)

    def test_order_total_price(self):
        user = User(username="buyer2", email="buyer2@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        order = Order(user_id=user.id, total_price=-50.0, status="Pending")
        db.session.add(order)
        with self.assertRaises(ValueError):
            db.session.commit()


class TestOrderItemModel(TestCaseWithAppContext):
    def test_create_order_item(self):
        user = User(username="buyer3", email="buyer3@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Order Item Product",
            category="Books",
            image_url="http://example.com/book.jpg",
            price=30.0,
            stock=50,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        order = Order(user_id=user.id, total_price=60.0, status="Pending")
        db.session.add(order)
        db.session.commit()

        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=2, price=30.0)
        db.session.add(order_item)
        db.session.commit()

        self.assertIsNotNone(order_item.id)
        self.assertEqual(order_item.order, order)
        self.assertEqual(order_item.product, product)

    def test_validate_order_item_fields(self):
        user = User(username="buyer4", email="buyer4@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Invalid Order Item Product",
            category="Books",
            image_url="http://example.com/book.jpg",
            price=30.0,
            stock=50,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        order = Order(user_id=user.id, total_price=60.0, status="Pending")
        db.session.add(order)
        db.session.commit()

        with self.assertRaises(ValueError):
            OrderItem(order_id=order.id, product_id=product.id, quantity=0, price=30.0)

        with self.assertRaises(ValueError):
            OrderItem(order_id=order.id, product_id=product.id, quantity=2, price=-30.0)


class TestWishlistModel(TestCaseWithAppContext):
    def test_add_to_wishlist(self):
        user = User(username="wishlistuser", email="wishlistuser@example.com", role="buyer")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Wishlist Product",
            category="Gadgets",
            image_url="http://example.com/gadget.jpg",
            price=150.0,
            stock=5,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        user.wishlists.append(product)
        db.session.commit()

        self.assertIn(product, user.wishlists)
        self.assertIn(user, product.wishlisted_by_users)


class TestViewingHistoryModel(TestCaseWithAppContext):
    def test_create_viewing_history(self):
        user = User(username="viewer", email="viewer@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Viewed Product",
            category="Music",
            image_url="http://example.com/music.jpg",
            price=20.0,
            stock=100,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        viewing_history = ViewingHistory(user_id=user.id, product_id=product.id)
        db.session.add(viewing_history)
        db.session.commit()

        self.assertIsNotNone(viewing_history.id)
        self.assertEqual(viewing_history.user, user)
        self.assertEqual(viewing_history.product, product)


class TestSearchQueryModel(TestCaseWithAppContext):
    def test_create_search_query(self):
        user = User(username="searcher", email="searcher@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        search_query = SearchQuery(user_id=user.id, search_query="Laptop")
        db.session.add(search_query)
        db.session.commit()

        self.assertIsNotNone(search_query.id)
        self.assertEqual(search_query.user, user)
        self.assertEqual(search_query.search_query, "Laptop")


class TestEngagementModel(TestCaseWithAppContext):
    def test_create_engagement(self):
        user = User(username="engageduser", email="engageduser@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Engaged Product",
            category="Video",
            image_url="http://example.com/video.jpg",
            price=10.0,
            stock=50,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        engagement = Engagement(user_id=user.id, product_id=product.id, watch_time=120)
        db.session.add(engagement)
        db.session.commit()

        self.assertIsNotNone(engagement.id)
        self.assertEqual(engagement.user, user)
        self.assertEqual(engagement.product, product)


class TestRatingModel(TestCaseWithAppContext):
    def test_create_rating(self):
        user = User(username="ratinguser", email="ratinguser@example.com", role="buyer")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Rated Product",
            category="Books",
            image_url="http://example.com/book.jpg",
            price=25.0,
            stock=10,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        rating = Rating(product_id=product.id, user_id=user.id, rating=5, comment="Excellent product!")
        db.session.add(rating)
        db.session.commit()

        self.assertIsNotNone(rating.id)
        self.assertEqual(rating.rating, 5)
        self.assertEqual(rating.comment, "Excellent product!")


class TestDiscountModel(TestCaseWithAppContext):
    def test_create_discount(self):
        user = User(username="discountuser", email="discountuser@example.com", role="seller")
        db.session.add(user)
        db.session.commit()

        product = Product(
            name="Discounted Product",
            category="Clothing",
            image_url="http://example.com/clothing.jpg",
            price=50.0,
            stock=20,
            seller=user
        )
        db.session.add(product)
        db.session.commit()

        discount = Discount(
            product_id=product.id,
            discount_percentage=20.0,
            start_date=datetime(2024, 8, 1),
            end_date=datetime(2024, 8, 10)
        )
        db.session.add(discount)
        db.session.commit()

        self.assertIsNotNone(discount.id)
        self.assertEqual(discount.product, product)
        self.assertEqual(discount.discount_percentage, 20.0)

