from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, HiddenField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid
import os
from PIL import Image

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_string_its_important'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["UPLOAD_EXTENSIONS"] = ["jpg", "png"]
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath('static/product_imgs'))

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        if uuid.UUID(str(user_id)):
            return Admin.query.get(user_id)
    except ValueError:
        return User.query.get(user_id)


def only_admin_access(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_active and uuid.UUID(str(current_user.id)):
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin_login'))

    return wrapper


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    products = db.relationship('Products', backref='categories', lazy=True)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)
    categories_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    discount_products = db.relationship('DiscountProducts', backref='products', lazy=True)


class DiscountProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discount = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


class Admin(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True, default=str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean(), default=True)


class AdminLoginForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class CategoriesForm(FlaskForm):
    name = StringField(validators=[DataRequired()])


class ProductForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    price = FloatField(validators=[DataRequired()])
    img_upload = FileField(validators=[FileRequired(), FileAllowed(app.config["UPLOAD_EXTENSIONS"], 'Images only')])
    quantity = IntegerField(validators=[DataRequired()])
    description = TextAreaField()
    hidden_tag_id = HiddenField()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin', defaults={'category_id': None})
@app.route('/admin/<category_id>')
@only_admin_access
def admin(category_id):
    categories_form = CategoriesForm()
    product_form = ProductForm()

    categories = Categories.query.all()
    if category_id:
        category_active = Categories.query.filter_by(id=category_id).first()

    return render_template('admin.html', categories=categories, categories_form=categories_form,
                           category_active=category_active if category_id else None, product_form=product_form)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin_local = Admin.query.filter_by(name=form.name.data).first()
        if not admin_local:
            return redirect(url_for('admin-login'))

        if check_password_hash(admin_local.password, form.password.data):
            login_user(admin_local)
            return redirect(url_for('admin'))

    return render_template('admin_login.html', form=form)


@app.route('/admin-create-category', methods=['POST'])
@only_admin_access
def admin_create_category():
    # TODO a check if this category exists
    categories_form = CategoriesForm()

    if categories_form.validate_on_submit():
        if Categories.query.filter_by(name=categories_form.name.data):
            return redirect(url_for('admin'))

        new_category = Categories(name=categories_form.name.data)
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('admin'))
    return redirect(url_for('admin'))


def resize_img(image_path, width=300):
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        height = int(width / aspect_ratio)
        img.thumbnail((width, height))
        img.save(image_path)


@app.route('/admin-create-product', methods=['POST'])
@only_admin_access
def admin_create_product():
    product_form = ProductForm()

    if product_form.validate_on_submit():
        tag_id = product_form.hidden_tag_id.data
        category_id_local = Categories.query.filter_by(id=tag_id).first()

        image = product_form.img_upload.data
        image_name = str(uuid.uuid4()) + '_' + secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
        image.save(image_path)
        resize_img(image_path)

        product = Products(name=product_form.name.data,
                           price=product_form.price.data,
                           img_url='product_imgs/{}'.format(image_name),
                           quantity=product_form.quantity.data,
                           description=product_form.description.data,
                           categories_id=category_id_local.id)

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin', category_id=tag_id))
    return redirect(url_for('admin'))


@app.route('/admin-delete-product/<product_id>/<category_id>', methods=['GET', 'POST'])
@only_admin_access
def admin_delete_product(product_id, category_id):
    product_to_delete = Products.query.filter_by(id=product_id).first()

    if product_to_delete:
        db.session.delete(product_to_delete)
        db.session.commit()

    return redirect(url_for('admin', category_id=category_id))



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
