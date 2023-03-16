import unittest

from werkzeug.security import generate_password_hash

from api import create_app
from ..database import db
from ..models.users import Admin


class CourseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("TEST")
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()

        db.create_all()
        Admin(
            email_address="adminuser@admin.com",
            full_name="Test Admin",
            password_hash=generate_password_hash("password123"),
            role="ADMIN"
        ).save()

    @classmethod
    def tearDownClass(cls):
        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def get_access_token(self):
        data = {
            "email_address": "adminuser@admin.com",
            "password": "password123"
        }
        response = self.client.post("/auth/login/", json=data)
        return response.json["access_token"]

    def generate_auth_header(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def test_create_course(self):
        headers = self.generate_auth_header()
        data = {
            "title": "Frontend Engineering",
            "credit_unit": 3,
            "course_code": "FE121"
        }
        response = self.client.post("courses/", json=data, headers=headers)
        assert response.status_code == 201
        assert b'"title": "Frontend Engineering"' in response.data

    def test_get_all_courses(self):
        headers = self.generate_auth_header()
        response = self.client.get("courses/", headers=headers)
        assert response.status_code == 200
        print(response.json)

    def test_get_single_course(self):
        headers = self.generate_auth_header()
        response = self.client.get("courses/1/", headers=headers)
        print(response.json)
        assert response.status_code == 200

    def test_update_course(self):
        headers = self.generate_auth_header()
        data = {
            "credit_unit": 1,
            "course_code": "FE101"
        }
        response = self.client.put("courses/1/", json=data, headers=headers)
        print(response.json)
        assert response.status_code == 200

    def test_delete_course(self):
        headers = self.generate_auth_header()
        response = self.client.delete("courses/1/", headers=headers)
        assert response.status_code == 204