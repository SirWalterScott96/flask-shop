"""empty message

Revision ID: 348c3fe9f078
Revises: 25693ca1270f
Create Date: 2024-04-03 18:21:20.499715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '348c3fe9f078'
down_revision = '25693ca1270f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phone_number', sa.String(length=13), nullable=True, server_default=''))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('phone_number')

    # ### end Alembic commands ###
