from http import HTTPStatus

from flask_restx import Namespace, Resource, abort, fields, marshal
from flask_jwt_extended import jwt_required

from ..models.users import Admin
from ..util import admin_required, is_teacher_or_admin

admin_ns = Namespace("Admin", "Admin operations")

admin_model = admin_ns.model(
    "Admin serializer",
    {
        "id": fields.Integer(),
        "full_name": fields.String(required=True),
        "email_address": fields.String(required=True),
    },
)


@admin_ns.route("/")
class AdminList(Resource):

    @admin_ns.doc(description="Get all admins")
    @admin_ns.response(200, "Success")
    @admin_required()
    def get(self):
        """
        Get all teachers
        """
        all_teachers = Admin.query.all()
        return marshal(all_teachers, admin_model), HTTPStatus.OK


@admin_ns.route("/<int:admin_id>/")
class AdminRetrieveUpdateDelete(Resource):

    @admin_ns.doc(
        description="Get an admin by ID",
        params={"admin_id": "The ID of the admin"},
    )
    @jwt_required()
    def get(self, admin_id):
        """
        Retrieve a teacher
        """
        admin = Admin.query.get_or_404(admin_id)

        # Grant access to teacher or admin
        if not is_teacher_or_admin(admin_id):
            abort(403, msg="You don't have access to this resource")

        return marshal(admin, admin_model), HTTPStatus.OK

    @admin_ns.marshal_with(admin_model)
    @admin_ns.expect(admin_model)
    @admin_ns.doc(
        description="Update an admin", params={"teacher_id": "The ID of the admin"}
    )
    @admin_required()
    def put(self, admin_id):
        """
        Update a teacher
        """
        admin = Admin.query.get_or_404(admin_id)
        data = admin_ns.payload
        admin.full_name = data.get("full_name", admin.full_name)
        admin.email_address = data.get("email_address", admin.email_address)
        admin.commit_update()
        return admin, HTTPStatus.OK

    @admin_ns.response(204, "No content")
    @admin_ns.doc(
        description="Delete an admin", params={"admin_id": "The ID of the admin"}
    )
    @admin_required()
    def delete(self, admin_id):
        """
        Delete a teacher
        """
        admin = Admin.query.get_or_404(admin_id)
        admin.delete()
        return None, HTTPStatus.NO_CONTENT
