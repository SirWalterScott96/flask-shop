from flask import Flask, render_template, redirect, url_for, request, flash, \
    json, jsonify, session, make_response, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, HiddenField, TextAreaField, EmailField, \
    SelectField, SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid
import os
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from datetime import timedelta
from PIL import Image
from flask.cli import with_appcontext
from getpass import getpass

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
COOKIE_DURATION = timedelta(days=3)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_string_its_important'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['REMEMBER_COOKIE_DURATION'] = COOKIE_DURATION
app.config["UPLOAD_EXTENSIONS"] = ["jpg", "png"]
app.config['UPLOAD_FOLDER_PRODUCT_IMGS'] = os.path.join(os.path.abspath('static/product_imgs'))
app.config['UPLOAD_FOLDER_SUBCATEGORY_IMGS'] = os.path.join(os.path.abspath('static/subcategory_imgs'))
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = ('Flask Shop', 'Flask shop')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'dpfrjyt@gmail.com'
app.config['MAIL_PASSWORD'] = 'fecosxhkvojaxckt'

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

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
            return redirect(url_for('home'))

    return wrapper


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sub_category = db.relationship('Subcategory', backref='categories', lazy=True)


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    img_url = db.Column(db.String(200), nullable=False)

    products = db.relationship('Products', backref='subcategory', lazy=True)


class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text)

    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'))

    discount_products = db.relationship('DiscountProducts', backref='products', lazy=True)

    def update_from_json(self, data: dict):
        if 'card-name' in data:
            self.name = data['card-name']
        if 'card-price' in data:
            self.price = data['card-price']
        if 'card-quantity' in data:
            self.quantity = data['card-quantity']
        if 'card-description' in data:
            self.description = data['card-description']

        db.session.commit()


class DiscountProducts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discount = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)


class Admin(db.Model, UserMixin):
    id = db.Column(db.String(50), primary_key=True, default=str(uuid.uuid4()), unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20))

    @staticmethod
    def does_exist_admin():
        is_admin_exist = Admin.query.filter_by(role='admin').all()
        return is_admin_exist

    @staticmethod
    def create_admin(name: str, username: str, password: str):
        new_admin = Admin(name=name,
                          username=username,
                          password=generate_password_hash(password),
                          role='admin')

        db.session.add(new_admin)
        db.session.commit()

    @staticmethod
    @app.cli.command(name='init_admin')
    @with_appcontext
    def init_admin():
        if not Admin.does_exist_admin():
            print('Creating new admin')
            name: str = str(input('Enter your name: '))
            username: str = str(input('Enter your username: '))
            password: str = getpass('Enter your password: ')

            Admin.create_admin(name, username, password)

            print('The admin is initialized.')
        else:
            print('Admin already exist')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    password = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean(), default=False)


class UserRegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])


class AdminRegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    role = SelectField(choices=['admin', 'administrator'])


class UserLoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class AdminLoginForm(FlaskForm):
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])


class CategoriesForm(FlaskForm):
    name = StringField(validators=[DataRequired()])


class SubCategoryForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    img_upload = FileField(validators=[FileRequired(), FileAllowed(app.config["UPLOAD_EXTENSIONS"], 'Images only')])
    hidden_tag_id = HiddenField()


class ProductForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    price = FloatField(validators=[DataRequired()])
    img_upload = FileField(validators=[FileRequired(), FileAllowed(app.config["UPLOAD_EXTENSIONS"], 'Images only')])
    quantity = IntegerField(validators=[DataRequired()])
    description = TextAreaField()
    hidden_tag_id = HiddenField()


@app.route('/')
def home():
    categories = Categories.query.all()
    return render_template('index.html', categories=categories)


@app.route('/category/<category_id>')
def category(category_id):
    category_local = Categories.query.all()
    return render_template('category.html', categories=category_local, category_id=int(category_id))


@app.route('/admin')
@only_admin_access
def admin():
    categories_form = CategoriesForm()
    product_form = ProductForm()
    sub_categories_form = SubCategoryForm()

    categories = Categories.query.all()

    response = make_response(render_template('admin.html', categories=categories,
                                             categories_form=categories_form,
                                             product_form=product_form,
                                             sub_categories_form=sub_categories_form))
    response.set_cookie('admin_id', '5000', max_age=3600)
    return response


@app.route('/admin/category-<category_id>')
@only_admin_access
def admin_show_subcategories(category_id):
    categories_form = CategoriesForm()
    sub_categories_form = SubCategoryForm()
    product_form = ProductForm()

    categories = Categories.query.all()
    subcategories_in_category = Categories.query.filter_by(id=category_id).first()

    return render_template('admin-category.html', categories=categories,
                           sub_categories_form=sub_categories_form,
                           categories_form=categories_form,
                           subcategories_in_category=subcategories_in_category)


@app.route('/admin/category-<category_id>/subcategory-<subcategory_id>')
@only_admin_access
def admin_show_products(category_id, subcategory_id):
    categories_form = CategoriesForm()
    sub_categories_form = SubCategoryForm()
    product_form = ProductForm()

    categories = Categories.query.all()
    sub_category_active = Subcategory.query.filter_by(id=subcategory_id).first()

    return render_template('admin_category_subcategory_product.html', categories_form=categories_form,
                           sub_categories_form=sub_categories_form,
                           product_form=product_form,
                           categories=categories,
                           sub_category_active=sub_category_active,
                           category_id=int(category_id),
                           subcategory_id=int(subcategory_id))


