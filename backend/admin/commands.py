# -*- coding: utf-8 -*-
"""Admin commands."""

import click
from flask.cli import with_appcontext
from getpass import getpass
from backend.admin.models import Admin


@click.command(name='init_admin')
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
