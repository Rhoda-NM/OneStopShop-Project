import unittest
from flask import current_app
from flask_testing import TestCase
from flask_jwt_extended import decode_token

from app import create_app, db
from models import User

class TestAuthBlueprint(TestCase):

    def create_app(self):
        app = create_app('testing')  # Ensure you have a testing config
        return app

    def setUp(self):
        db.create_all()
        self.client = self.app.test_client()
        self.register_url = '/user/register'
        self.login_url = '/user/login'

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        response = self.client.post(self.register_url, json={
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_duplicate_registration(self):
        self.client.post(self.register_url, json={
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        })
        response = self.client.post(self.register_url, json={
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], 'User already exists')

    def test_login(self):
        self.client.post(self.register_url, json={
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        })
        response = self.client.post(self.login_url, json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_invalid_login(self):
        response = self.client.post(self.login_url, json={
            'email': 'invalid@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['error'], 'Invalid credentials')

    def test_token_refresh(self):
        self.client.post(self.register_url, json={
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        })
        login_response = self.client.post(self.login_url, json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        refresh_token = login_response.get_json()['refresh_token']
        headers = {'Authorization': f'Bearer {refresh_token}'}
        refresh_response = self.client.get('/user/login', headers=headers)
        self.assertEqual(refresh_response.status_code, 200)
        data = refresh_response.get_json()
        self.assertIn('token', data)

if __name__ == '__main__':
    unittest.main()
