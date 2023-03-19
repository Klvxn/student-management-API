from http import HTTPStatus

from flask_restx import Namespace, Resource, abort, marshal
from flask_jwt_extended import get_current_user

from ..models.users import Admin
from ..serializers.users import admin_model, signup_model, user_input_model
from ..util import admin_required, is_valid_email

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
        data = admin_ns.payload
        full_name = data["full_name"]
        email_address = data["email_address"]
        password = data["password"]
        confirm_password = data["confirm_password"]

        valid = is_valid_email(email_address)
        if valid != True:
            abort(400, message=f"Invalid Email address: {valid}")

        error_msg = None

        name = full_name.split()
        if len(name) <= 1:
            error_msg = "Provide your first name and last name"

        if password != confirm_password:
            error_msg = "Invalid password. Check your password and try again"

        if error_msg:
            abort(400, error_msg)

        new_admin = Admin(full_name, email_address, password_str=password)
        new_admin.save()
        admin_ns.logger.info(f"Created new Admin: {new_admin}")
        return marshal(new_admin, admin_model), HTTPStatus.CREATED


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
            admin_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort(403, message="You don't have rights to access this resource")

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
        data = admin_ns.payload

        admin = Admin.query.get_or_404(admin_id)
        current_user = get_current_user()

        if admin != current_user:
            admin_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort(403, message="You don't have rights to access this resource")

        valid = is_valid_email(data.get("email_address"))
        if valid != True:
            abort(400, message=f"Invalid Email address: {valid}")

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
            admin_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort(403, message="You don't have rights to access this resource")

        admin.delete()
        return None, HTTPStatus.NO_CONTENT
