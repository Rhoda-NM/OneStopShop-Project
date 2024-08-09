from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates, relationship,backref
from sqlalchemy.ext.hybrid import hybrid_property
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from config import  db
from app import bcrypt

# Association table for many-to-many relationship between users and products

wishlist_table = db.Table('wishlist_table',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True)
)
# Association table for the many-to-many relationship between Products and Tags
product_tag_association = db.Table('product_tag_association',
    db.Column('product_id', db.Integer, db.ForeignKey('products.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)
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
    products = db.relationship('Product', back_populates='seller')
   
    wishlists = relationship('Product', secondary=wishlist_table, backref=backref('wishlisted_by_users', lazy='dynamic'))

    serialize_rules = ('-_password_hash', '-orders', '-created_at', '-updated_at')

    @validates('username', 'email')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'User must have a {key}')
        return value

    def set_password(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf8')
    
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            #'wishlists': [wishlist.serialize() for wishlist in self.wishlists]
        }


class Product(db.Model, SerializerMixin):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    sku = db.Column(db.String, nullable=False, unique=True)
    stock = db.Column(db.Integer, nullable=False)
    tags = db.relationship('Tag', secondary=product_tag_association, back_populates='products')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller = db.relationship('User', back_populates='products')

    order_items = db.relationship('OrderItem', backref='product')

    serialize_rules = ('-order_items', '-created_at', '-updated_at','-seller')

    @validates('name', 'category', 'price', 'stock')
    def validate_fields(self, key, value):
        if not value:
            raise ValueError(f'Product must have a {key}')
        return value
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'image_url': self.image_url,
            'description': self.description,
            'images': self.images
        }
    
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    products = db.relationship('Product', backref='category', lazy=True)
    tags = db.relationship('Tag', backref='category', lazy=True)
    def __repr__(self):
        return f"<Category(name={self.name})>"
    
class Tag(db.Model):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    products = db.relationship('Product', secondary=product_tag_association, back_populates='tags')

    def __repr__(self):
        return f"<Tag(name={self.name}, category_id={self.category_id})>"

class ProductImage(db.Model, SerializerMixin):
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image_url = db.Column(db.String, nullable=False)

    product = db.relationship('Product', back_populates='images')
    
    serialize_rules = ('-product',)


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
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'order_items': [item.serialize() for item in self.order_items]
        }

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
    
    def serialize(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price
        }


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
    search_query = db.Column(db.String(200))
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

class Rating(db.Model, SerializerMixin):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    product = db.relationship('Product', backref='ratings')
    user = db.relationship('User', backref='ratings')
    
    def __init__(self, product_id, user_id, rating, comment=None):
        self.product_id = product_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment

class Discount(db.Model, SerializerMixin):
    __tablename__ = 'discounts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, product_id, discount_percentage, start_date, end_date):
        self.product_id = product_id
        self.discount_percentage = discount_percentage
        self.start_date = start_date
        self.end_date = end_date
