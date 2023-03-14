from enum import Enum

from api.database import db


class LetterGrades(Enum):
    A = range(70, 101)
    B = range(55, 70)
    C = range(40, 55)
    D = range(30, 40)
    F = range(0, 30)


class Grade(db.Model):

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), primary_key=True)
    score = db.Column(db.Float, default=0.0)
    letter_grade = db.Column(db.CHAR(1))

    # relationships between student and course
    student = db.relationship("Student", backref="grades")
    course = db.relationship("Course", backref="grade", uselist=False)

    def __repr__(self):
        return f"<Grade: {self.student.full_name} - {self.course.title} - {self.score}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def allocate_letter_grade(self):
        for letter in LetterGrades:
            if round(self.score) in letter.value:
                self.letter_grade = letter.name
                break
        return