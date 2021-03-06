"""empty message

Revision ID: 7999a194bae1
Revises: 382d4161bde1
Create Date: 2022-05-28 10:54:23.445465

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7999a194bae1'
down_revision = '382d4161bde1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('past_shows', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.add_column('upcoming_shows', sa.Column('venue_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('upcoming_shows', 'venue_id')
    op.drop_column('past_shows', 'venue_id')
    # ### end Alembic commands ###
