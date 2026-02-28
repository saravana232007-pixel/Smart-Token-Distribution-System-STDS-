import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    dept = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    token = db.Column(db.String(6), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dept": self.dept,
            "phone": self.phone,
            "token": self.token,
        }
