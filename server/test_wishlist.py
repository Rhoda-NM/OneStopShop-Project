import unittest
import json
from flask import Flask
from config import api, db, jwt
from models import User, Product  # Ensure these models are imported correctly
from wishlist import wishlist_bp  # Adjust the import to match your file structure

class WishlistTestCase(unittest.TestCase):
    def setUp(self):
        # Configure Flask for testing
        self.app = Flask(__name__)
        self.app.config.from_object('test_config.TestConfig')
        db.init_app(self.app)
        jwt.init_app(self.app)
        api.init_app(self.app)

        # Register the blueprint
        self.app.register_blueprint(wishlist_bp)

        # Create the database and the test client
        with self.app.app_context():
            db.create_all()

        self.client = self.app.test_client()

        # Create test data
        with self.app.app_context():
            self.user = User(username='testuser', email='test@example.com', role='user')
            self.user.set_password('testpassword')
            db.session.add(self.user)
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_view_wishlist(self):
        with self.app.app_context():
            # Mock the JWT token for the user
            token = self.client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'testpassword'
            }).get_json()['access_token']

            # Test the GET /wishlist route
            response = self.client.get('/api/wishlist', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json(), [])

    def test_add_to_wishlist(self):
        with self.app.app_context():
            # Mock the JWT token for the user
            token = self.client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'testpassword'
            }).get_json()['access_token']

            # Add a test product
            product = Product(name='Test Product')
            db.session.add(product)
            db.session.commit()

            # Test the POST /wishlist route
            response = self.client.post('/api/wishlist', headers={'Authorization': f'Bearer {token}'}, json={
                'product_id': product.id
            })
            self.assertEqual(response.status_code, 201)
            self.assertIn('product added to wishlist', response.get_json()['message'])

    def test_remove_from_wishlist(self):
        with self.app.app_context():
            # Mock the JWT token for the user
            token = self.client.post('/auth/login', json={
                'username': 'testuser',
                'password': 'testpassword'
            }).get_json()['access_token']

            # Add a test product
            product = Product(name='Test Product')
            db.session.add(product)
            db.session.commit()

            # Add product to wishlist
            self.user.wishlists.append(product)
            db.session.commit()

            # Test the DELETE /wishlist/<int:product_id> route
            response = self.client.delete(f'/api/wishlist/{product.id}', headers={'Authorization': f'Bearer {token}'})
            self.assertEqual(response.status_code, 200)
            self.assertIn('Product removed from wishlist', response.get_json()['message'])

if __name__ == '__main__':
    unittest.main()
