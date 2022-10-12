import json
import dateutil.parser
import babel
from flask import(
  Flask, 
  render_template, 
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
  )
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import db,Venue,Artist,Show 
import datetime
import config
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db.init_app(app)


migrate=Migrate (app, db)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

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
    venues = Venue.query.all()                             
    areas = set()
                                  
    for venue in venues:
        areas.add((venue.city, venue.state))

    data=[]                               
    for city,state in areas:
         data.append({
             "city":city,
             "state":state,
             "venues": []
         }) 

    
    for venue in venues:
      for venue_area in data:                             
         if venue.state == venue_area['state'] and venue.city == venue_area['city']:                          
            upcoming_shows_count = len(Show.query.join(Venue).filter(Show.start_time > datetime.datetime.utcnow()).all())

            venue_area['venues'].append({
                 "id":venue.id,
                 "name":venue.name,
                 "num_upcoming_shows":upcoming_shows_count
             })
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  searched_term = request.form.get('search_term') 
  search_result = Venue.query.filter(Venue.name.ilike('%' + searched_term + '%')).all()
  search_array= []

  for data in search_result:
    num_upcoming_shows= Show.query.filter(Show.venue_id == data.id).count() 
    search_array.append({
      "id":data.id,
      "name":data.name,
     "num_upcoming_shows":num_upcoming_shows 
    })

  response={
    "count": len(search_array),
    "data": search_array
  }      
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter(Venue.id == venue_id ).first()
  past_shows_list = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  upcoming_shows_list = Show.query.join(Venue, Show.venue_id == venue_id).filter(Show.start_time > datetime.datetime.utcnow()).all()
     

  past_shows=[]
  for show in past_shows_list:
    past_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link":show.artists.image_link,
      "start_time": show.start_time
    })
  
  
  upcoming_shows=[]
  for show in upcoming_shows_list:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link":show.artists.image_link,
      "start_time": show.start_time
    })


  data ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city":venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows), 
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  seeking_talent = True if request.form.get('seeking_talent') =='y' else False 

  venue_form =VenueForm(request.form)
  if venue_form.validate():
    
    try:
      new_venue = Venue(name=name,city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link,seeking_description=seeking_description,seeking_talent=seeking_talent)
      db.session.add(new_venue)
      db.session.commit()
      
      flash('Venue ' + new_venue.name + ' was successfully listed!')
    except:
      db.session.rollback()
    
      flash('An error occurred. Venue ' + new_venue.name+ ' could not be listed.','error')
    finally:
      db.session.close()
    
      return render_template('pages/home.html')
  else:
    flash('Form Inputs Invalid please check again')          
  
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/', methods=['DELETE'])
def delete_venue(venue_id):

  venue = Venue.query.filter(Venue.id == venue_id).first()
  
  try:
    for show in venue.shows:
      db.session.delete(show)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was deleted')
  except:
    db.session.rollback()
    flash("Error deleting venue")
  finally:
    db.session.close()
  return redirect(url_for('venues'))
         


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  artists = Artist.query.all()
  data = []                                
  for artist in artists: 
        data.append({
        "id": artist.id,  
        "name": artist.name  
       })                                                          
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_query = request.form.get('search_term') 
  search_result = Artist.query.filter(Artist.name.ilike('%' + search_query + '%')).all()
  search_array= []
  for data in search_result:
    search_array.append({
      "id":data.id,
      "name":data.name,
    })

  response={
    "count": len(search_array),
    "data": search_array
  }                       
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.filter(Artist.id == artist_id).first()
  all_past_shows = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time <= datetime.datetime.utcnow()).all()
  all_upcoming_shows = Show.query.join(Artist, Show.artist_id == artist.id).filter(Show.start_time > datetime.datetime.utcnow()).all()

  past_shows=[] 
  for show in all_past_shows:
    past_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "venue_image_link":show.venues.image_link,
      "start_time": show.start_time
    })
  
  upcoming_shows=[]
  for show in all_upcoming_shows:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "venue_image_link":show.venues.image_link,
      "start_time": show.start_time
    })

  data ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city":artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link":artist.facebook_link,
    "seeking_venue":artist.want_venue,
    "seeking_description": artist.description,
    "image_link": artist.image_link,
    "past_shows":  past_shows,
    "upcoming_shows":   upcoming_shows,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows), 
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.filter(Artist.id==artist_id).first()
  form = ArtistForm()

  form.name.data = artist.name
  form.genres.data  = artist.genres
  form.city.data  = artist.city
  form.state.data  = artist.state
  form.phone.data  = artist.phone
  form.image_link.data  = artist.image_link
  form.facebook_link.data  = artist.facebook_link
  form.seeking_venue.data  = artist.want_venue
  form.seeking_description.data  =artist.description
  form.website_link.data = artist.website_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist_form =  ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id==artist_id).first()

  if(artist_form.validate()):
    artist.name = artist_form.name.data
    artist.genres = artist_form.genres.data
    artist.city = artist_form.city.data
    artist.state =artist_form.state.data
    artist.phone = artist_form.phone.data
    artist.image_link = artist_form.image_link.data
    artist.facebook_link = artist_form.facebook_link.data
    artist.description = artist_form.seeking_description.data
    artist.website_link = artist_form.website_link.data
    artist.want_venue = artist_form.seeking_venue.data
    try:
      db.session.commit()
      flash(f'update to artist {artist.name} successfull')
    except:
      db.session.rollback()
      flash('an error occurred while updating')
    finally:
      db.session.close()
    return redirect(url_for('show_artist',artist_id=artist.id))
  else:
    flash('Some fields are Invalid please fill correctly')
                   
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id==venue_id).first()

  form.name.data = venue.name
  form.genres.data  = venue.genres
  form.city.data  = venue.city
  form.address.data = venue.address
  form.state.data  = venue.state
  form.phone.data  = venue.phone
  form.image_link.data  = venue.image_link
  form.facebook_link.data  = venue.facebook_link
  form.seeking_talent.data  = venue.seeking_talent
  form.seeking_description.data  =venue.seeking_description
  form.website_link.data = venue.website_link

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.filter(Venue.id==venue_id).first() # find the venue to be edited
  venue_form =  VenueForm(request.form)
  

  if(venue_form.validate()):
    venue.name = venue_form.name.data
    venue.genres = venue_form.genres.data
    venue.city = venue_form.city.data
    venue.state =venue_form.state.data
    venue.address = venue_form.address.data
    venue.phone = venue_form.phone.data
    venue.image_link = venue_form.image_link.data
    venue.facebook_link = venue_form.facebook_link.data
    venue.seeking_description = venue_form.seeking_description.data
    venue.website_link = venue_form.website_link.data
    venue.seeking_talent = venue_form.seeking_talent.data
    try:
      db.session.commit()
      flash(f'update to venue {venue.name} successfull')
    except:
      db.session.rollback()
      flash(f'An error occured. venue {venue.name} was not updated')
    finally:
      db.session.close()
    return redirect(url_for('show_venue',venue_id=venue.id))
  else:
    flash('please fill the form correctly')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website_link = request.form.get('website_link')
  seeking_description = request.form.get('seeking_description')
  want_venue = True if request.form.get('seeking_venue') =='y' else False 
  
  artist_form =ArtistForm(request.form)
  
  if artist_form.validate():
    
    try:
      new_artist = Artist(name=name,description=seeking_description,city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link,website_link=website_link, image_link=image_link, want_venue=want_venue)
      db.session.add(new_artist)
      db.session.commit()
     
      flash('Artist ' + new_artist.name + ' was successfully listed!')
    except:
      db.session.rollback()
    
      flash('An error occurred. Artist ' + new_artist.name+ ' could not be listed.','error')
    finally:
      db.session.close()
   
    return render_template('pages/home.html')
  else:
    flash('Form Inputs Invalid please check again') 
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  shows = Show.query.all()
  data=[]

  for show in shows:
    data.append({ "venue_id": show.venue_id,
      "venue_name": show.venues.name,
      "artist_id": show.artist_id,
      "artist_name": show.artists.name,
      "artist_image_link":show.artists.image_link,
      "start_time": show.start_time
    }
 )
     
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  new_show = Show(artist_id=artist_id, venue_id=venue_id,start_time=start_time)

  show_form = ShowForm(request.form)


  if show_form.validate():
    try:
      db.session.add(new_show)
      db.session.commit()
  
      flash('Show was successfully listed!')
    except:

      db.session.rollback()
      flash('An error occurred. Show could not be listed.','error')
    finally:
      db.session.close()
    return render_template('pages/home.html')
  else:
    flash('Form Inputs Invalid please check again')       
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

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
