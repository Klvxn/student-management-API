from flask_restx import Model, fields


user_input_model = Model(
    "User Input Model",
    {
        "full_name": fields.String(required=True),
        "email_address": fields.String(required=True),
    },
)

user_output_model = Model(
    "User output model",
    {
        "id": fields.Integer(),
        "full_name": fields.String(),
        "email_address": fields.String(),
        "role": fields.String(),
    },
)

signup_model = Model(
    "Sign up model",
    {
        "email_address": fields.String(required=True),
        "full_name": fields.String(required=True),
        "password": fields.String(write_only=True),
        "confirm_password": fields.String(write_only=True),
    },
)

admin_model = user_output_model.clone("Admin model")

student_model = user_output_model.clone(
    "Student model",
    {
        "school_id": fields.String(),
        "gpa": fields.Float(),
    },
)

teacher_model = user_output_model.clone("Teacher model")
