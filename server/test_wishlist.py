import unittest
from flask_jwt_extended import create_access_token, JWTManager
from app import create_app
from models import db, User, Product

class WishlistTestCase(unittest.TestCase):

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
        
        self.client = self.app.test_client()

        # Initialize JWT
        self.jwt = JWTManager(self.app)

    def tearDown(self):
        # Clean up the database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def populate_db(self):
        # Create sample users
        user1 = User(username='john_doe', email='john@example.com', role='customer')
        user1.set_password('password')
        user2 = User(username='jane_smith', email='jane@example.com', role='customer')
        user2.set_password('password')
        db.session.add_all([user1, user2])
        db.session.commit()

        # Create sample products
        products = [
            Product(name='Laptop', user_id=1, category='Electronics', image_url='http://example.com/laptop.jpg', price=999.99, description='High performance laptop', stock=50),
            Product(name='Smart TV', user_id=1, category='Electronics', image_url='http://example.com/smart_tv.jpg', price=599.99, description='55 inch 4K Smart TV', stock=30)
        ]
        db.session.add_all(products)
        db.session.commit()

    def get_access_token(self, user_id):
        return create_access_token(identity=user_id)

    def test_view_wishlist(self):
        # Test viewing an empty wishlist
        user = User.query.filter_by(username='john_doe').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get('/api/wishlist', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_add_to_wishlist(self):
        # Test adding an item to the wishlist
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'product_id': product.id}
        response = self.client.post('/api/wishlist', headers=headers, json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Product added to wishlist', response.json['message'])

    def test_add_existing_item_to_wishlist(self):
        # Test adding an existing item to the wishlist
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        user.wishlists.append(product)
        db.session.commit()
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {'product_id': product.id}
        response = self.client.post('/api/wishlist', headers=headers, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Product already in wishlist', response.json['message'])

    def test_remove_from_wishlist(self):
        # Test removing an item from the wishlist
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        user.wishlists.append(product)
        db.session.commit()
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.delete(f'/api/wishlist/{product.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Product removed from wishlist', response.json['message'])

    def test_remove_nonexistent_item_from_wishlist(self):
        # Test removing a nonexistent item from the wishlist
        user = User.query.filter_by(username='john_doe').first()
        product_id = 999  # Assume this product does not exist
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.delete(f'/api/wishlist/{product_id}', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Product not in wishlist', response.json['message'])

if __name__ == '__main__':
    unittest.main()
