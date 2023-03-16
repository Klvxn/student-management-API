from http import HTTPStatus

from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_jwt,
    jwt_required
)
from flask_restx import Namespace, Resource, abort, fields
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.students import Student
from ..models.teachers import Teacher
from ..models.users import Admin
from ..util import BLOCKLIST

auth_ns = Namespace("Authentication", "Authentication related operations")

login = auth_ns.model(
    "Login serializer",
    {
        "school_id": fields.String(),
        "email_address": fields.String(),
        "password": fields.String(),
    },
)
new_password = auth_ns.model("New password", {"new_password": fields.String()})


@auth_ns.route("/login/")
class Login(Resource):

    @auth_ns.expect(login)
    @auth_ns.doc(description="Create an access token and a refresh token")
    def post(self):
        """
        Create an access and refresh token
        """
        data = request.get_json()

        school_id = data.get("school_id")
        email_address = data.get("email_address")
        password = data["password"]

        # Ensure that either an email address (admin/teachers) or school ID(student) is provided
        if not (school_id or email_address):
            abort(400, msg="Provide a school ID or email address")

        # Get the student if the school ID was provided
        if school_id:
            user = Student.get_by_school_id(school_id)

        # Check if the email provided belongs to an admin or teacher
        else:
            admin = Admin.query.filter_by(email_address=email_address).first()
            teacher = Teacher.query.filter_by(email_address=email_address).first()

            # Return 404 if no teacher or admin with the email address exists
            if not (admin or teacher):
                abort(404, msg=f"User with email address: {email_address} not found")

            user = teacher if teacher else admin

        # Check the user against the provided password and create access and refresh tokens
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(
                identity=user.id, additional_claims={"role": user.role}
            )
            refresh_token = create_refresh_token(
                identity=user.id, additional_claims={"role": user.role}
            )
            response = {
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            return response, HTTPStatus.OK

        # Return error message if the wrong password was provided
        abort(400, msg="Invalid credentials")


@auth_ns.route("/token/refresh/")
class TokenRefresh(Resource):

    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh an expired access token
        """
        current_user = get_current_user()
        access_token = create_access_token(
            identity=current_user.id, additional_claims={"role": current_user.role}
        )
        response = {"access_token": access_token}
        return response, HTTPStatus.CREATED


@auth_ns.route("/change-password/")
class PasswordChange(Resource):

    @auth_ns.expect(new_password)
    @jwt_required()
    def post(self):

        data = request.get_json()
        new_password = data["new_password"]
        current_user = get_current_user()
        current_user.password_hash = generate_password_hash(new_password)
        msg = {"msg": "Password changed successfully"}
        return msg, HTTPStatus.ACCEPTED


@auth_ns.route("/logout/")
class Logout(Resource):

    @jwt_required(verify_type=False)
    def post(self):
        """
        Log out and revoke refresh token
        """
        token = get_jwt()
        jti = token["jti"]
        token_type = token["type"]
        BLOCKLIST.add(jti)
        return {"msg": "Token revoked"}, HTTPStatus.OK
