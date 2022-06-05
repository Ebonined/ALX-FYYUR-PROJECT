from flask_migrate import Migrate
from flask import Flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = "venue"

    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    genres = db.Column(db.ARRAY(db.String()))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    show_child = db.relationship("Shows", backref="venue", lazy=True)
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
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show_child = db.relationship("Shows", backref="artist", lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# ADDED: added tables for `shows`
class Shows(db.Model):
    __tablename__ = 'shows'
    show_id = db.Column(db.Integer, db.Sequence('shows_id_seq'), primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.venue_id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.artist_id'), nullable=False)
    start_time = db.Column(db.DateTime)



# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# db.create_all()
