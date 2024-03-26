from datetime import datetime

from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

login_manager: LoginManager = LoginManager()
migrate: Migrate = Migrate()
db: SQLAlchemy = SQLAlchemy()
bcrypt: Bcrypt = Bcrypt()



if __name__ == '__main__':
    print(datetime.utcnow())