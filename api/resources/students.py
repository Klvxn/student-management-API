from http import HTTPStatus

from flask_jwt_extended import get_current_user, get_jwt, jwt_required
from flask_restx import Namespace, Resource, abort, fields, marshal
from werkzeug.security import generate_password_hash

from ..models.grades import Grade
from ..models.students import Student
from ..models.users import User
from ..util import admin_required


student_ns = Namespace("Students", "The student namespace")

student_model = student_ns.model(
    "Student model",
    {
        "id": fields.Integer(),
        "school_id": fields.String(read_only=True),
        "full_name": fields.String(required=True),
        "email_address": fields.String(required=True),
        "gpa": fields.Float(read_only=True),
    },
)


@student_ns.route("/")
class StudentListCreate(Resource):

    @student_ns.doc(description="Get all students")
    @admin_required()
    def get(self):
        """
        Get all students
        """
        all_students = Student.query.all()
        return marshal(all_students, student_model), HTTPStatus.OK

    @student_ns.doc(description="Create a new student")
    @student_ns.expect(student_model)
    @student_ns.response(201, "Created")
    @student_ns.response(400, "Bad request")
    @admin_required()
    def post(self):
        """
        Create a new student
        """
        data = student_ns.payload
        email_address = data["email_address"]
        full_name = data["full_name"]
        name = full_name.split()

        error_msg = None

        if len(name) <= 1:
            error_msg = "Provide your first name and last name"

        # Check if a student with the email address already exists.
        student = Student.query.filter_by(email_address=email_address).first()
        if student is not None:
            error_msg = f"Student with email address: {email_address} already exists"

        # Create a new student and set a default password if no error message else abort
        if error_msg:
            abort(400, msg=error_msg)

        user = User()
        new_student = Student(full_name=full_name, email_address=email_address)
        user.student = new_student
        default_password = "password123"
        user.password_hash = generate_password_hash(default_password)
        user.role = "STUDENT"
        user.save()
        new_student.save()
        return marshal(new_student, student_model), HTTPStatus.CREATED



@student_ns.route("/<int:student_id>/")
class StudentRetrieveUpdateDelete(Resource):

    @student_ns.doc(
        description="Retrieve a student by ID",
        params={"student_id": "The ID of the student"},
    )
    @jwt_required()
    def get(self, student_id):
        """
        Retrieve a student
        """
        claims = get_jwt()
        student = Student.query.get_or_404(student_id)
        current_user = get_current_user()

        # Allow access to the student or the admin
        if student.user == current_user or claims.get("ADMIN"):
            return marshal(student, student_model), HTTPStatus.OK

        abort(403, msg="You don't access to this resource")

    @student_ns.marshal_with(student_model)
    @student_ns.expect(student_model)
    @student_ns.doc(
        description="Update a student's details",
        params={"student_id": "The ID of the student"},
    )
    @admin_required()
    def put(self, student_id):
        """
        Update a student's details
        """
        student = Student.query.get_or_404(student_id)
        data = student_ns.payload
        student.full_name = data.get("full_name", student.full_name)
        student.email_address = data.get("email_address", student.email_address)
        student.commit_update()
        return student, HTTPStatus.OK

    @student_ns.doc(
        description="Delete a student", params={"student_id": "The ID of the student"}
    )
    @admin_required()
    def delete(self, student_id):
        """
        Delete a student
        """
        student = Student.query.get_or_404(student_id)
        student.delete()
        return None, HTTPStatus.NO_CONTENT


@student_ns.route("/<int:student_id>/courses/")
class StudentCoursesRetrieve(Resource):

    @student_ns.doc(
        description="Get a student's registered courses",
        params={"student_id": "The ID of the student"},
    )
    @student_ns.response(200, "Success")
    @jwt_required()
    def get(self, student_id):
        """
        Get a student's registered courses
        """
        claims = get_jwt()

        # Allow access to the student or admin only
        student = Student.query.get_or_404(student_id)
        current_user = get_current_user()

        if student.user == current_user or claims.get("ADMIN"):
            data = {
                "student": student.full_name,
                "enrolled_courses": [
                    course.title for course in student.courses if student.courses
                ],
            }
            return data, HTTPStatus.OK

        abort (403, msg="You don't access to this resource")


@student_ns.route("/<int:student_id>/result/")
class StudentResultRetrieve(Resource):

    @student_ns.response(200, "Success")
    @student_ns.doc(
        description="Get a student's grade in all courses and their GPA",
        params={"student_id": "The ID of the student"},
    )
    @jwt_required()
    def get(self, student_id):
        """
        Get a student's result
        """
        claims = get_jwt()
        student = Student.query.get_or_404(student_id)
        current_user = get_current_user()

        # Allow access to the student or admin
        if student.user == current_user or claims.get("ADMIN"):
            results = {}
            course_results = []

            for course in student.courses:
                grade = Grade.query.get((student.id, course.id))
                result = {"course_title": course.title, "grade": grade.letter_grade}
                course_results.append(result)

            results["course_results"] = course_results
            results["GPA"] = student.calculate_student_gpa()

            return {"result": results}, HTTPStatus.OK

        abort (403, msg="You don't access to this resource")
