from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy

Base = declarative_base()
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user') 

class Creator(db.Model):
    __tablename__ = 'creators'
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='creator')

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='admin')


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    album_name = db.Column(db.String(100), nullable=False)
    album_genre = db.Column(db.String(50), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    creator_username = db.Column(db.String(100), db.ForeignKey('creators.username'), nullable=False)
    songs = db.relationship('Song', secondary='album_song_association', back_populates='albums')

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(50), nullable=False)
    creator_username = db.Column(db.String(100), db.ForeignKey('creators.username'), nullable=False)
    albums = db.relationship('Album', secondary='album_song_association', back_populates='songs')
    playlists = db.relationship('Playlist', secondary='playlist_song_association', back_populates='songs')


    def __repr__(self):
        return f"Song(id={self.id}, song_name={self.song_name}, artist_name={self.artist_name}, " \
               f"duration={self.duration}, lyrics={self.lyrics}, language={self.language}, " \
               f"creator_username={self.creator_username})"


class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playlist_name = db.Column(db.String(100), nullable=False)
    playlist_created_by = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    songs = db.relationship('Song', secondary='playlist_song_association', back_populates='playlists')
    



class AlbumSongAssociation(db.Model):
    __tablename__ = 'album_song_association'
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)

class PlaylistSongAssociation(db.Model):
    __tablename__ = 'playlist_song_association'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), primary_key=True)




