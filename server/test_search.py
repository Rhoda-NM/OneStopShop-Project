import unittest
from flask_jwt_extended import create_access_token, JWTManager
from app import create_app
from models import db, Product

class TestSearchBlueprint(unittest.TestCase):

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
        # Create test products
        self.product1 = Product(name='Apple iPhone', category='Electronics', price=999.99, description='Smartphone by Apple', stock=10)
        self.product2 = Product(name='Apple MacBook', category='Electronics', price=1299.99, description='Laptop by Apple', stock=5)
        db.session.add_all([self.product1, self.product2])
        db.session.commit()

    def test_search(self):
        response = self.client.get('/api/search?q=Apple')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        self.assertIn('suggestions', data)

    def test_no_query(self):
        response = self.client.get('/api/search')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'No search query provided')

if __name__ == '__main__':
    unittest.main()
