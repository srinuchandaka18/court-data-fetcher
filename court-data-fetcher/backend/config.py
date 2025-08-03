import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    TARGET_COURT = os.getenv('TARGET_COURT', 'delhi_high_court')
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'database/court_data.db')
    CAPTCHA_STRATEGY = os.getenv('CAPTCHA_STRATEGY', 'manual')
    
    # Flask configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Rate limiting
    MAX_REQUESTS_PER_HOUR = int(os.getenv('MAX_REQUESTS_PER_HOUR', '10'))
