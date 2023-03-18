from unittest import TestCase

from api import create_app
from ..database import db
from ..models.users import Admin
from ..models.students import Student
from ..models.courses import Course


class CourseTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("config.Test")
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()

        db.create_all()
        Admin("Test Admin", "adminuser@admin.com", password_str="password123").save()
        Student("Test Student", "teststudent@gmail.com", password_str="password123").save()
        Course("Backend Engineering", "BE212", 3).save()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def get_access_token(self):
        data = {"email_address": "adminuser@admin.com", "password": "password123"}
        response = self.client.post("api/v0/auth/login/", json=data)
        return response.json["access_token"]

    def generate_auth_header(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def tests_get_all_courses(self):
        headers = self.generate_auth_header()
        response = self.client.get("api/v0/courses/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def tests_on_single_courses(self):
        headers = self.generate_auth_header()

        # Get a course
        response = self.client.get("api/v0/courses/1/", headers=headers)
        assert response.status_code == 200

        # Update course
        data = {"credit_unit": 1, "course_code": "BE500"}
        response = self.client.put("api/v0/courses/1/", json=data, headers=headers)
        assert response.status_code == 200
        assert b'"course_code": "BE500"' in response.data

        # Delete course
        response = self.client.delete("api/v0/courses/1/", headers=headers)
        assert response.status_code == 204

    def test_create_new_course(self):
        headers = self.generate_auth_header()
        data = {
            "title": "Frontend Engineering",
            "credit_unit": 3,
            "course_code": "FE121",
        }
        response = self.client.post("api/v0/courses/", json=data, headers=headers)
        assert response.status_code == 201
        assert b'"title": "Frontend Engineering"' in response.data

    def test_register_student_for_course(self):
        headers = self.generate_auth_header()
        student = Student.query.get(1)
        data = {
            "course_title": "Frontend Engineering",
            "school_id": f"{student.school_id}",
        }
        response = self.client.post("api/v0/courses/enroll/", json=data, headers=headers)
        print(response.json)
        assert response.status_code == 201
        assert (
            f"Student: {student.school_id} has registered for Frontend Engineering"
            in response.json.values()
        )

    def test_unregister_student_from_course(self):
        headers = self.generate_auth_header()
        student = Student.query.get(1)
        data = {
            "course_title": "Frontend Engineering",
            "school_id": f"{student.school_id}",
        }
        response = self.client.delete("api/v0/courses/enroll/", json=data, headers=headers)
        assert response.status_code == 204
