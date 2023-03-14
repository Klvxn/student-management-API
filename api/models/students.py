from datetime import date

from api.database import db
from api.models.grades import Grade


class Student(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.String(), index=True, unique=True)
    full_name = db.Column(db.String(10), nullable=False)
    email_address = db.Column(db.String(20), nullable=False, unique=True)
    gpa = db.Column(db.Float(precision=2, asdecimal=True))

    # One-to-one relationship with user model
    user = db.relationship("User", backref="student", uselist=False)

    def __repr__(self) -> str:
        return f"<Student: {self.full_name}>"

    def save(self):
        self.school_id = self.generate_school_id()
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    @classmethod
    def get_by_school_id(cls, school_id):
        return cls.query.filter_by(school_id=school_id).first_or_404()

    def generate_school_id(self):
        """"
        Generate a school ID for every student from their full name
        """
        full_name = self.full_name
        first_name = full_name.split()[0]
        hashed_name = hash(full_name)
        num = abs(hashed_name) % 1000000
        school_id = first_name.upper() + str(num) + "/" + str(date.today().year)
        return school_id

    def calculate_student_gpa(self):
        """
        Calculate the GPA of a student.
        """
        grade_points = {"A": 4.00, "B": 3.00, "C": 2.00, "D": 1.00, "F": 0.00}
        total_credit_unit = total_points = 0
        for course in self.courses:
            grade = Grade.query.get((self.id, course.id))
            point = grade_points[grade.letter_grade] * course.credit_unit
            total_points += point
            total_credit_unit += course.credit_unit
        student_gpa = round(total_points / total_credit_unit, 2)
        self.gpa = student_gpa
        self.commit_update()
        return student_gpa
