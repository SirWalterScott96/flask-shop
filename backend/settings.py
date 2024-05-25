# -*- coding: utf-8 -*-
"""Application configuration."""
import os
from dotenv import load_dotenv
from datetime import timedelta
from flask.helpers import get_debug_flag
from pathlib import Path

APP_DIR = Path(__file__).parent
load_dotenv(dotenv_path=APP_DIR.parent / '.env')


class Config:
    ENV = "dev"
    SECRET_KEY = os.getenv('SECRET_KEY')
    FLASK_DEBUG = get_debug_flag()
    UPLOAD_EXTENSIONS = ['jpg', 'png', 'JPG']
    REMEMBER_COOKIE_DURATION = timedelta(days=3)
    UPLOAD_FOLDER_PRODUCT_IMGS = APP_DIR / 'static' / 'product_imgs'
    UPLOAD_FOLDER_SUBCATEGORY_IMGS = APP_DIR / 'static' / 'subcategory_imgs'

    #Database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{APP_DIR / 'instance' / 'database.db'}"
    MIGRATIONS_FOLDER = APP_DIR / 'migrations'

    # Mail
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Flask Shop', 'Flask Shop')

    LOGIN_REDIRECT_URL = '/user/login'