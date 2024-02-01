from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user
import uuid


app = Flask(__name__)
app.config['SECRET_KEY'] = 'lapo4kado4ka'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
admin = Admin(app)


@login_manager.user_loader
def load_user(user_id):
    try:
        if uuid.UUID(str(user_id)):
            return Admin.query.get(user_id)
    except ValueError:
        return User.query.get(user_id)


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


admin.add_view(ModelView(Admin, db.session))

@app.route('/')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
