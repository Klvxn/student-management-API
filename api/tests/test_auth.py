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

    def get_tokens(self):
        data = {
            "email_address": "testadmin@gmail.com",
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login", json=data)
        return response.json["access_token"], response.json["refresh_token"]

    def test_login_and_create_tokens(self):
        data = {
            "email_address": "testadmin@gmail.com",
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login", json=data)
        assert response.status_code == 200
        assert "access_token" in response.json
        assert "refresh_token" in response.json

    def test_access_token_refresh(self):
        refresh_token = self.get_tokens()[1]
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = self.client.post("api/v0/auth/token/refresh", headers=headers)
        assert response.status_code == 201
        assert "access_token" in response.json

    def test_password_change(self):
        access_token = self.get_tokens()[0]
        headers = {"Authorization": f"Bearer {access_token}"}
        data = {"new_password": "my_new_password"}
        response = self.client.post("api/v0/auth/change-password", json=data, headers=headers)
        assert response.status_code == 202
        assert b'Password changed successfully' in response.data

    def test_logout_user_and_revoke_token(self):
        access_token = self.get_tokens()[0]
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.client.post("api/v0/auth/logout", headers=headers)
        assert response.status_code == 200
        assert b'Token revoked' in response.data