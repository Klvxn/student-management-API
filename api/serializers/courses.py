from flask_restx import Model, fields

from ..serializers import users


course_input_model = Model(
    "Course Input Model",
    {
        "title": fields.String(required=True),
        "course_code": fields.String(required=True),
        "credit_unit": fields.Integer(required=True),
        "teacher_id": fields.Integer(required=False),
    },
)

course_output_model = Model(
    "Course Output Model",
    {
        "id": fields.Integer(),
        "title": fields.String(),
        "course_code": fields.String(),
        "credit_unit": fields.Integer(),
        "teacher": fields.Nested(users.teacher_model, allow_null=True),
    },
)

course_students_model = course_output_model.clone(
    "Course with registered students",
    {"students": fields.Nested(users.student_model, as_list=True)},
)

course_register_model = Model(
    "Course Register Model",
    {
        "course_title": fields.String(required=True),
        "school_id": fields.String(required=True),
    },
)
