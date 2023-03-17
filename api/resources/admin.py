from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, abort, fields, marshal
from flask_jwt_extended import get_current_user, jwt_required

from ..models.users import Admin
from ..util import admin_required

admin_ns = Namespace("Admin", "Admin operations")

admin_model = admin_ns.model(
    "Admin serializer",
    {
        "id": fields.Integer(),
        "full_name": fields.String(required=True),
        "email_address": fields.String(required=True),
    },
)
signup_model = admin_ns.model(
    "Sign Up serializer",
    {
        "email_address": fields.String(),
        "full_name": fields.String(required=True),
        "password": fields.String(write_only=True),
        "confirm_password": fields.String(write_only=True),
    },
)


@admin_ns.route("/signup/")
class AdminSignUp(Resource):

    @admin_ns.expect(signup_model)
    def post(self):
        """
        Admin sign up
        """
        data = request.get_json()
        full_name = data["full_name"]
        email_address = data["email_address"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        if confirm_password and password == confirm_password:
            new_admin = Admin(full_name, email_address, password_str=password)
            new_admin.save()
            return marshal(new_admin, admin_model), HTTPStatus.CREATED

        abort(400, msg="Invalid password. Check your password and try again")


@admin_ns.route("/")
class AdminList(Resource):

    @admin_ns.doc(description="Get all admins")
    @admin_required()
    def get(self):
        """
        Get all admin users
        """
        admins = Admin.query.all()
        return marshal(admins, admin_model), HTTPStatus.OK


@admin_ns.route("/<int:admin_id>/")
class AdminRetrieveUpdateDelete(Resource):

    @admin_ns.doc(
        description="Get an admin by ID",
        params={"admin_id": "The ID of the admin"},
    )
    @jwt_required()
    def get(self, admin_id):
        """
        Get an admin
        """
        admin = Admin.query.get_or_404(admin_id)
        current_user = get_current_user()

        if admin != current_user:
            abort(403, msg="You don't have access to this resource")

        return marshal(admin, admin_model), HTTPStatus.OK

    @admin_ns.marshal_with(admin_model)
    @admin_ns.expect(admin_model)
    @admin_ns.doc(
        description="Update an admin", params={"admin_id": "The ID of the admin"}
    )
    @admin_required()
    def put(self, admin_id):
        """
        Update an admin
        """
        admin = Admin.query.get_or_404(admin_id)
        current_user = get_current_user()

        if admin != current_user:
            abort(403, msg="You don't have access to this resource")

        data = admin_ns.payload
        admin.full_name = data.get("full_name", admin.full_name)
        admin.email_address = data.get("email_address", admin.email_address)
        admin.commit_update()
        return admin, HTTPStatus.OK

    @admin_ns.doc(
        description="Delete an admin", params={"admin_id": "The ID of the admin"}
    )
    @admin_required()
    def delete(self, admin_id):
        """
        Delete an admin
        """
        admin = Admin.query.get_or_404(admin_id)
        current_user = get_current_user()

        if admin != current_user:
            abort(403, msg="You don't have access to this resource")

        admin.delete()
        return None, HTTPStatus.NO_CONTENT
