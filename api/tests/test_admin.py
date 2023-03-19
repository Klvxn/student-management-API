from unittest import TestCase

from .. import create_app
from ..database import db
from ..models.students import Student

class AdminTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app("config.Test")
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

    def get_access_token(self):
        data = {
            "email_address": "testadmin@gmail.com",
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login", json=data)
        return response.json["access_token"]

    def generate_auth_header(self):
        token = self.get_access_token()
        headers = {"Authorization": f"Bearer {token}"}
        return headers

    def test_admin_sign_up(self):
        data = {
            "full_name": "Admin User",
            "email_address": "testadmin@gmail.com",
            "password": "password123",
            "confirm_password": "password123",
        }
        response = self.client.post("api/v0/admin/signup", json=data)
        assert response.status_code == 201
        assert b'"full_name": "Admin User"' in response.data

    def test_get_all_admins(self):
        headers = self.generate_auth_header()
        response = self.client.get("api/v0/admin/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json, list)

    def tests_on_single_admin(self):
        headers = self.generate_auth_header()

        # Get an admin
        response = self.client.get("api/v0/admin/1", headers=headers)
        assert response.status_code == 200

        # Update admin
        data = {
            "full_name": "Admin Two",
            "email_address": "admintwo@gmail.com"
        }
        response = self.client.put("api/v0/admin/1", json=data, headers=headers)
        assert response.status_code == 200
        assert b'"full_name": "Admin Two"' in response.data
        assert b'"email_address": "admintwo@gmail.com"' in response.data

        # Delete admin:
        response = self.client.delete("api/v0/admin/1", headers=headers)
        assert response.status_code == 204

    # Test that only admins can access the admin endpoints
    def get_student_token(self):
        student = Student("Test Student", "teststudent@gmail.com", "password123")
        student.save()
        data = {
            "school_id": student.school_id,
            "password": "password123"
        }
        response = self.client.post("api/v0/auth/login", json=data)
        return response.json["access_token"]

    def test_protected_endpoints(self):
        token = self.get_student_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get("api/v0/admin/", headers=headers)
        assert response.status_code == 403
        assert b'"Admin access only"' in response.data