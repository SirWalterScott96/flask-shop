from flask import Flask
from backend.settings import Config

from backend.extensions import (
    login_manager,
    migrate,
    db,
)
from backend.user.views import user
from backend.orders.views import orders
from backend.public.views import public
from backend.product.views import product
from backend.admin.views import admin
from backend.admin import commands


def create_app(config_object=Config):
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


def register_extensions(app):
    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db, directory=app.config.get('MIGRATIONS_FOLDER'))


def register_blueprints(app):
    app.register_blueprint(public)
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(product, url_prefix='/product')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(orders, url_prefix='/orders')


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.init_admin)


if __name__ == '__main__':
    app = create_app()
    app.run()