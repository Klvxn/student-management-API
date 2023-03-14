from api.database import db


enrollment = db.Table(
    "enrollment",
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("student_id", db.Integer, db.ForeignKey("student.id")),
)


class Course(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False, unique=True)
    credit_unit = db.Column(db.Integer, nullable=False, default=1)
    code = db.Column(db.String(6), nullable=False, unique=True)

    # one-to-one relationship with teacher model
    teacher = db.relationship("Teacher", backref="courses", uselist=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id", ondelete="CASCADE"))

    # many-to-many relationship with student model
    students = db.relationship("Student", secondary=enrollment, backref="courses")

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
