import re
from functools import wraps
from http import HTTPStatus

from pyisemail import is_email
from pyisemail.diagnosis import ValidDiagnosis

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


def staff_required():
    """
    Decorator to protect endpoints meant for only teachers (staffs).
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role", None)
            if role == "STAFF":
                return fn(*args, **kwargs)
            return {"msg": "Staff access only"}, HTTPStatus.FORBIDDEN
        return decorator
    return wrapper


def is_student_or_admin(student_id):
    """
    Grant access to a student or an admin
    """
    current_user = get_current_user()
    claims = get_jwt()
    user_role = claims.get("role")
    student = Student.query.get_or_404(student_id)
    if student == current_user or user_role == "ADMIN":
        return True
    else:
        return False


def is_teacher_or_admin(teacher_id):
    """
    Grant access to a teacher or an admin
    """
    current_user = get_current_user()
    claims = get_jwt()
    user_role = claims.get("role")
    teacher = Teacher.query.get_or_404(teacher_id)
    if teacher == current_user or user_role == "ADMIN":
        return True
    else:
        return False


def is_valid_school_id(school_id):
    school_id_regex = r'^ALT\/[A-Z]+(?:\d{6})\/(?:2023)$'
    return re.match(school_id_regex, school_id) is not None


def is_valid_email(email):
    is_valid = is_email(email, diagnose=True)
    if isinstance(is_valid, ValidDiagnosis):
        return True
    return is_valid.message
