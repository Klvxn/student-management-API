from http import HTTPStatus

from flask import request
from flask_jwt_extended import get_current_user
from flask_restx import Namespace, Resource, abort, marshal
from sqlalchemy import exc

from ..models.courses import Course
from ..models.grades import Grade
from ..models.students import Student
from ..serializers.grades import grade_model, score_input
from ..util import staff_required, staff_or_admin_required


grade_ns = Namespace("Grade system", "Everything about grading")
grade_ns.add_model(grade_model.name, grade_model)
grade_ns.add_model(score_input.name, score_input)


@grade_ns.route("/<int:student_id>/<int:course_id>")
class GradeRetrieveUpdate(Resource):

    @grade_ns.doc(
        description="Get a student's grade in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_or_admin_required()
    def get(self, student_id, course_id):
        """
        Get a student's grade in a course
        """
        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if current_user != course.teacher or current_user.role != "ADMIN":
            abort (403, message="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        return marshal(grade, grade_model), HTTPStatus.OK

    @grade_ns.expect(score_input, validate=True)
    @grade_ns.doc(
        description="Grade a student in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_required()
    def post(self, student_id, course_id):
        """
        Grade a student in a course
        """
        data = request.get_json()
        score = data["score"]

        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)

        course_teacher = course.teacher
        current_user = get_current_user()

        if course_teacher != current_user:
            abort(403, message="Only the course teacher can perform this action")

        error_msg = None

        # Check that the student is registered to the course before grading
        if student not in course.students:
            error_msg = "This student did not register for this course"

        try:
            grade = Grade(student_id=student_id, course_id=course_id, score=score)
            grade.allocate_letter_grade()
            grade.save()
            return marshal(grade, grade_model), HTTPStatus.CREATED

        except exc.IntegrityError:
            error_msg = "This student has already been graded"

        abort(400, message=error_msg)

    @grade_ns.expect(score_input)
    @grade_ns.doc(
        description="Update a student's grade in a particular course",
        params={
            "student_id": "The ID of the student",
            "course_id": "The ID of the course",
        },
    )
    @staff_required()
    def put(self, student_id, course_id):
        """
        Update a student's grade in a course
        """
        data = grade_ns.payload

        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if course.teacher != current_user:
            abort(403, message="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        grade.score = data.get("score", grade.score)
        grade.allocate_letter_grade()
        grade.commit_update()
        return marshal(grade, grade_model), HTTPStatus.OK

    @staff_required()
    def delete(self, student_id, course_id):
        """
        Delete a student's grade in a course
        """
        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if course.teacher != current_user:
            abort(403, message="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        grade.delete()
        return None, HTTPStatus.NO_CONTENT