import unittest

from werkzeug.security import generate_password_hash

from api import create_app
from ..database import db
from ..models.users import Admin


class TeacherTestCase(unittest.TestCase):

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

    def test_create_teacher(self):
        headers = self.generate_auth_header()
        data = {
            "full_name": "Test Teacher",
            "email_address": "testteacher@gmail.com"
        }
        response = self.client.post("teachers/", json=data, headers=headers)
        assert response.status_code == 201
        assert b'"full_name": "Test Teacher"' in response.data

    def test_get_all_teachers(self):
        headers = self.generate_auth_header()
        response = self.client.get("teachers/", headers=headers)
        assert response.status_code == 200

    def test_get_teacher(self):
        headers = self.generate_auth_header()
        response = self.client.get("teachers/1/", headers=headers)
        print(response.status_code)
        assert response.status_code == 200

    def test_update_teacher(self):
        headers = self.generate_auth_header()
        data = {
            "full_name": "Test Teacher Toe",
        }
        response = self.client.put("/teachers/1/", json=data, headers=headers)
        print(response.status_code)
        assert response.status_code == 200

    def test_delete_teacher(self):
        headers = self.generate_auth_header()
        response = self.client.delete("teachers/1/", headers=headers)
        assert response.status_code == 204