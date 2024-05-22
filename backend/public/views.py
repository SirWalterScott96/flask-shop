from flask import Blueprint, render_template, g
from sqlalchemy.sql.expression import func
import uuid

from backend.extensions import login_manager
from backend.product.models import Categories, Subcategory, Products
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


def set_categories():
    if 'categories' not in g:
        g.categories = Categories.query.all()


@public.route('/')
def home():
    subcategory = Subcategory.query.order_by(func.random()).limit(7).all()
    popular_products = Products.query.order_by(func.random()).limit(12).all()
    return render_template('index.html', subcategory=subcategory, popular_products=popular_products)
