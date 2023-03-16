from .users import User
from ..database import db


class Teacher(User):

    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)

    # One-to-one relationship with course
    course = db.relationship("Course", backref="teacher", uselist=False)

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
