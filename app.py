# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import logging
from email.mime import image
from logging import FileHandler, Formatter
from urllib import response

import babel
import dateutil.parser
from flask import Response, flash, redirect, render_template, request, url_for
from flask_wtf import Form

from forms import *
from models import *

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_date(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "y-MM-dd h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


def format_datetime(value, format="medium"):
    return value


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Added Funtions by Daniel Ebonine
# ----------------------------------------------------------------------------#
# Converts string postgresql array to list for jinja2 compartibility
def checkboxget(mdict, key):
    try:
        var = mdict[key]
        if var:
            return True
    except:
        return False


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    stategroup = Venue.query.with_entities(Venue.city, Venue.state, db.func.count().label('venues')).\
        group_by(Venue.city, Venue.state).all()
    # Sub query for number of shows per venue
    show = Shows.query.with_entities(Shows.venue_id, db.func.count().label('num_upcoming_shows')).\
        filter(Shows.start_time > db.func.current_date()).group_by(
            Shows.venue_id).subquery('upcoming')
    # Main query for venuesresult
    venuesresult = Venue.query.with_entities(Venue.venue_id.label('id'), Venue.name, Venue.state, Venue.city,
                                             db.func.coalesce(show.columns.num_upcoming_shows, 0).
                                             label('num_upcoming_shows')).join(show, isouter=True).all()
    venuesresult = list(venuesresult)
    data = []
    for r in stategroup:
        tempdict = {}
        cols = r.keys()
        for col in cols:
            if col == "venues":
                templist = []
                for venue in venuesresult:
                    tempdict2 = {}
                    vcols = venue.keys()
                    if (
                            venue["state"] == tempdict["state"]
                            and venue["city"] == tempdict["city"]
                    ):
                        for col2 in vcols:
                            tempdict2[col2] = venue[col2]
                        templist.append(tempdict2)
                tempdict[col] = templist
            else:
                tempdict[col] = r[col]
        data.append(tempdict)
    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "").lower()
    searchresult = Venue.query.with_entities(Venue.venue_id.label('id'), Venue.name.label('name')).\
        filter(Venue.name.ilike(f'%{search_term}%')).all()

    response = {}
    search_list = list(searchresult)
    response['count'] = len(search_list)

    datalist = []
    for result in search_list:
        cols = result.keys()
        tempdict = {}
        for col in cols:
            tempdict[col] = result[col]
        datalist.append(tempdict)
    response['data'] = datalist
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    vTable = db.session.query(Venue).filter(
        Venue.venue_id == venue_id).all()[0]
    psTable = db.session.query(Shows).filter(Shows.venue_id == venue_id).\
        filter(Shows.start_time > db.func.current_date()).all()
    upsTable = db.session.query(Shows).filter(Shows.venue_id == venue_id).\
        filter(Shows.start_time < db.func.current_date()).all()

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
        venue[f"{v_col}"] = vTable.__getattribute__(f"{v_col}")
    ps = []
    for psrow in psTable:
        tempdict = {}
        for ps_col in ps_col_key:
            tempdict[f"{ps_col}"] = psrow.__getattribute__(f"{ps_col}")
        ps.append(tempdict)
    ups = []
    for upsrow in upsTable:
        tempdict = {}
        for ups_col in ups_col_key:
            tempdict[f"{ups_col}"] = upsrow.__getattribute__(f"{ups_col}")
        ups.append(tempdict)

    venue["past_shows"] = ps
    venue["upcoming_shows"] = ups
    venue["past_shows_count"] = len(ps)
    venue["upcoming_shows_count"] = len(ups)

    return render_template("pages/show_venue.html", venue=venue)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    result = request.form
    allid = Venue.query.with_entities(Venue.venue_id).all()
    ids = [int(id['venue_id']) for id in allid]
    ids.sort()
    ini = 1
    for id in ids:
        if ini < id:
            ini = ini
            break
        else:
            ini += 1
    try:
        venue = Venue(venue_id=ini, name=result["name"], genres=result.getlist('genres'),
                      address=result["address"], city=result["city"], state=result["state"],
                      phone=result["phone"], website=result["website_link"],
                      facebook_link=result["facebook_link"],  seeking_talent=checkboxget(
                          result, 'seeking_talent'),
                      image_link=result["image_link"], seeking_description=result["seeking_description"])
        db.session.add(venue)
        db.session.commit()
        flash("Venue " + result["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash("An error occurred. Venue " +
              result["name"] + ' could not be listed.')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<int:venue_id>", methods=["POST"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = True
    try:
        name = db.session.query(Venue).filter(
            Venue.venue_id == venue_id).all()[0].name
        db.session.query(Shows).filter(Shows.venue_id == venue_id).delete()
        db.session.query(Venue).filter(Venue.venue_id == venue_id).delete()
        db.session.commit()
        flash(f'Venue: {name}, has been deleted')
    except:
        db.session.rollback()
        error = False
        flash(f'Error deleting Venue: {name}')
    finally:
        db.session.close()
        if not error:
            return redirect(url_for('show_venue', venue_id=venue_id))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------


@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    artistresult = Artist.query.with_entities(Artist.artist_id.label('id'), Artist.name).\
        order_by(db.asc(Artist.name))
    artist_list = list(artistresult)
    data = []
    for artist in artist_list:
        acols = artist.keys()
        tempdict = {}
        for col in acols:
            tempdict[col] = artist[col]
        data.append(tempdict)
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "").lower()
    searchesult = Artist.query.with_entities(Artist.artist_id.label('id'), Artist.name.label('name')).\
        filter(Artist.name.ilike(f'%{search_term}%')).all()
    response = {}
    search_list = list(searchesult)
    response['count'] = len(search_list)

    datalist = []
    for result in search_list:
        cols = result.keys()
        tempdict = {}
        for col in cols:
            tempdict[col] = result[col]
        datalist.append(tempdict)
    response['data'] = datalist

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    # Using raw sql to enable jinja2 template compatibility by using `AS`
    venues = Venue.query.with_entities(
        Venue.venue_id, Venue.image_link, Venue.name).subquery('venue')
    shows = Shows.query.subquery('shows')
    psTable = Shows.query.with_entities(Shows.show_id, Shows.venue_id, Shows.artist_id, Shows.start_time, venues).join(venues).\
        filter(Shows.start_time < db.func.current_date()
               ).filter(Shows.artist_id == artist_id)
    upsTable = Shows.query.with_entities(Shows.show_id, Shows.venue_id, Shows.artist_id, Shows.start_time, venues).join(venues).\
        filter(Shows.start_time > db.func.current_date()
               ).filter(Shows.artist_id == artist_id)
    aTable = db.session.query(Artist).filter(
        Artist.artist_id == artist_id).all()[0]

    artist = {}
    try:
        v_col_key = [col.key for col in aTable.__table__.columns]
    except IndexError:
        v_col_key = []

    for v_col in v_col_key:
        artist[f"{v_col}"] = aTable.__getattribute__(f"{v_col}")
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

    artist["past_shows"] = ps
    artist["upcoming_shows"] = ups
    artist["past_shows_count"] = len(ps)
    artist["upcoming_shows_count"] = len(ups)

    return render_template("pages/show_artist.html", artist=artist)


