from unittest import TestCase

from .. import create_app
from ..database import db
from ..models.courses import Course
from ..models.students import Student
from ..models.teachers import Teacher


class GradeTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("config.Test")
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()

        db.create_all()

        # Create initial data in the database to test with
        Teacher("Test Teacher", "testteacher@gmail.com", "password123").save()
        Student("Test Student", "teststudent@gmail.com", "password123").save()
        Course("Backend Test", "BT112", 3, teacher_id=1).save()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def get_access_token(self):
        data = {
            "email_address": "testteacher@gmail.com",
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login", json=data)
        return response.json["access_token"]

    def generate_auth_header(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def test_cannot_grade_student_not_registered_for_course(self):
        headers = self.generate_auth_header()
        course = Course.query.all()[0]
        student = Student.query.all()[0]
        data = {"score": 54.33}
        response = self.client.post(
            f"api/v0/grade/{student.id}/{course.id}", json=data, headers=headers
        )
        assert response.status_code == 400
        assert b"This student did not register for this course" in response.data

    def register_student_for_course(self):
        headers = self.generate_auth_header()
        student = Student.query.all()[0]
        data = {
            "course_title": "Backend Test",
            "school_id": f"{student.school_id}",
        }
        self.client.post("api/v0/courses/enroll", json=data, headers=headers)

    def test_grade_student_in_course(self):
        self.register_student_for_course()
        course = Course.query.all()[0]
        student = Student.query.all()[0]
        headers = self.generate_auth_header()
        data = {"score": 98.5}
        response = self.client.post(
            f"api/v0/grade/{student.id}/{course.id}", json=data, headers=headers
        )
        print(response.json)
        assert response.status_code == 201
        assert b'"score": 98.5' in response.data
        assert b'"letter_grade": "A"' in response.data

    def test_update_student_grade_in_course(self):
        course = Course.query.all()[0]
        student = Student.query.all()[0]
        headers = self.generate_auth_header()
        data = {"score": 40.5}
        response = self.client.put(
            f"api/v0/grade/{student.id}/{course.id}", json=data, headers=headers
        )
        assert response.status_code == 200
        assert b'"score": 40.5' in response.data
        assert b'"letter_grade": "C"' in response.data