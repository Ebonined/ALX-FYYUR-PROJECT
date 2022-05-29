#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from email.mime import image
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    venue_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
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

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    artist_id = db.Column(db.Integer, primary_key=True)
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
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    return value


app.jinja_env.filters['datetime'] = format_datetime


#----------------------------------------------------------------------------#
# Added Funtions by Daniel Ebonine
#----------------------------------------------------------------------------#
# Converts string postgresql array to list for jinja2 compartibility
def sqlarraytolist(string):
    string = string.strip()
    string = string.replace(', ', ',')
    return string.split(',')


def listTosqlarray(list):
    pass
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    vTable = db.session.query(Venue).filter(
        Venue.venue_id == venue_id).all()[0]
    psTable = db.session.query(past_shows).filter(
        past_shows.venue_id == venue_id).all()
    upsTable = db.session.query(upcoming_shows).filter(
        upcoming_shows.venue_id == venue_id).all()

    # Convert database to dict for jinja2 compatibility
    venue = {}
    try:
        v_col_key = [col.key for col in vTable.__table__.columns]
    except IndexError:
        v_col_key = []
    try:
        ps_col_key = [col.key for col in psTable[0].__table__.columns]
    except IndexError:
        ps_col_key = []
    try:
        ups_col_key = [col.key for col in upsTable[0].__table__.columns]
    except IndexError:
        ups_col_key = []

    for v_col in v_col_key:
        # Convert array string to array for jinja compatibility
        if v_col == 'genres':
            string = vTable.__getattribute__(f'{v_col}')
            strarr = sqlarraytolist(string)
            venue[f'{v_col}'] = strarr
        else:
            venue[f'{v_col}'] = vTable.__getattribute__(f'{v_col}')
    ps = []
    for psrow in psTable:
        tempdict = {}
        for ps_col in ps_col_key:
            tempdict[f'{ps_col}'] = psrow.__getattribute__(f'{ps_col}')
        ps.append(tempdict)
    ups = []
    for upsrow in upsTable:
        tempdict = {}
        for ups_col in ups_col_key:
            tempdict[f'{ups_col}'] = upsrow.__getattribute__(f'{ups_col}')
        ups.append(tempdict)

    venue['past_shows'] = ps
    venue['upcoming_shows'] = ups
    venue['past_shows_count'] = len(ps)
    venue['upcoming_shows_count'] = len(ups)

    return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    # Using raw sql to enable jinja2 template compatibility by using `AS`
    psTable = db.session.execute(f"""SELECT * FROM PAST_SHOWS 
              INNER JOIN (SELECT VENUE.VENUE_ID AS VENUE_ID,
              VENUE.IMAGE_LINK AS VENUE_IMAGE_LINK,
              VENUE.NAME AS VENUE_NAME FROM VENUE)
              AS VENUE ON VENUE.VENUE_ID = PAST_SHOWS.VENUE_ID 
              WHERE PAST_SHOWS.ARTIST_ID = {artist_id}""")
    upsTable = db.session.execute(f"""SELECT * FROM UPCOMING_SHOWS 
              INNER JOIN (SELECT VENUE.VENUE_ID AS VENUE_ID,
              VENUE.IMAGE_LINK AS VENUE_IMAGE_LINK,
              VENUE.NAME AS VENUE_NAME FROM VENUE)
              AS VENUE ON VENUE.VENUE_ID = UPCOMING_SHOWS.VENUE_ID 
              WHERE UPCOMING_SHOWS.ARTIST_ID = {artist_id}""")
    aTable = db.session.query(Artist).filter(
        Artist.artist_id == artist_id).all()[0]

    artist = {}
    try:
        v_col_key = [col.key for col in aTable.__table__.columns]
    except IndexError:
        v_col_key = []

    for v_col in v_col_key:
        if v_col == 'genres':
            strarr = sqlarraytolist(aTable.__getattribute__(f'{v_col}'))
            artist[f'{v_col}'] = strarr
        else:
            artist[f'{v_col}'] = aTable.__getattribute__(f'{v_col}')
    ps = []
    for r in psTable:
        cols = list(r.keys())
        tempdict = {}
        for c in cols:
            tempdict[c] = r[c]
        ps.append(tempdict)
    ups = []
    for r in upsTable:
        cols = list(r.keys())
        tempdict = {}
        for c in cols:
            tempdict[c] = r[c]
        ups.append(tempdict)

    artist['past_shows'] = ps
    artist['upcoming_shows'] = ups
    artist['past_shows_count'] = len(ps)
    artist['upcoming_shows_count'] = len(ups)

    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = db.session.execute(f"""SELECT ARTIST_ID AS ID, NAME, GENRES,
    CITY, STATE, PHONE, WEBSITE, FACEBOOK_LINK, SEEKING_VENUE,
    SEEKING_DESCRIPTION, IMAGE_LINK
    FROM ARTIST
    WHERE ARTIST_ID = {artist_id}""")
    artist = next(artist)
    default_genres = sqlarraytolist(artist['genres'])
    form = ArtistForm(state=artist['state'], genres=default_genres)
    # TODO: populate form with fields from artist with ID <artist_id>

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    result = request.get_json()
    query_filter = db.session.query(Artist).filter(
        Artist.artist_id == artist_id)

    query_filter.update({Artist.name: result['name'],
                         Artist.genres: ','.join(result['genres']),
                         Artist.city: result['city'],
                         Artist.state: result['state'],
                         Artist.phone: result['phone'],
                         Artist.website: result['website_link'],
                         Artist.facebook_link: result['facebook_link'],
                         Artist.seeking_venue: result['seeking_venue'],
                         Artist.image_link: result['image_link'],
                         Artist.seeking_description: result['seeking_description']})
    db.session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.execute(f"""SELECT VENUE_ID AS ID, NAME, GENRES,
    ADDRESS, CITY, STATE, PHONE, WEBSITE, FACEBOOK_LINK, SEEKING_TALENT,
    SEEKING_DESCRIPTION, IMAGE_LINK
    FROM VENUE
    WHERE VENUE_ID = {venue_id}""")
    venue = next(venue)
    default_genres = sqlarraytolist(venue['genres'])
    form = VenueForm(state=venue['state'], genres=default_genres)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    result = request.get_json()
    print(result)
    query_filter = db.session.query(Venue).filter(
        Venue.venue_id == venue_id)

    query_filter.update({Venue.name: result['name'],
                         Venue.genres: ','.join(result['genres']),
                         Venue.address: result['address'],
                         Venue.city: result['city'],
                         Venue.state: result['state'],
                         Venue.phone: result['phone'],
                         Venue.website: result['website_link'],
                         Venue.facebook_link: result['facebook_link'],
                         Venue.seeking_talent: result['seeking_talent'],
                         Venue.image_link: result['image_link'],
                         Venue.seeking_description: result['seeking_description']})
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
