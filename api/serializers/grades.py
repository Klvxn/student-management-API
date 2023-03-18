from flask_restx import Model, fields


grade_model = Model(
    "Grade model",
    {
        "student_id": fields.Integer(),
        "course_id": fields.Integer(),
        "score": fields.Float(),
        "letter_grade": fields.String(),
    },
)

score_input = Model("Score", {"score": fields.Float(required=True)})
