from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from werkzeug.exceptions import NotFound

from .database import db
from .models.users import Admin
from .models.courses import Course, enrollment
from .models.grades import Grade
from .models.students import Student
from .models.teachers import Teacher
from .resources.auth import auth_ns
from .resources.admin import admin_ns
from .resources.courses import course_ns
from .resources.grades import grade_ns
from .resources.students import student_ns
from .resources.teachers import teacher_ns
from .util import BLOCKLIST


def create_app(stage):

    app = Flask(__name__)

    app.config.from_object(stage)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    migrate = Migrate(app, db, "migrations")
    jwt = JWTManager(app)

    authorizations = {
        "Bearer auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Your jwt token goes here",
        }
    }
    api = Api(
        app,
        version="0.1",
        title="Student Management API",
        description="A REST API service for Altacademy's student management system",
        authorizations=authorizations,
        security="Bearer auth",
        ordered=True,
        catch_all_404s=True
    )

    api.add_namespace(admin_ns, path="/admin")
    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(course_ns, path="/courses")
    api.add_namespace(grade_ns, path="/grade")
    api.add_namespace(student_ns, path="/students")
    api.add_namespace(teacher_ns, path="/teachers")


    @api.errorhandler(NotFound)
    def catch_404(error):
        return {"message": "The resource not found."}, 404

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        role = jwt_data["role"]
        if role == "ADMIN": return Admin.query.get(identity)
        elif role == "TEACHER": return Teacher.query.get(identity)
        else: return Student.query.get(identity)

    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "Admin": Admin,
            "Student": Student,
            "Teacher": Teacher,
            "Course": Course,
            "Grade": Grade,
            "enrollment": enrollment
        }

    return app
