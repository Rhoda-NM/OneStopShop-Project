import os
import pytest
import tempfile
from flask import session
from config import app, db, bcrypt
from models import Product, User
from seed import seed_db

@pytest.fixture(scope='module')
def test_client():
    # Create a temporary database file

    # Create a test client
    testing_client = app.test_client()

    # Establish an application context before running the tests
    ctx = app.app_context()
    ctx.push()

    yield testing_client
@pytest.fixture(scope='module')
def authenticate_user(test_client):
    """
    Authenticate a user and return the JWT token
    """
    # Create a JWT token for the test user
    response = test_client.post('/user/login', json={'email': 'user1@example.com', 'password': 'password1'})
    assert response.status_code == 200
    jwt_token = response.get_json()['access_token']

    return jwt_token
@pytest.fixture(scope='module')
def authenticate_admin(test_client):
    """
    Authenticate an admin and return the JWT token
    """
    # Create a JWT token for the test user
    response = test_client.post('/user/login', json={'email': 'admin@example.com', 'password': 'adminpassword'})
    assert response.status_code == 200
    jwt_token = response.get_json()['access_token']

    return jwt_token
@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table(s)
    with app.app_context():
        seed_db()
        yield db 



def test_get_all_products(test_client, init_database):
    """
    Test fetching all products
    """
    response = test_client.get('/api/products')
    assert response.status_code == 200
    assert len(response.get_json()) == 3

def test_create_product(test_client, init_database,authenticate_admin):
    """
    Test creating a new product
    """
    token = authenticate_admin
    data = {
        'name': 'Product2',
        'category': 'Category2',
        'image_url': 'http://example.com/image2.jpg',
        'price': 150.0,
        'description': 'Description2',
        'stock': 20
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/api/products', json=data, headers=headers)
    assert response.status_code == 201
    product = response.get_json()
    assert product['name'] == 'Product2'
    assert product['category'] == 'Category2'

def test_get_product_by_id(test_client, init_database):
    """
    Test fetching a product by ID
    """
    response = test_client.get('/api/products/1')
    assert response.status_code == 200
    product = response.get_json()
    assert product['name'] == 'Product 1'

def test_update_product(test_client, init_database,authenticate_admin):
    """
    Test updating a product
    """
    token = authenticate_admin
    data = {
        'name': 'UpdatedProduct2',
        'price': 120.0
    }
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.patch('/api/products/2', json=data, headers=headers)
    assert response.status_code == 200
    product = response.get_json()
    assert product['name'] == 'UpdatedProduct2'
    assert product['price'] == 120.0

def test_delete_product(test_client, init_database,authenticate_admin):
    """
    Test deleting a product
    """
    token =authenticate_admin
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.delete('/api/products/1', headers=headers)
    assert response.status_code == 204

def test_get_wishlist_items(test_client, init_database,authenticate_user):
    """
    Test fetching wishlist items for a user
    """
    token = authenticate_user
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.get('/api/wishlist', headers=headers)
    assert response.status_code == 200

def test_add_to_wishlist(test_client,init_database,authenticate_user):
    """
    Test adding a product to the wishlist
    """
    token = authenticate_user
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.post('/api/wishlists', json={'product_id': 1}, headers=headers)
    assert response.status_code == 201
    wishlist = response.get_json()
    assert wishlist['product_id'] == 1

def test_remove_from_wishlist(test_client, init_database,authenticate_user):
    """
    Test removing a product from the wishlist
    """
    token = authenticate_user
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.delete('/api/wishlists', json={'wishlist_id': 1}, headers=headers)
    assert response.status_code == 204
