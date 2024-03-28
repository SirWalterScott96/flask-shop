from functools import wraps

from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_user, current_user, login_required, logout_user

from .forms import UserLoginForm, UserRegisterForm
from backend.extensions import db, login_manager
from backend.mail.classes import EmailSender

user = Blueprint('user', __name__, template_folder='../templates/user')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('user.user_login'))


def is_active_user(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_active:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('user.user_dashboard'))

    return wrapper


@user.route('/login', methods=['GET', 'POST'])
@is_active_user
def user_login():
    """login page."""
    form = UserLoginForm()
    if form.validate_on_submit():
        login_user(form.user)
        return redirect(url_for('public.home'))
    return render_template('login.html', form=form)


@user.route('/register', methods=['GET', 'POST'])
@is_active_user
def user_register():
    """Register new user."""
    form = UserRegisterForm()

    if form.validate_on_submit():
        db.session.add(form.user)
        db.session.commit()
        EmailSender.send_confirmation_email(form.email.data)
        flash('A confirmation code has been sent to your email', 'success')
        return redirect(url_for('user.user_login'))
    return render_template('register.html', form=form)


@user.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    return redirect(url_for('public.home'))


@user.route('/settings')
@login_required
def settings():
    return redirect(url_for('user.dashboard', child=settings))


@user.route('/dashboard')
@user.route('/dashboard/<child>')
@login_required
def dashboard(child=None):
    return render_template('dashboard.html')
