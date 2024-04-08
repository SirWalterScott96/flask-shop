from flask import Blueprint, flash, redirect, url_for, session, g

from .classes import EmailSender

from backend.extensions import db
from backend.user.models import User

email = Blueprint('email', __name__)


@email.route('/resend_confirmation_email/<user_email>', methods=['GET'])
def resend_confirmation_email(user_email):
    EmailSender.send_confirmation_email(user_email)

    flash('A confirmation code has been sent to your email', 'success')
    return redirect(url_for('user.user_login'))


@email.route('/confirm-email/<user_email>/<token>')
def confirm_email(user_email, token):
    user = User.get_user_by_email(user_email)
    if not user:
        flash('no user found', 'danger')
        return redirect(url_for('user.user_login'))

    if not EmailSender.check_confirmation_email(token, salt='email-confirm'):
        return redirect(url_for('user.user_login', user_email=user.email))

    user.email_confirmed = True
    db.session.commit()

    flash('Email is confirmed', 'success')
    return redirect(url_for('user.user_login'))


@email.route('/reset-password/<user_email>/<token>')
def reset_password(user_email, token):
    user = User.get_user_by_email(user_email)
    if not user:
        flash('no user found', 'danger')
        return redirect(url_for('user.user_login'))

    if not EmailSender.check_confirmation_email(token, salt='reset-password'):
        return redirect(url_for('user.user_login', user_email=user.email, salt='reset-password'))

    session['reset_password'] = True
    return redirect(url_for('user.reset_password', token=token, user_email=user_email))
