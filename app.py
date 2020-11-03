# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import psycopg2
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
# TODO: connect to a local postgresql database
migrate = Migrate(app, db, compare_type=True)


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(), dimensions=1), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.String(50), nullable=True, default=True)
    seeking_description = db.Column(db.String(120), nullable=False,
                                    default='We are looking for an exciting artist to perform here!')
    reltion_Venue_id = db.relationship('Show', backref='Venue',lazy=True,foreign_keys = [id,name], primaryjoin="Venue.id == Show.venue_id")

    def __repr__(self):
        return f'<Venue Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def city_and_state(self):
        return {'city': self.city, 'state': self.state, }


    @property
    def get_past_shows(self):
        res = db.session.query(Show).filter((Show.venue_id == self.id)).all()
        if res:
            res = db.session.query(Show).filter((Show.venue_id == self.id), (Show.start_time <= datetime.now())).all()
            return res
        return []

    @property
    def get_past_shows_count(self):
        if self.get_upcoming_shows:
            num_past_shows = len(self.get_past_shows)
            return num_past_shows
        else:
            return 0

    @property
    def get_upcoming_shows(self):
        res = db.session.query(Show).filter((Show.venue_id == self.id)).all()
        if res:
            res = db.session.query(Show).filter((Show.venue_id == self.id), (Show.start_time > datetime.now())).all()
            return res
        return []

    @property
    def get_upcoming_shows_count(self):
        if self.get_upcoming_shows:
            num_upcoming_shows = len(self.get_upcoming_shows)
            return num_upcoming_shows
        else:
            return 0


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    data1 = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.ARRAY(db.String(), dimensions=1), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    website = db.Column(db.String(), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.String(50), nullable=False, default=True)
    seeking_description = db.Column(db.String(120), nullable=False,
                                    default='We are looking to perform at an exciting venue!')
    relation_artist_id = db.relationship('Show', backref='Artist', lazy=True,foreign_keys = [id,name],primaryjoin="Artist.id == Show.artist_id")

    def __repr__(self):
        return f'<Artist Name: {self.name}, City: {self.city}, State: {self.state}>'

    @property
    def get_past_shows(self):
        res = db.session.query(Show).filter((Show.artist_id == self.id)).all()
        if res:
            res = db.session.query(Show).filter((Show.artist_id == self.id), (Show.start_time <= datetime.now())).all()
            return res
        return []

    @property
    def get_past_shows_count(self):
        if self.get_upcoming_shows:
            num_past_shows = len(self.get_past_shows)
            return num_past_shows
        else:
            return 0

    @property
    def get_upcoming_shows(self):
        res = db.session.query(Show).filter((Show.artist_id == self.id)).all()
        if res:
            res = db.session.query(Show).filter((Show.artist_id == self.id), (Show.start_time > datetime.now())).all()
            return res
        return []

    @property
    def get_upcoming_shows_count(self):
        if self.get_upcoming_shows:
            num_upcoming_shows = len(self.get_upcoming_shows)
            return num_upcoming_shows
        else:
            return 0

    @property
    def basic_details(self):
        return {'id': self.id, 'name': self.name, 'city': self.city, 'state': self.state}


    # TODO: implement any missing fields, as a database migration using Flask-Migrate


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=True)  # False
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=True)  # False
    venue_name = db.Column(db.String, db.ForeignKey('Venue.name'), nullable=True)  # False
    artist_name = db.Column(db.String, db.ForeignKey('Artist.name'), nullable=True)  # False
    start_time = db.Column(db.DateTime(),nullable=True)

    @property
    def get_basic_artist(self):
        #         "artist_id": 6,
        #         "artist_name": "The Wild Sax Band",
        #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        #         "start_time": "2035-04-01T20:00:00.000Z"
        return {
                "artist_id": self.artist_id,
                "artist_name": self.artist_name,
                "artist_image_link": db.session.query(Artist).get(self.artist_id).image_link,
                "venue_image_link": db.session.query(Venue).get(self.venue_id).image_link,
                "start_time": str(self.start_time)
        }

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    # finished
    try:
        data = []
        areas = [v.city_and_state for v in
                 db.session.query(Venue).distinct(Venue.city, Venue.state).order_by(Venue.city, Venue.state).all()]
        for area in areas:
            _ = db.session.query(Venue).filter(Venue.city == area.get('city'),
                                               Venue.state == area.get('state')
                                               ).order_by(Venue.city, Venue.state).all()
            entry = {
                "city": area.get('city'),
                "state": area.get('state'),
                "venues": [{
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": venue.get_upcoming_shows_count,
                } for venue in _]}
            data.append(entry)
    except():
        db.session.rollback()
    finally:
        db.session.close()

    example_data = [{
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
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # finished
    try:
        search_term = request.form.get('search_term', '')  # get user searching input

        results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()  # get all possible matches

        response = {
            "count": len(results),
            "data": [{
                "id": v.id,
                "name": v.name,
                "num_upcoming_shows": v.get_upcoming_shows_count
            } for v in results]
        }
        print(response)
        return render_template('pages/search_venues.html', results=response,
                               search_term=request.form.get('search_term', ''))
    except:
        flash('An error occurred while searching, please try again')
        return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    all_venues = db.session.query(Venue).all()
    venue_list = []
    for venue in all_venues:
        entry = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": [show.get_basic_artist for show in venue.get_past_shows],
            "upcoming_shows": [show.get_basic_artist for show in venue.get_upcoming_shows],
            "past_shows_count": venue.get_past_shows_count,
            "upcoming_shows_count": venue.get_upcoming_shows_count,
        }
        venue_list.append(entry)
    data = list(filter(lambda d: d['id'] == venue_id, venue_list))[0]

    # data1 = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #     "past_shows": [{
    #         "artist_id": 4,
    #         "artist_name": "Guns N Petals",
    #         "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 2,
    #     "name": "The Dueling Pianos Bar",
    #     "genres": ["Classical", "R&B", "Hip-Hop"],
    #     "address": "335 Delancey Street",
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "914-003-1132",
    #     "website": "https://www.theduelingpianos.com",
    #     "facebook_link": "https://www.facebook.com/theduelingpianos",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 3,
    #     "name": "Park Square Live Music & Coffee",
    #     "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    #     "address": "34 Whiskey Moore Ave",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "415-000-1234",
    #     "website": "https://www.parksquarelivemusicandcoffee.com",
    #     "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    #     "seeking_talent": False,
    #     "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #     "past_shows": [{
    #         "artist_id": 5,
    #         "artist_name": "Matt Quevedo",
    #         "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [{
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "artist_id": 6,
    #         "artist_name": "The Wild Sax Band",
    #         "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 1,
    # }
    # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    return render_template('pages/show_venue.html', venue=data)


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
    #  finished

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    address = request.form['address']
    genres = request.form.getlist(
        'genres')  # if the form data is an array, get the data using get list, otherwise, you get the first
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = request.form['seeking_talent']
    seeking_description = request.form['seeking_description']

    try:
        v = Venue(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                  address=address, image_link=image_link, website=website, seeking_talent=seeking_talent,
                  seeking_description=seeking_description)

        db.session.add(v)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except():
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
        show = db.session.query(Show).filter(Show.venue_id == venue_id)
        q = db.session.query(Venue).filter(Venue.id == venue_id)
        show.delete()
        q.delete()
        db.session.commit()
    except():
        db.session.rollback()
        flash('Something goes wrong')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned    from querying the database
    """
  Insert some basic information
  """
    # finished
    try:
        data = []  # id and name
        artists = [v.basic_details for v in db.session.query(Artist).all()]
        for _ in artists:
            entry = {
                "id": _.get('id'),
                "name": _.get('name'),
                "state": _.get('state'),
                "city": _.get('city'),
            }
            data.append(entry)
        print(data)
    finally:
        db.session.close()
    print(data)
    #     artist_info = [v.basic_details for v in db.session.query(Artist).distinct(Artist.name,Artist.id).order_by(Artist.id).all()]
    #     for info in artist_info:
    #         artist_with_same_name = db.session.query(Artist).filter(Artist.name == info.get('name'),
    #                                        ).order_by(Artist.id).all()
    #         entry = {
    #             "artists": [{
    #                 "id": artist.id,
    #                 "name": artist.name,
    #             } for artist in artist_with_same_name]}
    #         data.append(entry)
    # finally:
    #     db.session.close()
    # print(data)
    example_data = [{
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
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    try:
        search_term = request.form.get('search_term', '')  # get user searching input
        artists = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
        response = {
            "count": len(artists),
            "data": [{
                "id": _.id,
                "name": _.name,
                "num_upcoming_shows": _.get_upcoming_shows_count,
            } for _ in artists]
        }
    finally:
        db.session.close()
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    all_artists = db.session.query(Artist).all()
    artist_list = []
    for artist in all_artists:
        entry = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": [show.get_basic_artist for show in artist.get_past_shows],
            "upcoming_shows": [show.get_basic_artist for show in artist.get_upcoming_shows],
            "past_shows_count": artist.get_past_shows_count,
            "upcoming_shows_count": artist.get_upcoming_shows_count,
        }
        artist_list.append(entry)
    data = list(filter(lambda d: d['id'] == artist_id, artist_list))[0]
    # data1 = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "past_shows": [{
    #         "venue_id": 1,
    #         "venue_name": "The Musical Hop",
    #         "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #         "start_time": "2019-05-21T21:30:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data2 = {
    #     "id": 5,
    #     "name": "Matt Quevedo",
    #     "genres": ["Jazz"],
    #     "city": "New York",
    #     "state": "NY",
    #     "phone": "300-400-5000",
    #     "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "past_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2019-06-15T23:00:00.000Z"
    #     }],
    #     "upcoming_shows": [],
    #     "past_shows_count": 1,
    #     "upcoming_shows_count": 0,
    # }
    # data3 = {
    #     "id": 6,
    #     "name": "The Wild Sax Band",
    #     "genres": ["Jazz", "Classical"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "432-325-5432",
    #     "seeking_venue": False,
    #     "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "past_shows": [],
    #     "upcoming_shows": [{
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-01T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-08T20:00:00.000Z"
    #     }, {
    #         "venue_id": 3,
    #         "venue_name": "Park Square Live Music & Coffee",
    #         "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    #         "start_time": "2035-04-15T20:00:00.000Z"
    #     }],
    #     "past_shows_count": 0,
    #     "upcoming_shows_count": 3,
    # }
    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = db.session.query(Artist).get(artist_id)

    form = ArtistForm(
        name=artist.name,
        city=artist.city,
        state=artist.state,
        genres=artist.genres,
        phone=artist.phone,
        facebook_link=artist.facebook_link,
        website=artist.website,
        image_link=artist.image_link,
        seeking_venue=artist.seeking_venue,
        seeking_description=artist.seeking_description)
    if artist:
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    else:
        return render_template('errors/404.html')
    # TODO: populate form with fields from artist with ID <artist_id>


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        artist = db.session.query(Artist).get(artist_id)
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist(
            'genres')  # if the form data is an array, get the data using get list, otherwise, you get the first
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.facebook_link = request.form['facebook_link']
        artist.seeking_venue = request.form['seeking_venue']
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except():
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be modified.')
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = db.session.query(Venue).filter(Venue.id == venue_id).first()
    form = VenueForm(
        name=venue.name,
        city=venue.city,
        state=venue.state,
        genres=venue.genres,
        address=venue.address,
        phone=venue.phone,
        facebook_link=venue.facebook_link,
        website=venue.website,
        image_link=venue.image_link,
        seeking_talent=venue.seeking_talent,
        seeking_description=venue.seeking_description)
    if venue:
        return render_template('forms/edit_venue.html', form=form, venue=venue)
    else:
        return render_template('errors/404.html')
    # venue = {
    #     "id": 1,
    #     "name": "The Musical Hop",
    #     "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    #     "address": "1015 Folsom Street",
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "123-123-1234",
    #     "website": "https://www.themusicalhop.com",
    #     "facebook_link": "https://www.facebook.com/TheMusicalHop",
    #     "seeking_talent": True,
    #     "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    #     "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    # }
    # TODO: populate form with values from venue with ID <venue_id>
    # finished


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing

    try:
        venue = db.session.query(Venue).get(venue_id)
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.phone = request.form['phone']
        venue.address = request.form['address']
        venue.genres = request.form.getlist(
            'genres')  # if the form data is an array, get the data using get list, otherwise, you get the first
        venue.image_link = request.form['image_link']
        venue.website = request.form['website']
        venue.facebook_link = request.form['facebook_link']
        venue.seeking_talent = request.form['seeking_talent']
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except():
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be modified.')
    finally:
        db.session.close()

    # venue record with ID <venue_id> using the new attributes
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
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist(
        'genres')  # if the form data is an array, get the data using get list, otherwise, you get the first
    image_link = request.form['image_link']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = request.form['seeking_venue']
    seeking_description = request.form['seeking_description']

    try:
        a = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,
                   image_link=image_link, website=website, seeking_venue=seeking_venue,
                   seeking_description=seeking_description)

        db.session.add(a)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except():
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    try:
        shows = db.session.query(Show).order_by(Show.id).all()
        data = [
            {
                    "venue_id": show.venue_id,
                    "venue_name": show.venue_name,
                    "artist_id": show.artist_id,
                    "artist_name": show.artist_name,
                    "artist_image_link": db.session.query(Artist).get(show.artist_id).image_link,
                    "start_time": str(show.start_time)
            } for show in shows
        ]
    except():
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    # example_data = [{
    #     "venue_id": 1,
    #     "venue_name": "The Musical Hop",
    #     "artist_id": 4,
    #     "artist_name": "Guns N Petals",
    #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    #     "start_time": "2019-05-21T21:30:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 5,
    #     "artist_name": "Matt Quevedo",
    #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    #     "start_time": "2019-06-15T23:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-01T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-08T20:00:00.000Z"
    # }, {
    #     "venue_id": 3,
    #     "venue_name": "Park Square Live Music & Coffee",
    #     "artist_id": 6,
    #     "artist_name": "The Wild Sax Band",
    #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    #     "start_time": "2035-04-15T20:00:00.000Z"
    # }]
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

    try:
        show = Show(
            artist_id=request.form['artist_id'],
            venue_id = request.form['venue_id'],
            artist_name=db.session.query(Artist).get(request.form['artist_id']).name,
            venue_name=db.session.query(Venue).get(request.form['venue_id']).name,
            start_time=request.form['start_time']
        )
        db.session.add(show)
        db.session.commit()
        flash('Show belongs to artist num: ' + request.form['artist_id'] + ' was successfully listed!')
    except():
        flash('An error occurred. Show ' + request.form['id'] + ' could not be listed.')
    finally:
        db.session.close()
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
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
