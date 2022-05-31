from app import db, app
from flask_migrate import Migrate

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = "venue"

    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    genres = db.Column(db.String(100))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    db.UniqueConstraint('name', name='uix_1')
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artist"

    artist_id = db.Column(db.Integer, db.Sequence(
        'artist_artist_id_seq', start=1), primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# ADDED: added tables for `past_shows` and `upcoming_shows`


class past_shows(db.Model):
    show_id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer)
    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String(100))
    artist_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime)


class upcoming_shows(db.Model):
    show_id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer)
    artist_id = db.Column(db.Integer)
    artist_name = db.Column(db.String(100))
    artist_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime)


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# db.create_all()
