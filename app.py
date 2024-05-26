from flask import Flask, render_template, request, redirect, url_for,session,flash,abort
from models import db, User, Creator, Admin, Playlist
from models import db, Creator, Song,Album, AlbumSongAssociation

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'
db.init_app(app)


def create_admin_user():
    with app.app_context():
        admin_username = 'admin'
        admin_password = 'adminpassword'
        admin_exists = Admin.query.filter_by(username=admin_username).first()

        if not admin_exists:
            admin_user = Admin(username=admin_username, password=admin_password)
            db.session.add(admin_user)
            db.session.commit()

# Initialize the database
with app.app_context():
    db.create_all()
    create_admin_user()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form['fullName']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        location = request.form['location']
        is_creator = request.form['creatorOption'] == 'Yes'

        # Check if the user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', error='Username already taken. Please choose another.')

        # Create a new user or creator based on the user's choice
        if is_creator:
            new_user = Creator(full_name=full_name, username=username, email=email, password=password, location=location)
        else:
            new_user = User(full_name=full_name, username=username, email=email, password=password, location=location)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType'].lower()

        if user_type == 'creator':
            # Check if the user is in the Creator table
            user = Creator.query.filter_by(username=username).first()

            if user and user.password == password:
                # Login successful for creator
                session['user_id'] = user.id
                session['user_type'] = 'creator'
                session['username'] = user.username
                return redirect(url_for('creator_profile', username=user.username))

        elif user_type == 'user':
            # Check if the user is in the User table
            user = User.query.filter_by(username=username).first()

            if user and user.password == password:
                # Login successful for user
                session['user_id'] = user.id
                session['user_type'] = 'user'
                session['username'] = user.username
                return redirect(url_for('user_profile',username=user.username))

        # Invalid username or password
        return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')

@app.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first()
    all_songs = Song.query.all()
    all_albums = Album.query.all()
    playlists = Playlist.query.filter_by(playlist_created_by=username).all()
    return render_template('user_profile.html', user=user, all_songs=all_songs,all_albums=all_albums,playlists=playlists,username=username)


@app.route('/creator_profile/<username>')
def creator_profile(username):
    creator = Creator.query.filter_by(username=username).first()

    if not creator:
        abort(404)  # Creator not found

    # Get the songs created by the current creator
    creator_songs = Song.query.filter_by(creator_username=username).all()
    total_songs = len(creator_songs) if creator else 0

    creator_album = Album.query.filter_by(creator_username=username).all()
    total_album = len(creator_album) if creator else 0

    return render_template('creator_profile.html', creator=creator, songs=creator_songs,total_songs=total_songs,username=session['username'],total_album=total_album)


@app.route('/admin_profile')
def admin_profile():
    return render_template('admin_profile.html')

@app.route('/c_add_song')
def c_add_song():
    username = "Ano"
    if 'username' in session:
            username = session['username']
    creator = Creator.query.filter_by(username=username).first()
    return render_template('c_add_song.html',creator=creator,username=session['username'])  # You need to create this template

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/c_add_song', methods=['POST'])
def add_song():
    if request.method == 'POST':
        # Get form data
        song_name = request.form['song_name']
        artist_name = request.form['artist_name']
        duration = request.form['duration']
        lyrics = request.form['lyrics']
        language = request.form['language']

        creator_username_s = ""

        if 'username' in session:
            creator_username_s = session['username']

        # Create a new song instance and add it to the database
        new_song = Song(
            song_name=song_name,
            artist_name=artist_name,
            duration=duration,
            lyrics=lyrics,
            language=language,
            creator_username=creator_username_s 
        )

        db.session.add(new_song)
        db.session.commit()

        # Redirect to a success page or profile page
        flash('Song added successfully!', 'success')
        return redirect(url_for('creator_profile', username=session['username']))


