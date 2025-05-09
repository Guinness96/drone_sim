import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

class Config:
    # PostgreSQL connection string
    # Format: postgresql://username:password@hostname:port/dbname
    default_postgres_uri = 'postgresql://drone_user:drone_password@localhost:5432/drone_monitoring_db'
    
    # Get database URL from environment or use local PostgreSQL by default
    database_url = os.getenv('DATABASE_URL', default_postgres_uri)
    
    # Fix issue with PostgreSQL URLs from some providers that use 'postgres://' instead of 'postgresql://'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-placeholder')  # Change this in production!
    
    # Development-specific configuration
    DEBUG = os.getenv('FLASK_ENV') == 'development' 