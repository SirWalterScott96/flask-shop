"""empty message

Revision ID: cc69c71f6177
Revises: 1d83aae541c8
Create Date: 2024-03-18 18:23:49.702116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cc69c71f6177'
down_revision = '1d83aae541c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('orders_products',
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('order_id', 'product_id')
    )
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.drop_column('products_and_quantity')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.add_column(sa.Column('products_and_quantity', sa.TEXT(), nullable=False))

    op.drop_table('orders_products')
    # ### end Alembic commands ###
