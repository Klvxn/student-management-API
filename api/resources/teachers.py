from http import HTTPStatus

from flask_restx import Namespace, Resource, abort, fields, marshal
from flask_jwt_extended import jwt_required

from ..models.teachers import Teacher
from ..util import admin_required, is_teacher_or_admin

teacher_ns = Namespace("Teachers", "The teacher namespace")

teacher_model = teacher_ns.model(
    "Teacher serializer",
    {
        "id": fields.Integer(),
        "full_name": fields.String(required=True),
        "email_address": fields.String(required=True),
    },
)


@teacher_ns.route("/")
class TeacherListCreate(Resource):

    @teacher_ns.doc(description="Get all teachers")
    @admin_required()
    def get(self):
        """
        Get all teachers
        """
        all_teachers = Teacher.query.all()
        return marshal(all_teachers, teacher_model), HTTPStatus.OK

    @teacher_ns.expect(teacher_model)
    @teacher_ns.doc(description="Create a teacher")
    @admin_required()
    def post(self):
        """
        Create a new teacher
        """
        error_msg = None
        data = teacher_ns.payload
        full_name = data["full_name"]
        email_address = data["email_address"]

        name = full_name.split()
        if len(name) <= 1:
            error_msg = "Provide your first name and last name"

        teacher = Teacher.query.filter_by(email_address=email_address).first()
        if teacher is not None:
            error_msg = f"Teacher with email address: {email_address} already exists"

        if error_msg:
            abort(400, msg=error_msg)

        default_password = "teacherpassword123"
        new_teacher = Teacher(full_name, email_address, default_password)
        new_teacher.save()
        return marshal(new_teacher, teacher_model), HTTPStatus.CREATED


@teacher_ns.route("/<int:teacher_id>/")
class TeacherRetrieveUpdateDelete(Resource):

    @teacher_ns.doc(
        description="Get a single teacher by ID",
        params={"teacher_id": "The ID of the teacher"},
    )
    @jwt_required()
    def get(self, teacher_id):
        """
        Retrieve a teacher
        """
        teacher = Teacher.query.get_or_404(teacher_id)

        # Grant access to teacher or admin
        if not is_teacher_or_admin(teacher_id):
            abort(403, msg="You don't have access to this resource")

        return marshal(teacher, teacher_model), HTTPStatus.OK

    @teacher_ns.marshal_with(teacher_model)
    @teacher_ns.expect(teacher_model)
    @teacher_ns.doc(
        description="Update a teacher", params={"teacher_id": "The ID of the teacher"}
    )
    @admin_required()
    def put(self, teacher_id):
        """
        Update a teacher
        """
        data = teacher_ns.payload
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.full_name = data.get("full_name", teacher.full_name)
        teacher.email_address = data.get("email_address", teacher.email_address)
        teacher.commit_update()
        return teacher, HTTPStatus.OK

    @teacher_ns.doc(
        description="Delete a teacher", params={"teacher_id": "The ID of the teacher"}
    )
    @admin_required()
    def delete(self, teacher_id):
        """
        Delete a teacher
        """
        teacher = Teacher.query.get_or_404(teacher_id)
        teacher.delete()
        return None, HTTPStatus.NO_CONTENT
