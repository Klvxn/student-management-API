import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class BaseConfig:

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/instance/db.sqlite3"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "secret-space")
    SECRET_KEY = os.environ.get("SECRET_KEY")


class Development(BaseConfig):

    DEBUG = True
    ENV = "development"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class Production(BaseConfig):

    DEBUG = False
    ENV = "production"
    SQLALCHEMY_ECHO = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class Test(BaseConfig):

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/instance/test.db"
