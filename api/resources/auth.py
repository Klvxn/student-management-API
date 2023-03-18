from http import HTTPStatus

from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_jwt,
    jwt_required
)
from flask_restx import Namespace, Resource, abort
from werkzeug.security import check_password_hash, generate_password_hash

from ..models.students import Student
from ..models.teachers import Teacher
from ..models.users import Admin
from ..serializers.auth import  login_model, new_password_input
from ..util import BLOCKLIST


auth_ns = Namespace("Authentication", "Authentication related operations")
auth_ns.add_model(login_model.name, login_model)
auth_ns.add_model(new_password_input.name, new_password_input)


@auth_ns.route("/login")
class Login(Resource):

    @auth_ns.expect(login_model, validate=True)
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
            abort(400, message="Provide a school ID or email address")

        # Get the student if the school ID was provided
        if school_id:
            user = Student.get_by_school_id(school_id)

        # Check if the email provided belongs to an admin or teacher
        else:
            admin = Admin.query.filter_by(email_address=email_address).first()
            teacher = Teacher.query.filter_by(email_address=email_address).first()

            # Return 404 if no teacher or admin with the email address exists
            if not (admin or teacher):
                abort(404, message=f"User with email address: {email_address} not found")

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
        abort(400, message="Invalid credentials")


@auth_ns.route("/token/refresh")
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


@auth_ns.route("/change-password")
class PasswordChange(Resource):
    """
    Change default password to user password
    """
    @auth_ns.expect(new_password_input, validate=True)
    @jwt_required()
    def post(self):

        data = request.get_json()
        new_password = data["new_password"]
        current_user = get_current_user()
        current_user.password_hash = generate_password_hash(new_password)
        current_user.commit_update()
        msg = {"message": "Password changed successfully"}
        return msg, HTTPStatus.ACCEPTED


@auth_ns.route("/logout")
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
        return {"message": "Token revoked"}, HTTPStatus.OK
