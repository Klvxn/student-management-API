from http import HTTPStatus

from flask_jwt_extended import get_current_user, jwt_required
from flask_restx import Namespace, Resource, abort, marshal

from ..models.courses import Course
from ..models.grades import Grade
from ..models.students import Student
from ..serializers.grades import grade_model, score_input
from ..util import staff_required


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
    @jwt_required()
    def get(self, student_id, course_id):
        """
        Get a student's grade in a course
        """
        course = Course.query.get_or_404(course_id)
        current_user = get_current_user()

        if (course.teacher == current_user) or (current_user.role == "ADMIN"):
            grade = Grade.query.get_or_404((student_id, course_id))
            return marshal(grade, grade_model), HTTPStatus.OK

        else:
            grade_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort (403, message="Only the course teacher can perform this action.vv")

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
        data = grade_ns.payload
        score = data["score"]

        student = Student.query.get_or_404(student_id)
        course = Course.query.get_or_404(course_id)

        current_user = get_current_user()

        if course.teacher != current_user:
            grade_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort(403, message="Only the course teacher can perform this action")

        # Check that the student is registered to the course before grading
        if student not in course.students:
            abort(400, message="This student did not register for this course")

        try:
            grade = Grade(student_id=student_id, course_id=course_id, score=score)
            grade.allocate_letter_grade()
            grade.save()
            student.calculate_student_gpa()
            grade_ns.logger.info("Grading student")
            return marshal(grade, grade_model), HTTPStatus.CREATED

        except Exception as e:
            grade_ns.logger.error(e)
            abort(500, message="This student might have already been graded")

    @grade_ns.expect(score_input, validate=True)
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
        student = Student.query.get_or_404(student_id)
        current_user = get_current_user()

        if course.teacher != current_user:
            grade_ns.logger.warn(f"Unauthorized access: {current_user}")
            abort(403, message="Only the course teacher can perform this action")

        grade = Grade.query.get_or_404((student_id, course_id))
        grade.score = data.get("score", grade.score)
        grade.allocate_letter_grade()
        student.calculate_student_gpa()
        grade.commit_update()
        return marshal(grade, grade_model), HTTPStatus.OK
