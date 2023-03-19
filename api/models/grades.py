from enum import Enum

from ..database import db


class LetterGrades(Enum):
    A = range(70, 101)  # 70 - 100
    B = range(50, 70)   # 50 - 69
    C = range(30, 50)   # 30 - 49
    D = range(0, 30)    # 0 - 29


class Grade(db.Model):

    __tablename__ = "grades"

    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), primary_key=True)
    score = db.Column(db.Float, default=0.0)
    letter_grade = db.Column(db.CHAR(1), default="D")

    def __repr__(self):
        return f"<Grade: {self.student_id} - {self.course_id} - {self.score}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        self.score = 0.0
        self.letter_grade = "D"
        db.session.commit()

    def allocate_letter_grade(self):
        for letter in LetterGrades:
            if round(self.score) in letter.value:
                self.letter_grade = letter.name
                break
        return