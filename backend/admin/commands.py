# -*- coding: utf-8 -*-
"""Admin commands."""

import click
from flask.cli import with_appcontext
from getpass import getpass
from backend.admin.models import Admin


@click.command(name='init_admin', help='Initializes the admin account for the application', short_help='Initializes the admin account.')
@with_appcontext
def init_admin():
    if not Admin.does_exist_admin():
        print('Creating new admin')
        name: str = str(input('Enter your name: '))
        username: str = str(input('Enter your username: '))
        password: str = getpass('Enter your password: ')
        repeat_password: str = getpass('Repeat your password: ')

        if not password == repeat_password:
            return print('Passwords do not match.')

        Admin.create_admin(name, username, password)

        print('The admin is initialized.')
    else:
        print('Admin already exist')
