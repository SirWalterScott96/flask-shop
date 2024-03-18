# -*- coding: utf-8 -*-
"""User forms."""
from flask import flash
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, EmailField, BooleanField
from wtforms.validators import DataRequired

from .models import User


class UserLoginForm(FlaskForm):
    """Login form."""

    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember = BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(UserLoginForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        user_to_validate = User.query.filter_by(username=self.username.data).first()

        if not user_to_validate:
            flash('incorrect username', 'danger')
            return False
        if not user_to_validate.check_password(self.password.data):
            flash('incorrect password', 'danger')
            return False
        if not user_to_validate.email_confirmed:
            flash('Confirm your email', 'danger')
            return False

        self.user = user_to_validate
        return True


class UserRegisterForm(FlaskForm):
    """Register form."""

    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])
