#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import abort
import sys
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
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
# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Venue(db.Model):    # LIEU (French)
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    #TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='listv', lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.image_link} {self.facebook_link}>'
   
class Artist(db.Model):    # Artiste (Fench)
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.String(5)) # seeking_venue = db.Column(db.Boolean, nullable=True, default=False)
    seeking_description = db.Column(db.String(200))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='lista', lazy=True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website} {self.seeking_venue} {self.seeking_description}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):    # Spectacles (Fench)
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)

    def __repr__(self):
      return f'<Show {self.id} {self.start_time} lista {self.artist_id} listv {self.venue_id}>'

# TODO Persist Dat to DataBase
db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/artist/<artist_id>')
def get_list_artists(artist_id):
    return render_template('artists.html',
    artists=Artist.query.filter_by(artist_id=artist_id).order_by('id').all())

'''
@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1))
'''

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  return render_template('pages/venues.html', areas=Venue.query.all())

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
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
  venue_info = Venue.query.filter_by(id=venue_id).first()
  return render_template('pages/show_venue.html', venue=venue_info)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
    error = False
    success = False
    body = {}
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        phone = request.get_json()['phone']
        address = request.get_json()['address']
        image_link= request.get_json()['image_link']
        facebook_link= request.get_json()['facebook_link'] 
        venue = Venue(name=name, city=city, state=state, phone=phone, address=address, image_link=image_link, facebook_link=facebook_link)
        body['id'] = venue.id
        body['name'] = venue.name
        body['city'] = venue.city
        body['state'] = venue.state
        body['phone'] = venue.phone
        body['address'] = venue.address
        body['image_link'] = venue.image_link
        body['facebook_link'] = venue.facebook_link
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        
    finally:
        db.session.close()
    if error == True:
        abort(400)
    else:
        return jsonify(body)
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
  return render_template('pages/artists.html', artists=Artist.query.all())

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
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
  venue = Venue.query.all(),
  artist_info = Artist.query.filter_by(id=artist_id).first()
  return render_template('pages/show_artist.html', artist=artist_info)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', artist=Artist.query.filter_by(id=artist_id).first())

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
# TODO: insert form data as a new Venue record in the db, instead
def create_artist_submission():
    error = False
    success = False
    body = {}
    try:
        name = request.get_json()['name']
        city = request.get_json()['city']
        state = request.get_json()['state']
        phone = request.get_json()['phone']
        genres = request.get_json()['genres']
        website = request.get_json()['website']
        image_link= request.get_json()['image_link']
        facebook_link= request.get_json()['facebook_link'] 
        seeking_venue= request.get_json()['seeking_venue']
        seeking_description= request.get_json()['seeking_description']
        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, website=website, facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
        body['id'] = artist.id
        body['name'] = artist.name
        body['city'] = artist.city
        body['state'] = artist.state
        body['phone'] = artist.phone
        body['genres'] = artist.genres
        body['image_link'] = artist.image_link
        body['website'] = artist.website
        body['facebook_link'] = artist.facebook_link
        body['seeking_venue'] = artist.seeking_venue
        body['seeking_description'] = artist.seeking_description
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        
    finally:
        db.session.close()
    if error == True:
        abort(400)
    else:
        return jsonify(body)
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        #return render_template('pages/home.html')
         # on successful db insert, flash success
        #flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
    # TODO: modify data to be the data object returned from db insertion
        
  
    # DELETE Artist
    """ @app.route('/artist/<artist_id>', methods=['DELETE'])
    def delete_todo(artist_id):
        try:
            Artist.query.filter_by(id=artist_id).delete()
            db.session.commit()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        return jsonify({'success': True}) """


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  return render_template('pages/shows.html', shows=Show.query.all(),artists=Artist.query.all(),venues=Venue.query.all())


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form, artists=Artist.query.all(),venues=Venue.query.all())
  

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
    error = False
    success = False
    body = {}
    try:
        artist_id = request.get_json()['artist_id']
        venue_id = request.get_json()['venue_id']
        start_time = request.get_json()['start_time']
        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        body['id'] = show.id
        body['artist_id'] = show.artist_id
        body['venue_id'] = show.venue_id
        body['start_time'] = show.start_time
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
        
    finally:
        db.session.close()
    if error == True:
        abort(400)
    else:
      return jsonify(body)
        # on successful db insert, flash success
        #flash('Show was successfully listed!')
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        #return render_template('pages/home.html')

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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
