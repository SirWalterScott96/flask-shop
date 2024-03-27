from flask import url_for, flash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

from backend.settings import Config
from backend.extensions import mail


class EmailSender:
    _instance = None
    serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def send_confirmation_email(cls, user_email):
        print(user_email)
        subject = 'Confirm Your Registration'
        token = cls.serializer.dumps(user_email, salt='email-confirm')
        confirmation_url = url_for('email.confirm_email', user_email=user_email, token=token, _external=True)
        message_body = f'Click the following link to confirm your registration: ' \
                       f'{confirmation_url}'
        msg = Message(subject=subject, recipients=[user_email], body=message_body)
        mail.send(msg)

    @classmethod
    def check_confirmation_email(cls, token):
        try:
            cls.serializer.loads(token, salt='email-confirm', max_age=3600)
            return True
        except SignatureExpired:
            flash('Expired token', 'danger')
            return False
        except BadSignature:
            flash('Invalid token', 'danger')
            return False
