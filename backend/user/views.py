from flask import Blueprint, render_template, redirect, flash, url_for, request, abort, session
from flask_login import login_user, current_user, login_required, logout_user
from collections import defaultdict
from functools import wraps

from .forms import UserLoginForm, UserRegisterForm
from backend.extensions import db, login_manager
from backend.mail.classes import EmailSender
from backend.orders.models import Orders, orders_products
from .models import User, Account, SaveProperties

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


@user.route('/dashboard/settings')
@login_required
def dashboard_settings():
    return render_template('dashboard-settings.html')


@user.route('/dashboard/orders')
@login_required
def dashboard_orders():
    get_orders_quantity_dict = Orders.get_quantity_dict(current_user)

    return render_template('dashboard-orders.html', order_quantities_dict=get_orders_quantity_dict)


@user.route('/set-account-details', methods=['PUT'])
@login_required
def set_account_details():
    account = Account()
    if request.method == 'PUT' and account.account_details_validation(request.json):
        save_properties = SaveProperties(current_user.id)
        save_properties.set_new_account_details(name=account.name, phone_number=account.phone_number)
        return '', 200
    abort(400)


@user.route('/set-new-password', methods=['PUT'])
@login_required
def set_new_password():
    account = Account()
    if request.method == 'PUT' and account.new_password_validation(request.json, current_user.id):
        save_properties = SaveProperties(current_user.id)
        save_properties.set_new_password(account.new_password)
        return '', 200
    abort(400)


@user.route('/send-email-reset-password', methods=['GET', 'POST'])
def send_email_reset_password():
    return render_template('send-email-reset-password.html')


@user.route('/reset-password-by-email', methods=['POST'])
def reset_password_by_email():
    if request.method == 'POST' and Account.email_validation(request.json):
        response = request.json
        EmailSender.send_password_reset_email(user_email=response['email'])
        return '', 200


@user.route('/reset-password/<token>/<user_email>', methods=['GET', 'PUT'])
def reset_password(token, user_email):
    if 'reset_password' not in session:
        return redirect(url_for('user.user_login'))

    if request.method == 'PUT' and Account.email_validation(request.json):
        response = request.json
        user_to_update = User.get_user_by_email(user_email)
        save_properties = SaveProperties(user_to_update.id)
        save_properties.set_new_password(response['new_password'])
        session.pop('reset_password')
        return '', 200

    return render_template('reset-password.html', user_email=user_email)
