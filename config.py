from datetime import timedelta


class Default:

    SQLALCHEMY_DATABASE_URI = "sqlite:///db.sqlite3"
    JWT_SECRET_KEY = "safe-space"
    SECRET_KEY = "safe-space"


class Dev(Default):

    DEBUG = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=3)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


class Prod(Default):

    DEBUG = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)


STAGE = {
    "DEV": Dev,
    "PROD": Prod,
    "TEST": "TEST"
}