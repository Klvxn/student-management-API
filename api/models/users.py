from ..database import db

from werkzeug.security import generate_password_hash


class User(db.Model):
    """
    BaseConfig model for all users including students, teachers and admins.
    """

    __abstract__ = True

    full_name = db.Column(db.String(), nullable=True)
    email_address = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False)

    def __init__(self, full_name, email_address, password_str):
        self.full_name = full_name
        self.email_address = email_address
        self.password_hash = generate_password_hash(password_str)

    def __repr__(self):
        return f"<{__class__.__name__}: {self.full_name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Admin(User):
    """
    Model for admin users
    """

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, unique=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "ADMIN"
