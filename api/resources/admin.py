from http import HTTPStatus

from flask import request
from flask_restx import Namespace, Resource, abort, marshal
from flask_jwt_extended import get_current_user

from ..models.users import Admin
from ..serializers.users import admin_model, signup_model, user_input_model
from ..util import admin_required


admin_ns = Namespace("Admin", "Admin operations")
admin_ns.add_model(admin_model.name, admin_model)
admin_ns.add_model(signup_model.name, signup_model)
admin_ns.add_model(user_input_model.name, user_input_model)


@admin_ns.route("/signup")
class AdminSignUp(Resource):

    @admin_ns.expect(signup_model, validate=True)
    def post(self):
        """
        Admin sign up
        """
        data = request.get_json()
        full_name = data["full_name"]
        email_address = data["email_address"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        name = full_name.split()
        if len(name) <= 1:
            abort(400, message="Provide your first name and last name")

        if confirm_password and password == confirm_password:
            new_admin = Admin(full_name, email_address, password_str=password)
            new_admin.save()
            return marshal(new_admin, admin_model), HTTPStatus.CREATED

        else:
            abort(400, message="Invalid password. Check your password and try again")


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


@admin_ns.route("/<int:admin_id>")
class AdminRetrieveUpdateDelete(Resource):

    @admin_ns.doc(
        description="Get an admin by ID",
        params={"admin_id": "The ID of the admin"},
    )
    @admin_required()
    def get(self, admin_id):
        """
        Get an admin
        """
        admin = Admin.query.get_or_404(admin_id)
        current_user = get_current_user()

        if admin != current_user:
            abort(403, message="You don't have access to this resource")

        return marshal(admin, admin_model), HTTPStatus.OK

    @admin_ns.expect(user_input_model)
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
            abort(403, message="You don't have access to this resource")

        data = admin_ns.payload
        admin.full_name = data.get("full_name", admin.full_name)
        admin.email_address = data.get("email_address", admin.email_address)
        admin.commit_update()
        return marshal(admin, admin_model), HTTPStatus.OK

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
            abort(403, message="You don't have access to this resource")

        admin.delete()
        return None, HTTPStatus.NO_CONTENT
