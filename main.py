from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_string_its_important'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = '/path/to/the/uploads'
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
    img_upload = FileField(validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only')])
    quantity = IntegerField(validators=[DataRequired()])
    categories_id = StringField(validators=[DataRequired()])


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin')
@only_admin_access
def admin():
    categories_form = CategoriesForm()
    categories = Categories.query.all()
    print(categories)
    return render_template('admin.html', categories=categories, categories_form=categories_form)


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


@app.route('/admin-create-category/<category_id>', methods=['POST'])
@only_admin_access
def admin_create_product(category_id):
    product_form = ProductForm()

    if product_form.validate_on_submit():
        category_id_local = Categories.query.filter_by(id=category_id).first()

        product = Products(name=product_form.name.data,
                           price=product_form.price.data,
                           # TODO add normal link to img
                           img_url=product_form.img_upload.data,
                           quantity=product_form.quantity.data,
                           categories_id=category_id_local.id)

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin'))
    return redirect(url_for('admin'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
