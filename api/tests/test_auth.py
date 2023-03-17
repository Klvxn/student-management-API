from unittest import TestCase

from .. import create_app
from ..database import db
from ..models.users import Admin


class AuthTestCase(TestCase):

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


    def test_login_and_create_tokens(self):
        data = {
            "email_address": "testadmin@gmail.com",
            "password": "password123"
        }
        response = self.client.post("/auth/login/", json=data)
        assert response.status_code == 200
        assert "access_token" in response.json
        assert "refresh_token" in response.json
        return response.json["refresh_token"]

    def test_refresh_access_token(self):
        refresh_token = self.test_login_and_create_tokens()
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = self.client.post("auth/token/refresh/", headers=headers)
        assert response.status_code == 201
        assert "access_token" in response.json