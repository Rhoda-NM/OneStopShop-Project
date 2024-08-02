import unittest
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from app import create_app
from models import db, User


class AuthenticateTestCase(unittest.TestCase):

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

    def get_access_token(self, user_id):
        return create_access_token(identity=user_id)

    def get_refresh_token(self, user_id):
        return create_refresh_token(identity=user_id)

    def test_register(self):
        # Test user registration
        response = self.client.post('/user/register', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_login(self):
        # Test user login
        response = self.client.post('/user/login', json={
            'email': 'john@example.com',
            'password': 'password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

    def test_update_user(self):
        # Test updating user information
        user = User.query.filter_by(email='john@example.com').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.put(f'/user/update_user/{user.id}', headers=headers, json={
            'email': 'updated@example.com',
            'username': 'updateduser'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['msg'], 'User updated successfully')

    def test_delete_user(self):
        # Test deleting a user
        user = User.query.filter_by(email='john@example.com').first()
        access_token = self.get_access_token(user.id)
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.client.delete('/user/delete/1', headers=headers)
        self.assertEqual(response.status_code, 204)
        self.assertIsNone(db.session.get(User, user.id))

if __name__ == '__main__':
    unittest.main()

