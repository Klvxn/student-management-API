from flask_restx import Model, fields

login_model = Model(
    "Login model",
    {
        "school_id": fields.String(),
        "email_address": fields.String(),
        "password": fields.String(required=True),
    },
)
new_password_input = Model("New password", {"new_password": fields.String(required=True)})
