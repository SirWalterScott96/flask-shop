from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, FloatField, HiddenField, TextAreaField, EmailField, SelectField
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

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
COOKIE_DURATION = timedelta(days=3)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_string_its_important'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['REMEMBER_COOKIE_DURATION'] = COOKIE_DURATION
app.config["UPLOAD_EXTENSIONS"] = ["jpg", "png"]
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath('static/product_imgs'))
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
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
            return redirect(url_for('admin_login'))
    return wrapper


class Categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sub_category = db.relationship('Subcategory', backref='categories', lazy=True)


class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

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


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String())
    password = db.Column(db.String(100))
    email_confirmed = db.Column(db.Boolean(), default=False)


class RegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    email = EmailField(validators=[DataRequired()])


class AdminRegisterForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    username = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    role = SelectField(['admin', 'administrator'])


class LoginForm(FlaskForm):
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
    categories = Categories.query.all()
    return render_template('index.html', categories=categories)


@app.route('/category/<category_id>')
def category(category_id):
    category_local = Categories.query.filter_by(id=category_id).all()
    print(category_local[0].name)
    return render_template('category.html', category_local=category_local)


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


@app.route('/admin-panel/add-admin', methods=['GET', 'POST'])
@only_admin_access
def add_admin():
    form = AdminRegisterForm()
    admins = Admin.query.all()

    if form.validate_on_submit():

        new_admin = Admin(
            name=form.name.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(new_admin)
        db.session.commit()

        return redirect(url_for('add_admin'))
    return render_template('paneladmin-admins.html', form=form, admins=admins)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.name.data

        if not username.startswith('admin'):
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('home'))
        elif username.startswith('admin'):
            admin_local = Admin.query.filter_by(username=username).first()

            if admin_local and check_password_hash(admin_local.username, form.password.data):
                login_user(admin_local)
                return redirect(url_for('admin'))

            return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()

    if form.validate_on_submit():
        new_user = User(name=form.name.data,
                        username=form.username.data,
                        password=generate_password_hash(form.password.data),
                        email=form.email.data)
        db.session.add(new_user)
        db.session.commit()
        send_confirmation_email(form.email.data, new_user.id)

        flash('A confirmation code has been sent to your email')
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)


def send_confirmation_email(email, id_user):
    mail = Mail(app)
    subject = 'Confirm Your Registration'
    token = serializer.dumps(email, salt='email-confirm')
    confirmation_url = url_for('emai_confirm', id=id_user,  token=token,  _external=True)
    message_body = f'Click the following link to confirm your registration: {confirmation_url}'
    msg = Message(subject=subject, recipients=[email], body=message_body)
    mail.send(msg)


@app.route('/confirm-email/<id>/<token>')
def confirm_email(id, token):
    try:
        serializer.loads(token, salt='email-confirm', max_age=3600)

        user = User.query.filter_by(id=id).first()
        user.email_confirmed = True
        db.session.commit()

        flash('Email is confirmed')
        return url_for('login')
    except SignatureExpired:
        flash('Expired token')
        return redirect(url_for('login'))
    except BadSignature:
        flash('Invalid token')
        return redirect(url_for('login'))


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
