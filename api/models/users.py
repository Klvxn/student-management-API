from ..database import db


class User(db.Model):

    __abstract__ = True

    full_name = db.Column(db.String(), nullable=True)
    email_address = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False)


class Admin(User):

    id = db.Column(db.Integer, primary_key=True, unique=True)


    def __repr__(self):
        return f"<Admin: {self.email_address}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
