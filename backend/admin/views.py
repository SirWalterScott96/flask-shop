from flask import redirect, url_for, Blueprint, render_template, abort, jsonify, session, request
from flask_login import current_user, login_user
import uuid
from functools import wraps
import os

from .models import Admin
from .forms import AdminLoginForm, AdminRegisterForm
from backend.product.forms import CategoriesForm, ProductForm, SubCategoryForm
from backend.product.models import Categories, Subcategory, Products
from backend.product.image_utils import ImageProduct, ImageSubcategory
from backend.extensions import db
from backend.settings import Config
from backend.orders.models import Orders


admin = Blueprint('admin', __name__, template_folder='../templates/admin')


def only_admin_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if current_user.is_active and uuid.UUID(str(current_user.id)):
                return func(*args, **kwargs)
        except ValueError:
            return redirect(url_for('public.home'))

    return wrapper


@admin.route('/home')
@only_admin_access
def home():
    """Home page."""
    categories_form = CategoriesForm()
    product_form = ProductForm()
    sub_categories_form = SubCategoryForm()

    categories = Categories.query.all()

    return render_template('home.html', categories=categories,
                           categories_form=categories_form,
                           product_form=product_form,
                           sub_categories_form=sub_categories_form)


@admin.route('/login', methods=['GET', 'POST'])
def login():
    """login page."""
    form = AdminLoginForm()

    if form.validate_on_submit():
        login_user(form.admin)
        return redirect(url_for('admin.home'))

    return render_template('admin-login.html', form=form)


@admin.route('/home/category-<category_id>')
@only_admin_access
def show_subcategories(category_id):
    """Show subcategories of category."""
    categories_form = CategoriesForm()
    sub_categories_form = SubCategoryForm()

    categories = Categories.query.all()
    subcategories_in_category = Categories.query.filter_by(id=category_id).first()

    return render_template('admin-category.html', categories=categories,
                           sub_categories_form=sub_categories_form,
                           categories_form=categories_form,
                           subcategories_in_category=subcategories_in_category)


@admin.route('/home/category-<category_id>/subcategory-<subcategory_id>')
@only_admin_access
def show_products(category_id, subcategory_id):
    """Show all products for a category."""
    categories_form = CategoriesForm()
    sub_categories_form = SubCategoryForm()
    product_form = ProductForm()

    categories = Categories.query.all()
    sub_category_active = Subcategory.query.filter_by(id=subcategory_id).first()

    return render_template('admin/admin_category_subcategory_product.html', categories_form=categories_form,
                           sub_categories_form=sub_categories_form,
                           product_form=product_form,
                           categories=categories,
                           sub_category_active=sub_category_active,
                           category_id=int(category_id),
                           subcategory_id=int(subcategory_id))


@admin.route('/create-category', methods=['POST'])
@only_admin_access
def create_category():
    """Create new category."""
    categories_form = CategoriesForm()

    if categories_form.validate_on_submit():
        new_category = Categories(name=categories_form.name.data)
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('admin.home'))
    return redirect(url_for('admin.home'))


@admin.route('/create-subcategory', methods=['POST'])
@only_admin_access
def create_subcategory():
    """Create new subcategory."""
    form = SubCategoryForm()
    if form.validate_on_submit():
        category_id = form.hidden_tag_id.data
        image = ImageSubcategory(form.img_upload.data)
        image.save_img()
        print(image.img_url())

        new_subcategory = Subcategory(name=form.name.data,
                                      category_id=category_id,
                                      img_url=image.img_url())

        db.session.add(new_subcategory)
        db.session.commit()

        return redirect(url_for('admin.show_subcategories', category_id=category_id))
    return redirect(url_for('admin_show.subcategories'))


@admin.route('/create-product/<category_id>/<subcategory_id>', methods=['POST'])
@only_admin_access
def create_product(category_id, subcategory_id):
    """Create the product."""
    product_form = ProductForm()

    if product_form.validate_on_submit():
        subcategory_id = product_form.hidden_tag_id.data

        image = ImageProduct(product_form.img_upload.data)
        image.save_img()

        product = Products(name=product_form.name.data,
                           price=product_form.price.data,
                           img_url=image.img_url(),
                           quantity=product_form.quantity.data,
                           description=product_form.description.data,
                           subcategory_id=subcategory_id)

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin.show_products', category_id=category_id, subcategory_id=subcategory_id))
    return redirect(url_for('admin.show_products'))


@admin.route('/edit_product', methods=['PATCH'])
def edit_product():
    """Edit the product."""
    is_admin_request = Admin.query.filter_by(id=session['_user_id']).first()

    if not is_admin_request:
        abort(403)

    data = request.get_json()
    product_to_edit = Products.query.filter_by(id=data['product_id']).first()

    if product_to_edit:
        product_to_edit.update_from_json(data)

    return jsonify({'status': 'success', 'message': 'Saved!'})


@admin.route('/delete-product/<product_id>/<category_id>/<subcategory_id>')
@only_admin_access
def delete_product(product_id, category_id, subcategory_id):
    """Delete the product."""
    product_to_delete = Products.query.filter_by(id=product_id).first()

    if product_to_delete:
        db.session.delete(product_to_delete)
        db.session.commit()
    return redirect(url_for('admin_show_products', category_id=category_id, subcategory_id=subcategory_id))


@admin.route('/admin-panel/add-admin', methods=['GET', 'POST'])
@only_admin_access
def add_admin():
    """Register new admin."""
    form = AdminRegisterForm()
    admins = Admin.query.all()

    if form.validate_on_submit():
        new_admin = Admin(
            username=form.username.data,
            name=form.name.data,
            password=form.password.data,
            role=form.role.data
        )
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for('admin.add_admin'))
    return render_template('paneladmin-admins.html', form=form, admins=admins)


@admin.route('/orders', methods=['GET', 'POST'])
@only_admin_access
def orders():
    """Get all orders."""
    all_orders = Orders.get_all_orders()
    get_all_orders_products_data = Orders.get_all_orders_products_data()
    return render_template('orders.html', orders=all_orders,
                           order_quantities_dict=get_all_orders_products_data)


@admin.route('/orders/update-status', methods=['PATCH'])
@only_admin_access
def update_status():
    """Update order status."""
    if request.method == 'PATCH' and request.json:
        response = request.json
        status_to_update = Orders.set_new_status(response['order_id'], response['status'])
        return status_to_update
    return '', 400
