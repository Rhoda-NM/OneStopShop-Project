import unittest
from flask_jwt_extended import create_access_token, JWTManager
from app import create_app
from models import db, User, Product, ViewingHistory, SearchQuery, Engagement
from datetime import datetime 

class ProductsTestCase(unittest.TestCase):

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
        admin_user = User(username='admin', email='admin@example.com', role='admin')
        admin_user.set_password('password')
        customer_user = User(username='customer', email='customer@example.com', role='customer')
        customer_user.set_password('password')
        db.session.add_all([admin_user, customer_user])
        db.session.commit()

        # Create sample products
        products = [
            Product(name='Laptop', user_id=admin_user.id, category='Electronics', image_url='http://example.com/laptop.jpg', price=999.99, description='High performance laptop', stock=50),
            Product(name='Smart TV', user_id=admin_user.id, category='Electronics', image_url='http://example.com/smart_tv.jpg', price=599.99, description='55 inch 4K Smart TV', stock=30)
        ]
        db.session.add_all(products)
        db.session.commit()

    def get_access_token(self, user_id):
        return create_access_token(identity=user_id)

    def test_get_products(self):
        response = self.client.get('/api/products')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_create_product(self):
        admin_user = User.query.filter_by(username='admin').first()
        access_token = self.get_access_token(admin_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {
            'name': 'Smartphone',
            'category': 'Mobiles',
            'price': 699.99,
            'description': 'Latest model smartphone',
            'stock': 100
        }
        response = self.client.post('/api/products', headers=headers, json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], 'Smartphone')

    def test_get_product(self):
        product = Product.query.filter_by(name='Laptop').first()
        response = self.client.get(f'/api/products/{product.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Laptop')

    def test_update_product(self):
        admin_user = User.query.filter_by(username='admin').first()
        product = Product.query.filter_by(name='Laptop').first()
        access_token = self.get_access_token(admin_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {
            'name': 'Gaming Laptop'
        }
        response = self.client.patch(f'/api/products/{product.id}', headers=headers, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Gaming Laptop')

    def test_delete_product(self):
        admin_user = User.query.filter_by(username='admin').first()
        product = Product.query.filter_by(name='Laptop').first()
        access_token = self.get_access_token(admin_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.delete(f'/api/products/{product.id}', headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(Product.query.get(product.id))

    def test_get_recommended_products(self):
        customer_user = User.query.filter_by(username='customer').first()
        product = Product.query.filter_by(name='Laptop').first()
        
        # Add viewing history
        view = ViewingHistory(user_id=customer_user.id, product_id=product.id, viewed_at=datetime.utcnow())
        db.session.add(view)
        db.session.commit()
        
        access_token = self.get_access_token(customer_user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get('/api/recommended_products', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json['recommended_products']), 0)

if __name__ == '__main__':
    unittest.main()
