from unittest import TestCase

from .. import create_app
from ..database import db
from ..models.users import Admin


class StudentTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("config.Test")
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()

        db.create_all()
        Admin("Test Admin", "testadmin@gmail.com", "password123").save()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def get_access_token(self):
        data = {
            "email_address": "testadmin@gmail.com",
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login/", json=data)
        return response.json["access_token"]

    def generate_auth_header(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def test_create_student(self):
        headers = self.generate_auth_header()
        data = {
            "full_name": "Student One",
            "email_address": "studentone@gmail.com"
        }
        response = self.client.post("api/v0/students/", json=data, headers=headers)
        assert response.status_code == 201
        assert b'"full_name": "Student One"' in response.data

    def test_get_all_students(self):
        headers = self.generate_auth_header()
        response = self.client.get("api/v0/students/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def tests_on_single_student(self):
        headers = self.generate_auth_header()

        # Get a student
        response = self.client.get("api/v0/students/1/", headers=headers)
        assert response.status_code == 200

        # Update student
        data = {
            "full_name": "Student Two",
            "email_address": "studenttwo@gmail.com"
        }
        response = self.client.put("api/v0/students/1/", json=data, headers=headers)
        assert response.status_code == 200
        assert b'"full_name": "Student Two"' in response.data

        # Delete student:
        response = self.client.delete("api/v0/students/1/", headers=headers)
        assert response.status_code == 204
