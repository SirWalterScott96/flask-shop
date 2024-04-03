from flask import abort
from flask_login import UserMixin, current_user
from sqlalchemy.ext.hybrid import hybrid_property

from backend.extensions import db, bcrypt


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    phone_number = db.Column(db.String(13))
    _password = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean(), default=False)

    orders = db.relationship('Orders', backref='user', lazy=True)

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

    @staticmethod
    def get_user(id):
        return User.query.filter_by(id=id).first()

    def __str__(self):
        return self.username


class Account:

    def __init__(self):
        self.name: str = ''
        self.phone_number: str = ''
        self.new_password: str = ''

    def account_details_validation(self, data: dict):
        if len(data) == 0:
            abort(400)
        if 'name' in data:
            self.name = data['name']
        if 'phone_number' in data and 12 <= len(data['phone_number']) <= 13 and '.' not in data['phone_number']:
            self.phone_number = self.correction_phone_number(data['phone_number'])
        else:
            abort(400)

        return True

    def new_password_validation(self, data: dict, user_id):
        if len(data) == 0:
            abort(400)
        if 'new_password' not in data and 'current_password' not in data:
            abort(400)
        user = User.query.get_or_404(user_id)
        if user and user.check_password(data['current_password']):
            print(1)
            self.new_password = data['new_password']
            return True
        else:
            abort(400)

    def correction_phone_number(self, phone: str):
        phone_number_to_check: str = ''
        if phone.startswith("+"):
            phone_number_to_check = phone[1:]
        else:
            phone_number_to_check = phone
        return phone_number_to_check


class SaveProperties:
    def __init__(self, user_id):
        self.user = User.query.get_or_404(user_id)

    def set_new_account_details(self, **kwargs):
        if self.user:
            for key, value in kwargs.items():
                setattr(self.user, key, value)
            db.session.commit()

    def set_new_password(self, new_password: str):
        if self.user:
            self.user.password = new_password
            db.session.commit()
