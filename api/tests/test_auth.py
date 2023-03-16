import unittest

from api import create_app
from ..database import db

class AuthTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):


        cls.app = create_app("TEST")
        cls.test_app = cls.app.app_context()
        cls.test_app.push()
        cls.client = cls.app.test_client()

        db.create_all()

    @classmethod
    def tearDownClass(cls):

        db.drop_all()
        cls.test_app.pop()
        cls.app = None
        cls.client = None

    def test_admin_sign_up(self):
        data = {
            "full_name": "Admin User",
            "email_address": "adminuser@admin.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        response = self.client.post("/admin/signup/", json=data)
        assert response.status_code == 201

    def test_login_and_create_tokens(self):
        data = {
            "email_address": "adminuser@admin.com",
            "password": "password123"
        }
        response = self.client.post("/auth/login/", json=data)
        assert response.status_code == 200
        assert "access_token" in response.json
        assert "refresh_token" in response.json
        return response.json["refresh_token"]

    def test_create_refresh_token(self):
        refresh_token = self.test_login_and_create_tokens()
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = self.client.post("auth/token/refresh/", headers=headers)
        print(response.status_code)
        assert response.status_code == 201
        assert "access_token" in response.json