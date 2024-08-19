import os
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import timedelta

# Base configuration with default settings.
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'You will never walk alone')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key') 

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MAIL_USERNAME)

# Development configuration with settings for development.
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///app.db')

# Testing configuration with settings for testing.
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test_database.db')
    WTF_CSRF_ENABLED = False
    DEBUG = True

# Production configuration with settings for production.
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///prod_database.db')
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    ACCESS_TOKEN_EXPIRES = timedelta(days=30)

# Dictionary to map environment names to configuration classes.
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Optional function to load a configuration based on an environment variable.
def get_config(config_name=None):
    config_name = config_name or os.getenv('FLASK_CONFIG', 'development')
    return config_by_name.get(config_name, DevelopmentConfig)

# Define metadata, instantiate db.
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
api = Api()
cors = CORS()
mail = Mail()
