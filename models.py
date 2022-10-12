import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120),nullable=False)
    image_link = db.Column(db.String(500))
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=True)
    seeking_description = db.Column(db.String(250))
    shows = db.relationship('Show', backref='venues', lazy=True)

    def __repr__(self):
          return f"<Venue {self.id} name: {self.name}>"   

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artists', lazy=True)
    want_venue =db.Column(db.Boolean, default=False)
    description = db.Column(db.String)
    def __repr__(self):
        return f"<Artist {self.id} name: {self.name}>"

class Show(db.Model):
  __tablename__ = 'Shows'
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow())   
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False) 
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
   
  def __repr__(self):
    return f'<Show {self.id} {self.start_time}, Artist {self.artist_id}, Venue {self.venue_id}>'