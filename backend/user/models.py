from flask_login import UserMixin
from backend.extensions import db, bcrypt
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    password = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean(), default=False)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    def __str__(self):
        return self.username
