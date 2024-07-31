from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import bcrypt,db


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String(128))
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    orders = db.relationship('Order', backref='user')
    order_items = association_proxy('orders', 'order_items')

    serialize_rules = ('-_password_hash', '-orders', '-created_at', '-updated_at')

    @validates('username', 'email')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'User must have a {key}')
        return value

    def set_password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password)

class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    stock = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    order_items = db.relationship('OrderItem', backref='product')

    serialize_rules = ('-order_items', '-created_at', '-updated_at')

    @validates('name', 'category', 'price', 'stock')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'Product must have a {key}')
        return value

class Order(db.Model, SerializerMixin):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    order_items = db.relationship('OrderItem', backref='order')
    items = association_proxy('order_items', 'product')

    serialize_rules = ('-order_items', '-user', 'created_at', 'updated_at')

class OrderItem(db.Model, SerializerMixin):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    serialize_rules = ('-order', '-product', '-created_at', '-updated_at')

    @validates('quantity', 'price')
    def validate_fields(self, key, value):
        if value <= 0:
            raise ValueError(f'{key.capitalize()} must be greater than 0')
        return value

class ViewingHistory(db.Model, SerializerMixin):
    __tablename__ = 'viewing_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    viewed_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='viewing_history')
    product = db.relationship('Product', backref='viewing_history')

    serialize_rules = ('-user', '-product', '-viewed_at')

class SearchQuery(db.Model, SerializerMixin):
    __tablename__ = 'search_query'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    query = db.Column(db.String(200))
    searched_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='search_queries')

    serialize_rules = ('-user', '-searched_at')

class Engagement(db.Model, SerializerMixin):
    __tablename__ = 'engagement'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    watch_time = db.Column(db.Integer)  
    engaged_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='engagements')
    product = db.relationship('Product', backref='engagements')

    serialize_rules = ('-user', '-product', '-engaged_at')

class Wishlist(db.Model, SerializerMixin):
    __tablename__ = 'wishlists'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))

    user = db.relationship('User', backref='wishlists')
    product = db.relationship('Product', backref='wishlists')

    serialize_rules = ('-user', '-product')