# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import logging
from email.mime import image
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import (Response, flash, redirect, render_template, request,
                   url_for)
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
def sqlarraytolist(string):
    string = string.strip()
    string = string.replace(", ", ",")
    return string.split(",")


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
    stategroup = db.session.execute(
        """SELECT CITY, STATE,
		COUNT(*) AS VENUES
		FROM VENUE
		GROUP BY CITY, STATE"""
    )
    venuesresult = db.session.execute(
        """SELECT VENUE.VENUE_ID AS ID, VENUE.NAME,
            VENUE.STATE, VENUE.CITY,
            COALESCE(UPCOMING.NUM_UPCOMING_SHOWS, 0) AS NUM_UPCOMING_SHOWS
            FROM VENUE LEFT JOIN (SELECT VENUE_ID, COUNT(*) AS NUM_UPCOMING_SHOWS
            FROM SHOWS where shows.start_time > Current_date GROUP BY VENUE_ID)
            AS UPCOMING ON VENUE.VENUE_ID = UPCOMING.VENUE_ID"""
    )
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
    seresult = db.session.execute(f"""
                                SELECT VENUE.VENUE_ID AS ID,
                                VENUE.NAME AS NAME,
                                COALESCE(UPCOMING.NUM_UPCOMING_SHOWS,0)
                                AS NUM_UPCOMING_SHOWS
                                FROM VENUE LEFT JOIN (SELECT VENUE_ID,
                                COUNT(*) AS NUM_UPCOMING_SHOWS FROM SHOWS
                                WHERE SHOWS.START_TIME > CURRENT_DATE
                                GROUP BY VENUE_ID)
                                AS UPCOMING ON VENUE.VENUE_ID = UPCOMING.VENUE_ID
                                WHERE LOWER(VENUE.NAME) like '%{search_term}%'
                                """
                                  )

    response = {}
    search_list = list(seresult)
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
        if v_col == "genres":
            string = vTable.__getattribute__(f"{v_col}")
            strarr = sqlarraytolist(string)
            venue[f"{v_col}"] = strarr
        else:
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
    allid = db.session.execute('SELECT VENUE_ID FROM VENUE')
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
        venue = Venue(venue_id=ini, name=result["name"], genres=",".join(result.getlist('genres')),
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


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------


@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    artistresult = db.session.execute("""SELECT ARTIST.ARTIST_ID AS ID,
                                        ARTIST.NAME FROM ARTIST
                                        ORDER BY ARTIST.ARTIST_ID ASC"""
                                      )
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
    seresult = db.session.execute(f"""                               
                                SELECT ARTIST.ARTIST_ID AS ID,
                                ARTIST.NAME AS NAME,
                                COALESCE(UPCOMING.NUM_UPCOMING_SHOWS,0)
                                AS NUM_UPCOMING_SHOWS FROM ARTIST LEFT JOIN
                                (SELECT ARTIST_ID, COUNT(*) AS NUM_UPCOMING_SHOWS
                                FROM SHOWS WHERE SHOWS.START_TIME > CURRENT_DATE
                                GROUP BY ARTIST_ID)
                                AS UPCOMING ON ARTIST.ARTIST_ID = UPCOMING.ARTIST_ID
                                WHERE LOWER(ARTIST.NAME) like '%{search_term}%'"""
                                  )
    response = {}
    search_list = list(seresult)
    response['count'] = len(search_list)

    datalist = []
    for result in search_list:
        cols = result.keys()
        tempdict = {}
        for col in cols:
            tempdict[col] = result[col]
        datalist.append(tempdict)
    response['data'] = datalist
    print(datalist)

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
    psTable = db.session.execute(
        f"""SELECT * FROM SHOWS 
            INNER JOIN (SELECT VENUE.VENUE_ID AS VENUE_ID,
            VENUE.IMAGE_LINK AS VENUE_IMAGE_LINK,
            VENUE.NAME AS VENUE_NAME FROM VENUE)
            AS VENUE ON VENUE.VENUE_ID = SHOWS.VENUE_ID 
            WHERE SHOWS.ARTIST_ID = {artist_id} 
            AND SHOWS.START_TIME < CURRENT_DATE"""
    )
    upsTable = db.session.execute(
        f"""SELECT * FROM SHOWS 
            INNER JOIN (SELECT VENUE.VENUE_ID AS VENUE_ID,
            VENUE.IMAGE_LINK AS VENUE_IMAGE_LINK,
            VENUE.NAME AS VENUE_NAME FROM VENUE)
            AS VENUE ON VENUE.VENUE_ID = SHOWS.VENUE_ID 
            WHERE SHOWS.ARTIST_ID = {artist_id} 
            AND SHOWS.START_TIME > CURRENT_DATE"""
    )
    aTable = db.session.query(Artist).filter(
        Artist.artist_id == artist_id).all()[0]

    artist = {}
    try:
        v_col_key = [col.key for col in aTable.__table__.columns]
    except IndexError:
        v_col_key = []

    for v_col in v_col_key:
        if v_col == "genres":
            strarr = sqlarraytolist(aTable.__getattribute__(f"{v_col}"))
            artist[f"{v_col}"] = strarr
        else:
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
    artist = db.session.execute(
        f"""SELECT ARTIST_ID AS ID, NAME, GENRES,
    CITY, STATE, PHONE, WEBSITE, FACEBOOK_LINK, SEEKING_VENUE,
    SEEKING_DESCRIPTION, IMAGE_LINK
    FROM ARTIST
    WHERE ARTIST_ID = {artist_id}"""
    )
    artist = next(artist)
    default_genres = sqlarraytolist(artist["genres"])
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
            Artist.genres: ",".join(result.getlist("genres")),
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
    venue = db.session.execute(
        f"""SELECT VENUE_ID AS ID, NAME, GENRES,
    ADDRESS, CITY, STATE, PHONE, WEBSITE, FACEBOOK_LINK, SEEKING_TALENT,
    SEEKING_DESCRIPTION, IMAGE_LINK
    FROM VENUE
    WHERE VENUE_ID = {venue_id}"""
    )
    venue = next(venue)
    default_genres = sqlarraytolist(venue["genres"])
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
            Venue.genres: ",".join(result.getlist('genres')),
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
    allid = db.session.execute('SELECT ARTIST_ID FROM ARTIST')
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
        artist = Artist(artist_id=ini, name=result["name"], genres=",".join(result.getlist('genres')),
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
    shows_result = db.session.execute(f"""SELECT VENUE.VENUE_ID AS VENUE_ID,
                                    VENUE.NAME AS VENUE_NAME, ARTIST_ID,
                                    ARTIST_NAME, ARTIST_IMAGE_LINK, START_TIME
                                    FROM SHOWS
                                    JOIN VENUE ON SHOWS.VENUE_ID = VENUE.VENUE_ID
                                    ORDER BY START_TIME ASC"""
                                           )
  
    ps_list = list(shows_result)

    data = []
    for show in ps_list:
        cols = show.keys()
        tempdict = {}
        for col in cols:
            tempdict[col] = show[col]
        data.append(tempdict)
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
    artist_data = db.session.execute(f'''SELECT ARTIST_ID, NAME, IMAGE_LINK FROM  ARTIST
                        WHERE ARTIST_ID = {result['artist_id']}''')
    venue_data = db.session.execute(f'''SELECT VENUE_ID FROM  VENUE
                        WHERE VENUE_ID = {result['venue_id']}''')
    allid = db.session.execute('SELECT SHOW_ID FROM SHOWS')
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
