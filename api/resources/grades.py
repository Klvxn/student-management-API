from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_current_user
from flask_restx import Namespace, Resource, abort, fields, marshal
from sqlalchemy import exc

from ..models.courses import Course
from ..models.grades import Grade
from ..models.students import Student
from ..util import staff_only

grade_ns = Namespace("Grade system", "Everything about grading")

grade_serializer = grade_ns.model(
    "Grade serializer",
    {
        "student_id": fields.Integer(),
        "student_full_name": fields.String(attribute="student.full_name"),
        "course_title": fields.String(attribute="course.title"),
        "score": fields.Float(required=True),
        "letter_grade": fields.String(),
    },
)
score_input = grade_ns.model("Score", {"score": fields.Float(required=True)})


@grade_ns.route("/<int:student_id>/<int:course_id>/")
class GradeRetrieveUpdate(Resource):

    @grade_ns.response(200, "Success")
    @grade_ns.doc(
        description="Get a student's grade in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_only()
    def get(self, student_id, course_id):
        """
        Get a student's grade in a course
        """
        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if course.teacher != current_user.teacher:
            abort (403, msg="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        return marshal(grade, grade_serializer), HTTPStatus.OK

    @grade_ns.expect(score_input)
    @grade_ns.response(201, "Created")
    @grade_ns.response(400, "Bad request")
    @grade_ns.response(403, "Forbidden")
    @grade_ns.doc(
        description="Grade a student in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_only()
    def post(self, student_id, course_id):
        """
        Grade a student in a course
        """
        data = request.get_json()
        score = data["score"]

        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)

        # Only the course's teacher is allowed to grade a student for the course
        course_teacher = course.teacher
        current_user = get_current_user()


        if course_teacher != current_user.teacher:
            abort(403, "Only the course teacher can perform this action")

        error_msg = None

        # Check that the student is registered to the course before grading
        if student not in course.students:
            error_msg = "This student did not register for this course"

        # Try to catch any database error in case the student has already been graded
        try:
            grade = Grade(student=student, course=course, score=score)
            grade.allocate_letter_grade()
            grade.save()
            response = {
                "course_title": course.title,
                "student_full_name": student.full_name,
                "score": score,
            }
            return response, HTTPStatus.CREATED

        except exc.IntegrityError:
            error_msg = "This user has already been graded"

        abort(400, msg=error_msg)

    @grade_ns.expect(grade_serializer)
    @grade_ns.response(200, "Success")
    @grade_ns.doc(
        description="Update a student's grade in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_only()
    def put(self, student_id, course_id):
        """
        Update a student's grade in a course
        """
        data = grade_ns.payload

        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if course.teacher != current_user.teacher:
            abort(403, msg="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        grade.score = data.get("score", grade.score)
        grade.allocate_letter_grade()
        grade.commit_update()
        return marshal(grade, grade_serializer), HTTPStatus.OK
