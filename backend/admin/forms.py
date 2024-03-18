# -*- coding: utf-8 -*-
"""Admin forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SelectField
from wtforms.validators import DataRequired

from .models import Admin


class AdminRegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    role = SelectField(choices=['admin', 'administrator'])


class AdminLoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(AdminLoginForm, self).__init__(*args, **kwargs)
        self.admin = None

    def validate(self, extra_validators=None):
        """Validate the form."""
        initial_validation = super(AdminLoginForm, self).validate(extra_validators)
        if not initial_validation:
            return False

        admin_to_validate = Admin.query.filter_by(username=self.username.data).first()

        if not admin_to_validate:
            return False

        if not admin_to_validate.check_password(self.password.data):
            return False

        self.admin = admin_to_validate
        return True
