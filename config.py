from datetime import timedelta


class Base:

    SQLALCHEMY_DATABASE_URI = "sqlite:///smstest.db"
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
    SQLALCHEMY_DATABASE_URI = "sqlite:///test_base.db"

STAGE = {
    "DEV": Dev,
    "PROD": Prod,
    "TEST": Test
}