from api.database import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    password_hash = db.Column(db.String(), nullable=False)
    role = db.Column(db.String(), nullable=False)

    admin_id = db.Column(db.Integer, db.ForeignKey("admin.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"))

    def __repr__(self):
        return f"<User: {self.id} - {self.role}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Admin(db.Model):

    id = db.Column(db.Integer, primary_key=True, unique=True)
    email_address = db.Column(db.String(), unique=True, nullable=False)

    # one-to-one relationship with the user model
    user = db.relationship("User", backref="admin", uselist=False)

    def __repr__(self):
        return f"<Admin: {self.email_address}>"

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def commit_update():
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
