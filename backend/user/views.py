from functools import wraps

from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_user, current_user, login_required, logout_user
from collections import defaultdict

from .forms import UserLoginForm, UserRegisterForm
from backend.extensions import db, login_manager
from backend.mail.classes import EmailSender
from backend.orders.models import Orders, orders_products
from .models import User

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


@user.route('/dashboard/settings')
@login_required
def dashboard_settings():
    return render_template('dashboard-settings.html')



@user.route('/dashboard/orders')
@login_required
def dashboard_orders():

    order_quantities_dict = defaultdict(list)
    for order in current_user.orders:
        products = order.products
        for product in products:
            quantity = db.session.query(orders_products.c.quantity).filter_by(order_id=order.id,
                                                                              product_id=product.id).scalar()
            order_quantities_dict[order.id].append(quantity)

    return render_template('dashboard-orders.html', order_quantities_dict=order_quantities_dict)
