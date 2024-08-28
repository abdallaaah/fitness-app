"""add field bmi to body table

Revision ID: a9ad9058c869
Revises: c90e178637e0
Create Date: 2024-08-28 13:55:24.492529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9ad9058c869'
down_revision = 'c90e178637e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('body', schema=None) as batch_op:
        batch_op.add_column(sa.Column('bmi', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('body', schema=None) as batch_op:
        batch_op.drop_column('bmi')

    # ### end Alembic commands ###
