from functools import wraps

from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_user, current_user, login_required

from .forms import UserLoginForm, UserRegisterForm
from .models import User

user = Blueprint('user', __name__, template_folder='../templates/user')


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


@user.route('/register')
@is_active_user
def user_register():
    """Register new user."""
    form = UserRegisterForm()

    if form.validate_on_submit():
        # TODO realize if username, write that username is used, ajax
        new_user = User(name=form.name.data,
                        username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        send_confirmation_email(form.email.data, new_user.id)

        flash('A confirmation code has been sent to your email', 'success')
        return redirect(url_for('user.user_login'))
    return render_template('register.html', form=form)


@login_required
@user.route('/user-dashboard')
def user_dashboard():
    return render_template('user-dashboard.html')
