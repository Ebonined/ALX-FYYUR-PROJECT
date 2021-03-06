"""empty message

Revision ID: 382d4161bde1
Revises: ae0ba64e358b
Create Date: 2022-05-25 22:50:39.124463

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '382d4161bde1'
down_revision = 'ae0ba64e358b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Venue')
    op.add_column('venue', sa.Column('upcoming_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'upcoming_shows')
    op.create_table('Venue',
    sa.Column('venue_id', sa.INTEGER(), server_default=sa.text('nextval(\'"Venue_venue_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('genres', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('address', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('website', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('facebook_link', sa.VARCHAR(length=120), autoincrement=False, nullable=True),
    sa.Column('seeking_talent', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('seeking_description', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('upcoming_shows', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('pass_shows_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('venue_id', name='Venue_pkey')
    )
    # ### end Alembic commands ###
