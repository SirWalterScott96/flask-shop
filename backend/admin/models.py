from flask_login import UserMixin
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

from backend.extensions import db, bcrypt


class Admin(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True, default=str(uuid.uuid4()), unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    _password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20))

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = bcrypt.generate_password_hash(value).decode("UTF-8")

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self.password.encode('UTF-8'), value)

    @staticmethod
    def does_exist_admin():
        is_admin_exist = Admin.query.filter_by(role='admin').all()
        return is_admin_exist

    @staticmethod
    def create_admin(name: str, username: str, password_local: str):
        new_admin = Admin(name=name,
                          username=username,
                          password=password_local,
                          role='admin')

        db.session.add(new_admin)
        db.session.commit()

    def __str__(self):
        return self.username
