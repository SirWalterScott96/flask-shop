from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, logout_user, current_user
import uuid
from backend.extensions import login_manager
from backend.product.models import Categories, Subcategory
from backend.user.models import User
from backend.admin.models import Admin

public = Blueprint('public', __name__, template_folder='../templates/public')


@login_manager.user_loader
def load_user(user_id):
    try:
        if uuid.UUID(str(user_id)):
            return Admin.query.get(user_id)
    except ValueError:
        return User.query.get(user_id)


@public.route('/logout')
@login_required
def logout():
    """Logout."""
    logout_user()
    return redirect(url_for('public.home'))


@public.route('/')
def home():
    categories = Categories.query.all()
    subcategory = Subcategory.query.limit(7)
    return render_template('index.html', categories=categories, subcategory=subcategory)
