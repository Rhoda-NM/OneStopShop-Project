# Standard library imports
import os
# Remote library imports
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from flask_jwt_extended import JWTManager # type: ignore
from datetime import timedelta

# Local imports

# Instantiate app, set attributes
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
#app.config['SECRET_KEY']= 'You will never walk Alone'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.json.compact = False

class Config:
    """Base configuration with default settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'You will never walk alone')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Longer-lived refresh token
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # For a 24-hour access token


class DevelopmentConfig(Config):
    """Development configuration with settings for development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///app.db')
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Longer-lived refresh token
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # For a 24-hour access token


class TestingConfig(Config):
    """Testing configuration with settings for testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test_database.db')
    WTF_CSRF_ENABLED = False
    DEBUG = True
    

class ProductionConfig(Config):
    """Production configuration with settings for production."""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///prod_database.db')
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)  # Longer-lived refresh token
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)  # For a 24-hour access token

# Dictionary to map environment names to configuration classes
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

# Optional function to load a configuration based on an environment variable
def get_config(config_name=None):
    config_name = config_name or os.getenv('FLASK_CONFIG', 'development')
    return config_by_name.get(config_name, DevelopmentConfig)

# Define metadata, instantiate db
metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
api = Api()
cors = CORS()