from http import HTTPStatus

from flask import request
from flask_jwt_extended import jwt_required
from flask_restx import Namespace, Resource, abort, fields, marshal

from . import students, teachers
from ..models.courses import Course
from ..models.students import Student
from ..util import admin_required

course_ns = Namespace("Courses", "The course namespace")

course_model = course_ns.model(
    "Course model",
    {
        "id": fields.Integer(),
        "title": fields.String(required=True),
        "credit_unit": fields.Integer(required=True),
        "code": fields.String(required=True),
        "teacher": fields.Nested(teachers.teacher_model, allow_null=True),
    },
)
course_register_model = course_ns.model(
    "Course register model",
    {
        "course_title": fields.String(required=True),
        "school_id": fields.String(required=True),
    },
)
course_with_enrolled_students = course_model.clone(
    "Course with registered students",
    {"students": fields.Nested(students.student_model, as_list=True)},
)


@course_ns.route("/")
class CourseList(Resource):

    @course_ns.response(200, "Success")
    @admin_required()
    def get(self):
        """
        Get all available courses
        """
        all_courses = Course.query.all()
        return marshal(all_courses, course_model), HTTPStatus.OK

    @course_ns.expect(course_model)
    @course_ns.doc(description="Add a new course")
    @admin_required()
    def post(self):
        """
        Add a new course
        """
        data = course_ns.payload
        title = data["title"]
        credit_unit = data["credit_unit"]
        code = data["code"]
        teacher_id = data.get("teacher_id")

        # Check that a course with the title doesn't already exist and create a new course
        course = Course.query.filter_by(title=title).first()

        if course is not None:
            abort(400, msg=f"Course with title: {title} already exists")

        new_course = Course(
            title=title,
            credit_unit=credit_unit,
            code=code,
            teacher_id=teacher_id
        )
        new_course.save()
        return marshal(new_course, course_model), HTTPStatus.CREATED


@course_ns.route("/<int:course_id>/")
class CourseRetrieveUpdateDelete(Resource):

    @course_ns.doc(
        params={"course_id": "The ID of the course"},
        description="Retrieve a course and all the students enrolled for that course",
    )
    @admin_required()
    def get(self, course_id):
        """
        Retrieve a single course
        """
        course = Course.query.get_or_404(course_id)
        return marshal(course, course_with_enrolled_students), HTTPStatus.OK

    @course_ns.marshal_with(course_model)
    @course_ns.doc(
        description="Update the details of a course",
        params={"course_id": "The ID of the course"},
    )
    @course_ns.expect(course_model)
    @admin_required()
    def put(self, course_id):
        """
        Update a course
        """
        course = Course.query.get_or_404(course_id)
        data = course_ns.payload
        course.title = data.get("title", course.title)
        course.credit_unit = data.get("credit_unit", course.credit_unit)
        course.teacher_id = data.get("teacher_id", course.teacher_id)
        course.commit_update()
        return course, HTTPStatus.OK

    @course_ns.doc(
        params={"course_id": "The ID of the course"},
        description="Delete a course",
    )
    @admin_required()
    def delete(self, course_id):
        """
        Delete a course
        """
        course = Course.query.get_or_404(course_id)
        course.delete()
        return None, HTTPStatus.NO_CONTENT


@course_ns.route("/enroll/")
class CourseRegister(Resource):

    @course_ns.expect(course_register_model)
    @course_ns.response(201, "Created")
    @course_ns.response(400, "Bad request")
    @jwt_required()
    def post(self):
        """
        Register a student for a course
        """
        data = course_ns.payload
        course_title = data["course_title"]
        school_id = data["school_id"]

        student = Student.get_by_school_id(school_id)

        if isinstance(course_title, list):
            for title in course_title:
                course = Course.get_by_title(title)

                # Abort if a student has already registered for the course
                if student in course.students:
                    abort(400, msg=f"This student already enrolled for {course.title}")

                course.students.append(student)
                course.commit_update()

        else:
            course = Course.get_by_title(course_title)

            if student in course.students:
                abort(400, msg=f"This student already enrolled for {course.title}")

            course.students.append(student)
            course.commit_update()

        return (
            {"msg": f"Student: {school_id} has registered for {course_title}"},
            HTTPStatus.CREATED
        )


    @course_ns.expect(course_register_model)
    @course_ns.doc(description="Unregister a student from a course")
    @jwt_required()
    def delete(self):
        """
        Unregister a student from a course
        """
        data = request.get_json()
        course_title = data["course_title"]
        school_id = data["school_id"]

        course = Course.get_by_title(course_title)
        student = Student.get_by_school_id(school_id)

        # Check that student registered for the course before unregistering
        if student not in course.students:
            abort(400, msg="This student did not register for this course")

        course.students.remove(student)
        course.commit_update()
        return {"msg": "Student unregistered."}, HTTPStatus.NO_CONTENT
