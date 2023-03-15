import unittest

from api import create_app
from ..database import db


class StudentTestCase(unittest.TestCase):

    def setUpClass(self):
        self.app = create_app("TEST")
        self.test_app = self.app.app_context()
        self.test_app.push()
        self.client = self.app.test_client()

        db.create_all()

    def tearDownClass(self):
        db.drop_all()
        self.test_app.pop()
        self.app = None
        self.client = None