#  Update
#  ----------------------------------------------------------------


@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.with_entities(Artist.artist_id.label('id'), Artist.name, Artist.genres,
                                        Artist.city, Artist.state, Artist.phone, Artist.website,
                                        Artist.facebook_link, Artist.seeking_venue, Artist.seeking_description, Artist.image_link).\
        filter(Artist.artist_id == artist_id).all()[0]

    default_genres = artist["genres"]
    form = ArtistForm(state=artist["state"], genres=default_genres)
    # TODO: populate form with fields from artist with ID <artist_id>

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    result = request.form
    query_filter = db.session.query(Artist).filter(
        Artist.artist_id == artist_id)

    query_filter.update(
        {
            Artist.name: result["name"],
            Artist.genres: result.getlist("genres"),
            Artist.city: result["city"],
            Artist.state: result["state"],
            Artist.phone: result["phone"],
            Artist.website: result["website_link"],
            Artist.facebook_link: result["facebook_link"],
            Artist.seeking_venue: checkboxget(result, 'seeking_venue'),
            Artist.image_link: result["image_link"],
            Artist.seeking_description: result["seeking_description"],
        }
    )
    db.session.commit()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.with_entities(Venue.venue_id.label('id'), Venue.name, Venue.genres,
                                      Venue.address, Venue.city, Venue.state, Venue.phone, Venue.website,
                                      Venue.facebook_link, Venue.seeking_talent, Venue.seeking_description, Venue.image_link).\
        filter(Venue.venue_id == venue_id).all()[0]

    default_genres = venue["genres"]
    form = VenueForm(state=venue["state"], genres=default_genres)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    result = request.form
    print(result)
    query_filter = db.session.query(Venue).filter(Venue.venue_id == venue_id)

    query_filter.update(
        {
            Venue.name: result["name"],
            Venue.genres: result.getlist('genres'),
            Venue.address: result["address"],
            Venue.city: result["city"],
            Venue.state: result["state"],
            Venue.phone: result["phone"],
            Venue.website: result["website_link"],
            Venue.facebook_link: result["facebook_link"],
            Venue.seeking_talent: checkboxget(result, 'seeking_talent'),
            Venue.image_link: result["image_link"],
            Venue.seeking_description: result["seeking_description"],
        }
    )
    db.session.commit()
    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    result = request.form
    allid = Artist.query.with_entities(Artist.artist_id).all()
    ids = [int(id['artist_id']) for id in allid]
    ids.sort()
    ini = 1
    for id in ids:
        if ini < id:
            ini = ini
            break
        else:
            ini += 1
    try:
        artist = Artist(artist_id=ini, name=result["name"], genres=result.getlist('genres'),
                        city=result["city"], state=result["state"],
                        phone=result["phone"], website=result["website_link"],
                        facebook_link=result["facebook_link"],
                        seeking_venue=checkboxget(result, 'seeking_venue'),
                        image_link=result["image_link"], seeking_description=result["seeking_description"])
        db.session.add(artist)
        db.session.commit()
        flash("Artist " + result["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              result["name"] + ' could not be listed.')
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    venue = Venue.query.with_entities(
        Venue.venue_id, Venue.name.label('venue_name')).subquery('venue')
    artist = Artist.query.with_entities(
        Artist.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link')).subquery('artist')
    ps_list = Shows.query.with_entities(venue, artist, Shows.show_id, Shows.start_time).join(venue).\
        join(artist).order_by(db.asc(Shows.start_time)).all()

    data = []
    for show in ps_list:
        cols = show.keys()
        tempdict = {}
        for col in cols:
            tempdict[col] = show[col]
        data.append(tempdict)
    print(data)
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    result = request.form
    artist_data = Artist.query.with_entities(Artist.artist_id, Artist.name, Artist.image_link).\
        filter(Artist.artist_id == result['artist_id']).all()
    venue_data = Venue.query.with_entities(Venue.venue_id).\
        filter(Venue.venue_id == result['venue_id']).all()
    allid = Shows.query.with_entities(Shows.show_id).all()

    artistlist = list(artist_data)
    venuelist = list(venue_data)
    ids = [int(id['show_id']) for id in allid]
    ids.sort()
    ini = 1
    for id in ids:
        if ini < id:
            ini = ini
            break
        else:
            ini += 1
    if artistlist and venuelist:
        art_id = artistlist[0]['artist_id']
        art_name = artistlist[0]['name']
        art_imagelink = artistlist[0]['image_link']
        ven_id = venuelist[0]['venue_id']
        start_time = format_date(result['start_time'])
        print(art_id, art_name, art_imagelink, ven_id, start_time)
        show = Shows(show_id=ini, artist_id=art_id, artist_name=art_name,
                     artist_image_link=art_imagelink, venue_id=ven_id,
                     start_time=start_time)
        try:
            db.session.add(show)
            db.session.commit()
            flash("Show was successfully listed!")
        except:
            db.session.rollback()
            flash('An error occurred. Show could not be listed.')
    else:
        print(artistlist)
        flash(f'An error occurred. Artist: {result["artist_id"]} and Venue: {result["venue_id"]} doesn\'t exist')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run(debug=True)

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
