from .users import User
from ..database import db


class Teacher(User):
    """
     Model for teachers
     """

    __tablename__ = "teacher"

    id = db.Column(db.Integer, primary_key=True)

    # One-to-one relationship with course
    course = db.relationship("Course", backref="teacher", uselist=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role = "TEACHER"
