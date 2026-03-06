import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, jsonify, request, url_for, session, redirect
import pprint
import os
import signal

from playlists_manager.db import Database

app = Flask(__name__)

# Set the name of the session cookie
app.config['SESSION_COOKIE_NAME'] = 'Spotify Cookie'

# Set a random secret key to sign the cookie
app.secret_key = 'YOUR_SECRET_KEY'

# Set the key for the token info in the session dictionary
TOKEN_INFO = 'token_info'

def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = '',
        client_secret = '',
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

@app.route('/')
def login():
    #Spotifu oauth instance and get the authorization URL
    auth_url = create_spotify_oauth().get_authorize_url()
    # redirect user to authorization URL
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    # clear the session
    session.clear()
    # get the authorization code from the request parameters
    code = request.args.get('code')
    # exchange the authorization code from the request parameters
    token_info = create_spotify_oauth().get_access_token(code)
    #save the token info in the session
    session[TOKEN_INFO] = token_info
    # redirect the user to the save_discover_weekly route
    return redirect(url_for('createPlaylist',_external= True))

@app.route('/createPlaylist')
def createPlaylist():
    try:
        TOKEN_INFO = get_token()
    except:
        print('User not logged in')
        return redirect("/")
    
    
    sp = spotipy.Spotify(auth=TOKEN_INFO['access_token'])
    user_id = sp.current_user()['id'] 

    # Get playlist name and data Stored from the Dabaseses
    db = Database()
    db.connect()
    print(db.restore)
    playlist_name, song_data = db.playlist_name_and_song()
       

    # Create New playlist with relevant name
    new_playlist = sp.user_playlist_create(user_id, playlist_name , public=False )

    # Fetch id of playlist we just created
    new_playlist_id = new_playlist['id'] 

    if song_data[0][2] == "ON-RESTORE":
        #This means its in retore more and restore mode only returns song_uris
        add_tracks_response =  sp.user_playlist_add_tracks(user_id, new_playlist_id, [song[6] for song in song_data], None)
        if 'snapshot_id' in add_tracks_response:
            print(F"Sucessully Restored your Playlist {playlist_name}")
            return "Done"
    else:
                                                        # my user id     anyplaylists ID     any song uris
        add_tracks_response = sp.user_playlist_add_tracks(user_id, new_playlist_id, [song[6] for song in song_data], None)

    print(f"New playlist created with ID: {new_playlist_id}")


    print(add_tracks_response)
    if 'snapshot_id' in add_tracks_response:  # Spotipy returns a dict like {'snapshot_id': 'AAAAA9c/xGUgMabGXCWof2Mej3eeUWfd'}
        db.create_playlist_with_songs(playlist_name, song_data)
        message = f'Playlist "{playlist_name}" successfully created with ID: {new_playlist_id}'
        # time.sleep(6)
        shutdown_server()
        return message, shutdown_server()  # Return success message with 200 status code
    else:
        message = 'Failed to add tracks to the playlist.'
        # time.sleep(6)
        # shutdown_server()
        return message, 400
    
    return ('Playlist successsully created')



    

    return f'Playlist "{get_playlist_name}" created successfully with ID: {new_playlist_id}'

def shutdown_server():
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)
    
                    
# @app.route('/saveDiscoverWeekly')
# def save_discover_weekly():
#     try:
#         # get the token info from the session
#         token_info= get_token()
#     except:
#         # if the token info is not found, redirect the user to the login route
#         print('User not logged in')
#         return redirect("/")
    
#     # spotipy instance with access token
#     sp = spotipy.Spotify(auth=token_info['access_token'])

#     # get your palylists

    

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        # if the token info is not found, redirect the user to the login route
        redirect(url_for('login',_external=False))

    # check if then token is expired and refresh itif necessary
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotipy_oauth = create_spotify_oauth()
        token_info = spotipy_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info

app.run(debug=True)





