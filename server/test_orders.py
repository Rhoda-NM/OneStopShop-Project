import unittest
from flask_jwt_extended import create_access_token, JWTManager
from app import create_app
from models import db,  User, Product, Order, OrderItem

class OrdersTestCase(unittest.TestCase):

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

    def test_view_cart(self):
        # Test viewing an empty cart
        user = User.query.filter_by(username='john_doe').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.get('/api/cart', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('No items in the cart', response.json['message'])

    def test_add_to_cart(self):
        # Test adding items to the cart
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        data = {
            'order_items': [
                {'product_id': product.id, 'quantity': 1}
            ]
        }
        response = self.client.post('/api/cart', headers=headers, json=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['status'], 'cart')

    def test_remove_from_cart(self):
        # Test removing items from the cart
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        
        # Add item to the cart first
        order = Order(user_id=user.id, status='cart', total_price=product.price)
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=product.price)
        db.session.add(order_item)
        db.session.commit()
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.delete(f'/api/cart/{product.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Cart is now empty', response.json['message'])

    def test_checkout(self):
        # Test checking out
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        
        # Add item to the cart first
        order = Order(user_id=user.id, status='cart', total_price=product.price)
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=product.price)
        db.session.add(order_item)
        db.session.commit()
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.post('/api/checkout', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'pending')

    def test_complete_order(self):
        # Test completing an order
        user = User.query.filter_by(username='john_doe').first()
        product = Product.query.filter_by(name='Laptop').first()
        
        # Add item to the cart first and checkout
        order = Order(user_id=user.id, status='pending', total_price=product.price)
        db.session.add(order)
        db.session.commit()
        
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=1, price=product.price)
        db.session.add(order_item)
        db.session.commit()
        
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.post(f'/api/complete_order/{order.id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'completed')

    def test_get_orders(self):
        # Test getting all previous orders
        user = User.query.filter_by(username='john_doe').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Add some orders
        order1 = Order(user_id=user.id, status='completed', total_price=1000)
        order2 = Order(user_id=user.id, status='completed', total_price=1500)
        db.session.add_all([order1, order2])
        db.session.commit()
        
        response = self.client.get('/api/orders', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

if __name__ == '__main__':
    unittest.main()
