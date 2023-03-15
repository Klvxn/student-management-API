from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api
from werkzeug.exceptions import NotFound

from config import STAGE
from .database import db
from .models.users import Admin
from .models.students import Student
from .models.teachers import Teacher
from .resources.auth import auth_ns
from .resources.courses import course_ns
from .resources.grades import grade_ns
from .resources.students import student_ns
from .resources.teachers import teacher_ns


def create_app(stage):

    app = Flask(__name__)

    config = STAGE[stage]
    app.config.from_object(config)

    db.init_app(app)
    with app.app_context():
        db.create_all()


    migrate = Migrate(app, db)
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
        description="A REST API service for a school's student management system",
        authorizations=authorizations,
        security="Bearer auth",
        ordered=True,
        catch_all_404s=True
    )

    api.add_namespace(auth_ns, path="/auth")
    api.add_namespace(course_ns, path="/courses")
    api.add_namespace(grade_ns, path="/grade")
    api.add_namespace(student_ns, path="/students")
    api.add_namespace(teacher_ns, path="/teachers")


    @api.errorhandler(NotFound)
    def catch_404(error):
        return {"message": "The resource not found."}, 404

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        print(jwt_data)
        identity = jwt_data["sub"]
        role = jwt_data["role"]
        if role == "ADMIN": return Admin.query.get(identity)
        elif role == "TEACHER": return Teacher.query.get(identity)
        else: return Student.query.get(identity)

    return app
