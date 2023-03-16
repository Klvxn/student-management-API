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
        print("testing")

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


    def test_user_login(self):

        data = {
            "email_address": "adminuser@admin.com",
            "password": "password123"
        }
        response = self.client.post("/auth/login/", json=data)
        self.token = response.json["access_token"]
        assert response.status_code == 200
        assert "access_token" in response.json