@app.route('/c_create_album', methods=['GET', 'POST'])
def c_create_album():
    if 'username' in session:
        username = session['username']
    creator = Creator.query.filter_by(username=username).first()
    songs_c = Song.query.filter_by(creator_username=username).all()


    if request.method == 'POST':
        # Get form data
        album_name = request.form['album_name']
        album_genre = request.form['album_genre']
        artist_name = request.form['artist_name']
        selected_songs_ids = request.form.getlist('selected_songs')

        # Create a new album instance and add it to the database
        new_album = Album(
            album_name=album_name,
            album_genre=album_genre,
            artist_name=artist_name,
            creator_username=username
        )

        # Associate selected songs with the album
        for song_id in selected_songs_ids:
            song = Song.query.get(song_id)
            new_album.songs.append(song)

        db.session.add(new_album)
        db.session.commit()

        flash('Album added successfully!', 'success')
        return redirect(url_for('creator_profile', username=username,creator=creator))

    return render_template('c_create_album.html',creator=creator, songs=songs_c,username=username)


# Route to display song details
@app.route('/song_details/<int:song_id>')
def song_details(song_id):
    song = Song.query.get(song_id)
    Username = session['username']

    if song:
        return render_template('song_details.html', song=song,username=Username)
    else:
        flash('Song not found', 'error')
        return redirect(url_for('user_profile'))
    

@app.route('/album_details/<int:album_id>')
def album_details(album_id):
    album = Album.query.get(album_id)

    if album:
        return render_template('album_details.html', album=album)
    else:
        flash('Album not found', 'error')
        return redirect(url_for('user_profile', username=session['username']))


@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        print(request.form)
        playlist_name = request.form['playlist_name']
        selected_song_ids = request.form.getlist('selected_songs')
        playlist_rating = int(request.form['playlist_rating'])

        new_playlist = Playlist(
            playlist_name=playlist_name,
            playlist_created_by=session['username'],
            rating=playlist_rating
        )

        for song_id in selected_song_ids:
            song = Song.query.get(song_id)
            new_playlist.songs.append(song)


        db.session.add(new_playlist)
        db.session.commit()

        flash('Playlist created successfully!', 'success')
        return redirect(url_for('user_profile', username=session['username']))

    # Fetch songs to display in the playlist creation form
    songs = Song.query.all()

    return render_template('create_playlist.html', songs=songs, username=session['username'])


@app.route('/playlist_info/<int:playlist_id>', methods=['GET'])
def playlist_info(playlist_id):
    # Retrieve playlist information based on playlist_id
    playlist = Playlist.query.get(playlist_id)

    # Check if the playlist exists
    if playlist is None:
        flash('Playlist not found!', 'error')
        return redirect(url_for('user_profile', username=session['username']))

    # Pass the playlist information to the template
    return render_template('playlist_info.html', playlist=playlist)



@app.route('/search', methods=['GET'])
def search_song():
    return render_template('search_song.html',username=session['username'])

@app.route('/search_result', methods=['POST'])
def search_song_result():
    search_query = request.form.get('search_query', '')
    search_results = Song.query.filter(Song.song_name.ilike(f'%{search_query}%')).all()

    if not search_results:
        flash('No matching songs found!', 'info')
        return redirect(url_for('search_song'))

    return render_template('search_result.html', search_results=search_results,username=session['username'])
    
@app.route('/c_song_details/<int:song_id>')
def c_song_details(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('c_song_details.html', song=song,username=session['username'])


@app.route('/root_login', methods=['GET', 'POST'])
def root_login():
    if request.method == 'POST':
        #login
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        if admin_username == 'admin' and admin_password == 'adminpassword':
            return redirect(url_for('root_profile'))  

    return render_template('root_login.html')

@app.route('/root_profile')
def root_profile():
    users = User.query.all()
    song = Song.query.all()
    return render_template('root_profile.html', users=users,song=song)



if __name__ == '__main__':
    app.run(debug=True)
