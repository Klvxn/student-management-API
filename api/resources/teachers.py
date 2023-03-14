from http import HTTPStatus

from flask_restx import Namespace, Resource, abort, fields, marshal
from flask_jwt_extended import current_user, get_jwt, jwt_required
from werkzeug.security import generate_password_hash

from ..models.teachers import Teacher
from ..models.users import User
from ..util import admin_required

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
    @teacher_ns.response(200, "Successful")
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

        # Check if a teacher with the email address already exists
        teacher = Teacher.query.filter_by(email_address=email_address).first()
        if teacher is not None:
            error_msg = f"Teacher with email address: {email_address} already exists"

        # abort if there's error message else create a new teacher with a default password
        if error_msg:
            abort(400, msg=error_msg)

        user = User()
        new_teacher = Teacher(full_name=full_name, email_address=email_address)
        user.teacher = new_teacher
        default_password = "teacherpassword123"
        user.password_hash = generate_password_hash(default_password)
        user.role = "TEACHER"
        user.save()
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
        claims = get_jwt()
        teacher = Teacher.query.get_or_404(teacher_id)

        # Grant access to teacher or admin
        if current_user == teacher.user or claims.get("ADMIN"):
            return marshal(teacher, teacher_model), HTTPStatus.OK

        abort(403, msg="You don't have access to this resource")

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
        teacher = Teacher.query.get_or_404(teacher_id)
        data = teacher_ns.payload
        teacher.full_name = data.get("full_name", teacher.full_name)
        teacher.email_address = data.get("email_address", teacher.email_address)
        teacher.commit_update()
        return teacher, HTTPStatus.OK

    @teacher_ns.response(204, "No content")
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
