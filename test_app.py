import os
import tempfile
import unittest
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from app import create_app
from flask import session
from config import app, db, bcrypt
from models import Product, User
from seed import seed_db

class TestCaseWithAppContext(unittest.TestCase):
    def setUp(self):
        # Set up test app and database
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['JWT_SECRET_KEY'] = 'test_secret_key'
        
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        self.populate_db()
        
        self.test_client = self.app.test_client()

        # Initialize JWT
        self.jwt = JWTManager(self.app)
        
        # Define and register the user lookup callback
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

    def test_get_all_products(self):
        response = self.test_client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.get_json()), 3)

    def test_create_product(self):
        user = User.query.filter(User.email == "admin@example.com").first()
        token = self.get_access_token(user.id)
        data = {
            'name': 'Product2',
            'category': 'Category2',
            'image_url': 'http://example.com/image2.jpg',
            'price': 150.0,
            'description': 'Description2',
            'stock': 20
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.post('/api/products', json=data, headers=headers)
        self.assertEqual(response.status_code, 201)
        product = response.get_json()
        self.assertEqual(product['name'], 'Product2')
        self.assertEqual(product['category'], 'Category2')

    def test_get_product_by_id(self):
        response = self.test_client.get('/api/products/1')
        self.assertEqual(response.status_code, 200)
        product = response.get_json()
        self.assertEqual(product['name'], 'Product 1')

    def test_update_product(self):
        user = User.query.filter(User.email == "admin@example.com").first()
        token = self.get_access_token(user.id)
        data = {
            'name': 'UpdatedProduct2',
            'price': 120.0
        }
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.patch('/api/products/2', json=data, headers=headers)
        self.assertEqual(response.status_code, 200)
        product = response.get_json()
        self.assertEqual(product['name'], 'UpdatedProduct2')
        self.assertEqual(product['price'], 120.0)

    def test_delete_product(self):
        user = User.query.filter(User.email == "admin@example.com").first()
        token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.delete('/api/products/1', headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_get_wishlist_items(self):
        user = User.query.filter(User.email == "user1@example.com").first()
        token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.get('/api/wishlist', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_add_to_wishlist(self):
        user = User.query.filter(User.email == "user1@example.com").first()
        token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {token}'}
        response = self.test_client.post('/api/wishlist', json={'product_id': 1}, headers=headers)
        self.assertEqual(response.status_code, 201)
        wishlist = response.get_json()
        self.assertEqual(wishlist['message'], 'Product added to wishlist')

if __name__ == '__main__':
    unittest.main()
