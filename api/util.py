from functools import wraps
from http import HTTPStatus

from flask_jwt_extended import get_jwt, verify_jwt_in_request

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
            if claims.get("ADMIN", None):
                return fn(*args, **kwargs)
            return {"msg": "Unauthorized access"}, HTTPStatus.FORBIDDEN

        return decorator

    return wrapper


def staff_only():
    """
    Decorator to protect endpoints meant for only teachers.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("TEACHER", None):
                return fn(*args, **kwargs)
            return {"msg": "Only a teacher can access this endpoint"}, HTTPStatus.FORBIDDEN

        return decorator

    return wrapper

