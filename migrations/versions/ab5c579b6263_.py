"""empty message

Revision ID: ab5c579b6263
Revises: 4727f984b80e
Create Date: 2022-05-31 21:20:07.441146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ab5c579b6263'
down_revision = '4727f984b80e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('artist_id', sa.Integer(), nullable=True))
    op.drop_column('shows', 'rtist_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('rtist_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_column('shows', 'artist_id')
    # ### end Alembic commands ###