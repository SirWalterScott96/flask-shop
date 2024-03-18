from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

login_manager: LoginManager = LoginManager()
migrate: Migrate = Migrate()
db: SQLAlchemy = SQLAlchemy()
bcrypt: Bcrypt = Bcrypt()
