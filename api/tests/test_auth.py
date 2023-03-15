import unittest


from api import create_app
from ..database import db

class AuthTestCase(unittest.TestCase):

    headers = {"Content-Type": "application/json"}

    def setUpClass(self):

        self.app = create_app("TEST")
        self.test_app = self.app.app_context()
        self.test_app.push()
        self.client = self.app.test_client()

        db.create_all()

    @classmethod
    def tearDownClass(self):

        db.drop_all()
        self.test_app.pop()
        self.app = None
        self.client = None

    def test_admin_sign_up(self):

        data = {
            "full_name": "Admin User",
            "email_address": "adminuser@adimn.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        response = self.client.post("/auth/admin/signup/", json=data)
        assert response.status_code == 201


    # def test_user_login(self):
    #
    #     data = {
    #         "email_address": "adminuser@admin.com",
    #         "password": "password123"
    #     }
    #     response = self.client.post("/auth/login/", json=data)
    #     print(response.json)
    #     assert response.status_code == 200
    #     assert "access_token" in response.json

