import os
import time
import requests
from flask import Flask, jsonify, request, url_for, session, redirect, render_template, stream_with_context, Response
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import json

from playlists_manager.db import Database
from Models.track import Track

load_dotenv()

app = Flask(__name__)
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'fallback-dev-secret')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB per file

TOKEN_INFO = 'token_info'
SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a', '.wma', '.aiff'}

os.makedirs('data', exist_ok=True)


def get_db():
    """Create a fresh db connection for each request."""
    db = Database()
    db.connect()
    return db


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )


def get_token():
    token_info = session.get(TOKEN_INFO)
    if not token_info:
        return None
    now = int(time.time())
    if token_info['expires_at'] - now < 60:
        token_info = create_spotify_oauth().refresh_access_token(token_info['refresh_token'])
        session[TOKEN_INFO] = token_info
    return token_info

@app.route('/')
def index():
    token_info = get_token()
    if token_info:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('dashboard'))



@app.route('/how-it-works')
def how_it_works():
    return render_template('how_it_works.html')

@app.route('/dashboard')
def dashboard():
    token_info = get_token()
    if not token_info:
        return redirect(url_for('login'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user = sp.current_user()

    db = get_db()
    history = db.history(user['id'])
    db.close()

    return render_template('dashboard.html', user=user, history=history)

@app.route('/set-audd-key', methods=['POST'])
def set_audd_key():
    key = request.json.get('audd_api_key', '').strip()
    if not key:
        return jsonify({'error': 'Key cannot be empty'}), 400
    session['audd_api_key'] = key
    return jsonify({'success': True})

@app.route('/create-playlist', methods=['POST'])
def create_playlist():
    token_info = get_token()
    if not token_info:
        return jsonify({'error': 'Not logged in'}), 401

    playlist_name = request.form.get('playlist_name', '').strip()
    files = request.files.getlist('songs')
    audd_key = session.get('audd_api_key') or os.getenv('AUDD_API_KEY')

    if not audd_key:
        return jsonify({'error': 'Audd.io API key is required. Please enter it in the Settings tab.'}), 400
    if not playlist_name:
        return jsonify({'error': 'Playlist name is required'}), 400
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']

    def process_and_stream():
        tracks = []
        total = len(files)

        yield f"data: {json.dumps({'type': 'start', 'total': total})}\n\n"

        for i, file in enumerate(files):
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in SUPPORTED_FORMATS:
                yield f"data: {json.dumps({'type': 'skip', 'file': file.filename, 'index': i+1, 'total': total})}\n\n"
                continue

            try:
                file_bytes = file.read()
                response = requests.post(
                    'https://api.audd.io/',
                    data={'api_token': audd_key, 'return': 'spotify'},
                    files={'file': (file.filename, file_bytes)}
                )
                data = response.json()

                if data.get('status') == 'success' and data.get('result'):
                    result = data['result']
                    spotify_uri = 'Unavailable'
                    if 'spotify' in result and result['spotify']:
                        spotify_uri = result['spotify']['uri']

                    track = Track(
                        link=result.get('song_link', ''),
                        title=result.get('title', 'Unknown'),
                        artist=result.get('artist', 'Unknown'),
                        album=result.get('album', 'Unknown'),
                        spotify_uri=spotify_uri
                    )
                    tracks.append(track)
                    yield f"data: {json.dumps({'type': 'recognized', 'file': file.filename, 'title': track.title, 'artist': track.artist, 'uri': spotify_uri, 'index': i+1, 'total': total})}\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'unrecognized', 'file': file.filename, 'index': i+1, 'total': total})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'file': file.filename, 'message': str(e), 'index': i+1, 'total': total})}\n\n"

        # Create Spotify playlist
        try:
            spotify_tracks = [t.spotify_uri for t in tracks if t.spotify_uri != 'Unavailable']
            new_playlist = sp.user_playlist_create(user_id, playlist_name, public=False)
            new_playlist_id = new_playlist['id']

            if spotify_tracks:
                sp.user_playlist_add_tracks(user_id, new_playlist_id, spotify_tracks)

            db = get_db()
            db.create_playlist_with_songs(playlist_name, user_id, tracks)
            db.close()

            yield f"data: {json.dumps({'type': 'done', 'playlist_name': playlist_name, 'total_added': len(spotify_tracks), 'total_unrecognized': len(tracks) - len(spotify_tracks)})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'fatal_error', 'message': str(e)})}\n\n"

    return Response(stream_with_context(process_and_stream()), mimetype='text/event-stream')

@app.route('/restore-playlist', methods=['POST'])
def restore_playlist():
    token_info = get_token()
    if not token_info:
        return jsonify({'error': 'Not logged in'}), 401

    playlist_name = request.json.get('playlist_name')
    if not playlist_name:
        return jsonify({'error': 'Playlist name required'}), 400

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']

    db = get_db()
    name, uris = db.restore_playlist(playlist_name, user_id)
    db.close()

    if not uris:
        return jsonify({'error': 'No tracks found for this playlist'}), 404

    new_playlist = sp.user_playlist_create(user_id, name, public=False)
    sp.user_playlist_add_tracks(user_id, new_playlist['id'], uris)

    return jsonify({'success': True, 'playlist_name': name, 'tracks_restored': len(uris)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
