from functools import wraps
from http import HTTPStatus
from .models.students import Student
from .models.teachers import Teacher

from flask_jwt_extended import get_current_user, get_jwt, verify_jwt_in_request

BLOCKLIST = set()


def admin_required():
    """
    Decorator to allow only users with `ADMIN` role access
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role", None)
            if role == "ADMIN":
                return fn(*args, **kwargs)
            return {"msg": "Admin access only"}, HTTPStatus.FORBIDDEN
        return decorator
    return wrapper


def teacher_only():
    """
    Decorator to protect endpoints meant for only teachers.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role", None)
            if role == "TEACHER":
                return fn(*args, **kwargs)
            return {"msg": "Only a teacher can access this endpoint"}, HTTPStatus.FORBIDDEN
        return decorator
    return wrapper


def is_student_or_admin(student_id):
    current_user = get_current_user()
    claims = get_jwt()
    user_role = claims.get("role")
    student = Student.query.get_or_404(student_id)
    if student == current_user or user_role == "ADMIN":
        return True
    else:
        return False


def is_teacher_or_admin(teacher_id):
    current_user = get_current_user()
    claims = get_jwt()
    user_role = claims.get("role")
    teacher = Teacher.query.get_or_404(teacher_id)
    if teacher == current_user or user_role == "ADMIN":
        return True
    else:
        return False