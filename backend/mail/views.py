from flask import Blueprint, flash, redirect, url_for

from .classes import EmailSender

from backend.extensions import db
from backend.user.models import User

email = Blueprint('email', __name__)


@email.route('/resend_confirmation_email/<user_email>', methods=['POST'])
def resend_confirmation_email(user_email):
    EmailSender.send_confirmation_email(user_email)

    flash('A confirmation code has been sent to your email', 'success')
    return redirect(url_for('user.user_login'))


@email.route('/confirm-email/<user_email>/<token>')
def confirm_email(user_email, token):
    user = User.is_user_exist_by_email(user_email)
    if not user:
        flash('no user found', 'danger')
        return redirect(url_for('user.user_login'))

    if not EmailSender.check_confirmation_email(token):
        return redirect(url_for('user.user_login', user_email=user.email))

    user.email_confirmed = True
    db.session.commit()

    flash('Email is confirmed', 'success')
    return redirect(url_for('user.user_login'))