@app.route('/admin-panel/add-admin', methods=['GET', 'POST'])
@only_admin_access
def add_admin():
    form = AdminRegisterForm()
    admins = Admin.query.all()

    if form.validate_on_submit():
        new_admin = Admin(
            username=form.username.data,
            name=form.name.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for('add_admin'))
    return render_template('paneladmin-admins.html', form=form, admins=admins)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    form = UserLoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password, form.password.data):
            if not user.email_confirmed:
                flash('Confirm your email', 'danger')
                return redirect(url_for('user_login'))

            login_user(user)
            return redirect(url_for('home'))

        flash('incorrect username or password', 'danger')
        return redirect(url_for('user_login'))

    return render_template('login.html', form=form)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        admin_to_login = Admin.query.filter_by(username=form.username.data).first()
        if admin_to_login and check_password_hash(admin_to_login.password, form.password.data):
            login_user(admin_to_login)
            return redirect(url_for('admin'))

        flash('incorrect data', 'danger')
        return redirect(url_for('admin_login'))

    return render_template('admin-login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        return redirect(url_for('user_login'))
    return render_template('register.html', form=form)


@app.route('/resend_confirmation_email/<user_email>/<user_id>', methods=['GET', 'POST'])
def resend_confirmation_email(user_email, user_id):
    send_confirmation_email(user_email, user_id)

    flash('A confirmation code has been sent to your email', 'success')
    return redirect(url_for('user_login'))


def send_confirmation_email(user_email, id_user):
    mail = Mail(app)
    subject = 'Confirm Your Registration'
    token = serializer.dumps(user_email, salt='email-confirm')
    confirmation_url = url_for('confirm_email', confirm_id=id_user, token=token, _external=True)
    message_body = f'Click the following link to confirm your registration: ' \
                   f'{confirmation_url}'
    msg = Message(subject=subject, recipients=[user_email], body=message_body)
    mail.send(msg)


@app.route('/confirm-email/<confirm_id>/<token>')
def confirm_email(confirm_id, token):
    # TODO a resend confirmation email
    try:
        user = User.query.filter_by(id=confirm_id).first()
        if not user:
            flash('no user found', 'danger')
            return redirect(url_for('user_login'))

        serializer.loads(token, salt='email-confirm', max_age=3600)

        user.email_confirmed = True
        db.session.commit()

        flash('Email is confirmed', 'success')
        return redirect(url_for('user_login'))
    except SignatureExpired:
        flash('Expired token', 'danger')
        return redirect(url_for('user_login'))
    except BadSignature:
        flash('Invalid token', 'danger')
        return redirect(url_for('user_login', user_email=user.email, id_user=user.id))


@app.route('/admin-create-category', methods=['POST'])
@only_admin_access
def admin_create_category():
    # TODO a check if this category exists
    categories_form = CategoriesForm()

    if categories_form.validate_on_submit():
        if Categories.query.filter_by(name=categories_form.name.data).first():
            return redirect(url_for('admin'))

        new_category = Categories(name=categories_form.name.data)
        db.session.add(new_category)
        db.session.commit()

        return redirect(url_for('admin'))
    return redirect(url_for('admin'))


@app.route('/admin-create-subcategory', methods=['POST'])
@only_admin_access
def admin_create_subcategory():
    form = SubCategoryForm()
    if form.validate_on_submit():
        tag_id = form.hidden_tag_id.data
        image = form.img_upload.data
        image_name = str(uuid.uuid4()) + '_' + secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER_SUBCATEGORY_IMGS'], image_name)
        image.save(image_path)

        new_subcategory = Subcategory(name=form.name.data,
                                      category_id=tag_id,
                                      img_url='subcategory_imgs/{}'.format(image_name))

        db.session.add(new_subcategory)
        db.session.commit()

        return redirect(url_for('admin', subcategory_id=new_subcategory.id))
    return redirect(url_for('admin'))


def resize_img(image_path):
    height = 230
    with Image.open(image_path) as img:
        aspect_ratio = img.width / img.height
        width = int(height / aspect_ratio)
        img.thumbnail((width, height))
        img.save(image_path)


@app.route('/admin-create-product/<category_id>/<subcategory_id>', methods=['POST'])
@only_admin_access
def admin_create_product(category_id, subcategory_id):
    product_form = ProductForm()

    if product_form.validate_on_submit():
        tag_id = product_form.hidden_tag_id.data
        category_id_local = Subcategory.query.filter_by(id=tag_id).first()

        image = product_form.img_upload.data
        image_name = str(uuid.uuid4()) + '_' + secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER_PRODUCT_IMGS'], image_name)
        image.save(image_path)
        resize_img(image_path)

        product = Products(name=product_form.name.data,
                           price=product_form.price.data,
                           img_url='product_imgs/{}'.format(image_name),
                           quantity=product_form.quantity.data,
                           description=product_form.description.data,
                           subcategory_id=category_id_local.id)

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin_show_products', category_id=category_id, subcategory_id=subcategory_id))
    return redirect(url_for('admin_show_products'))


@app.route('/edit_product', methods=['POST'])
def edit_product():
    header_validation = request.headers.get('Admin-Ajax-Id')

    if not header_validation:
        abort(403)

    data = request.get_json()
    product_to_edit = Products.query.filter_by(id=data['product_id']).first()

    if product_to_edit:
        product_to_edit.update_from_json(data)

    return jsonify({'status': 'success', 'message': 'Saved!'})


@app.route('/admin-delete-product/<product_id>/<category_id>/<subcategory_id>')
@only_admin_access
def admin_delete_product(product_id, category_id, subcategory_id):
    product_to_delete = Products.query.filter_by(id=product_id).first()

    if product_to_delete:
        db.session.delete(product_to_delete)
        db.session.commit()
    return redirect(url_for('admin_show_products', category_id=category_id, subcategory_id=subcategory_id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
