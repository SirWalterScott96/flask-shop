from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from backend.extensions import db, bcrypt


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    _password = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean(), default=False)

    def __init__(self, name, username, email, password, **kwargs):
        super().__init__(name=name, username=username, email=email, password=password, **kwargs)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value).decode('UTF-8')

    def check_password(self, value):
        return bcrypt.check_password_hash(self._password.encode('UTF-8'), value)

    @staticmethod
    def is_user_exist_by_email(email):
        return User.query.filter_by(email=email).first()

    def __str__(self):
        return self.username
