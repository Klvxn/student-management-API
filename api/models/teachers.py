from api.database import db


class Teacher(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(10), nullable=False)
    email_address = db.Column(db.String(20), nullable=False, unique=True, index=True)

    # one-to-one relationship with the user model
    user = db.relationship("User", backref="teacher", uselist=False)

    def __repr__(self) -> str:
        return f"<Teacher: {self.full_name}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
