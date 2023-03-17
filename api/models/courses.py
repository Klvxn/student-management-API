from ..database import db


enrollment = db.Table(
    "enrollment",
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
)


class Course(db.Model):

    __tablename__ = "course"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False, unique=True)
    course_code = db.Column(db.String(6), nullable=False, unique=True)
    credit_unit = db.Column(db.Integer, nullable=False, default=1)

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))

    # many-to-many relationship with student model
    students = db.relationship("Student", secondary=enrollment, backref="courses")

    def __init__(self, title, course_code, credit_unit, **kwargs):
        self.title = title
        self.course_code = course_code
        self.credit_unit = credit_unit

    def __repr__(self):
        return f"<Course: {self.title}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_title(cls, course_title):
        return cls.query.filter_by(title=course_title).first_or_404()
