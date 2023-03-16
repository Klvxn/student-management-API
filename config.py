from pathlib import Path

from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent

class Base:

    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/instance/lol.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "safe-space"
    SECRET_KEY = "safe-space"


class Dev(Base):

    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class Prod(Base):

    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class Test(Base):

    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/instance/test.db"
