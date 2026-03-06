# main.py
import sys
import traceback
# from playlist_manager.commands import save_playlist, restore_playlist

import requests
import os
import json

from Models.playlist import Playlist
from playlists_manager.db import Database


def what_would_you_like_to_do():
    
    commands_descriptions = ["save-playlist" "\tcreates new playlist", "restore-playlist" "\trestores previoulsy created playlist", "history" "\tgets history of saved"]
    print(commands_descriptions)
    while True:
        print("What would you like to do? Here are your options:\n")
        for command_descriptions in commands_descriptions:
            command = command_descriptions.split()[0]
            print(f"- {command}")

        user_input = input("\nPlease enter a command: ").strip().lower()

        if user_input in [command.split()[0] for command in commands_descriptions]:
            print(f"You have selected: {user_input}")
            if user_input == "history":
                db = Database()
                db.connect()
                db.history()
            break
        else:
            print("Please enter a valid command.\n")

    return user_input

def restore():
    db = Database()
    db.connect()

    playlist_names = db.history()

    while True:
        user_input = input("\nPlease enter a name of playlist to restore: ").strip().lower()

        if user_input in playlist_names:
            print(f"> Selected: {user_input}")
            print("> Starting playlist Restoration")
            # db.restore_playlist(user_input)
            break
        else:
            print("- Playlist not in playlists\n- Enter valid Playlist Name: ")
    return db.restore_playlist(user_input)

def get_playlist_name():
    not_allowed = (
        '\x00', # Null character
        '\x01', '\x02', '\x03', '\x04', '\x05', '\x06', '\x07', '\x08', '\x09', # Control characters
        '\x0A', '\x0B', '\x0C', '\x0D', '\x0E', '\x0F', '\x10', '\x11', '\x12', '\x13',
        '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1A', '\x1B', '\x1C', '\x1D',
        '\x1E', '\x1F',
        '&', # Ampersand
        '?', # Question Mark
        '=', # Equals Sign
        '/', # Forward Slash
        '\\', # Backslash
        '|',) # Pipe ]    

    while True:
        playlist_name = input("What would you like to name your playlist: ").strip()
        if playlist_name and len(playlist_name) <= 100:
            if any(char in not_allowed for char in playlist_name):
                print(f"\nYou're not allowed to have characters: \n{not_allowed} \nin your playlist name.\n")
            else:
                print('Creating Playlist...')
                break
        else:
            print("Name cannot be blank or have more than 100 characters.")
            
    return playlist_name

def get_music_dir():
    # r'C:\Users\cash\Music'
    while True:
        music_directory = input("Please paste the music directory you want converted path in the form of 'C:\\Users\\cash\\Music': ").strip()
        if music_directory:
            break
    return os.path.normpath(music_directory)

def get_song_address(directory):

    alt_directory = r'C:\Users\cash\Music'


    supported_song_formats = (
        ".mp3",
        ".wav",
        ".flac",
        ".ogg",
        ".aac",
        ".m4a",
        ".wma",
        ".aiff",
        ".alac")
    song_paths_list =[]
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            # Full path to the file by joining song name with root folder
            file_path = os.path.join(root, file_name)
            # If you need to check the file's name or extension
            file_base_name, file_extension = os.path.splitext(file_name)
            if file_extension.lower() in supported_song_formats:
                #append full song path(root directory + song name + ext)
                song_paths_list.append(file_path)
                
    return song_paths_list 



def Audd_api_call(paths_list):
    # Add Your Your Own API KEY
    api_key = 'API_KEY'

    # Step 3: Set up the API endpoint and parameters
    api_single_song = 'https://api.audd.io/'

    songs_that_get_appended = []
    for song_path in paths_list:
        params = {
            'api_token': api_key,
            'return': 'spotify'  # This can include 'apple_music', 'spotify', 'deezer', etc.
        }

        with open(song_path, 'rb') as audio_file:
            files = {'file': audio_file}

        # Make the request to the Audd.io API
            response = requests.post(api_single_song, data=params, files=files)

        # Check the response and parse the result
        if response.status_code == 200:
            song_data = response.json()

            with open('song_data.json', 'a') as json_file:
                json.dump(song_data, json_file, indent=4)
            
            from Models.track import Track as trk

            # from Models.playlist import Playlist as plylist
            from Models.playlist import Playlist
            
           # Handle the response (you can access various details like artist name, song title, etc.)
            if song_data['status'] == 'success'and 'spotify' not in song_data['result']:

                print(f"Song Title: {song_data['result']['title']}")
                print(f"Artist: {song_data['result']['artist']}")
                print(f"Album: {song_data['result']['album']}")
                # append_song to current playlists
                new_trk = trk(song_data['result']['song_link'], song_data['result']['title'], song_data['result']['artist'], song_data['result']['album'], "Unavailable")
                print(new_trk)
                songs_that_get_appended.append(new_trk)
                print("________________________________________________")
                # Additional data can be accessed similarly
            else:
                print(f"Song: {1}")
                print(f"Song Title: {song_data['result']['title']}")
                print(f"Artist: {song_data['result']['artist']}")
                print(f"Album: {song_data['result']['album']}")
                # append_song to current playlists
                print(f"SPOTIFY LINK: {song_data['result']['spotify']['external_urls']['spotify']}")
                print(f"URI: {song_data['result']['spotify']['uri']}")
                new_trk = trk(song_data['result']['song_link'], song_data['result']['title'], song_data['result']['artist'], song_data['result']['album'],song_data['result']['spotify']['uri'])
                print(new_trk)
                songs_that_get_appended.append(new_trk)
                print("________________________________________________")
                
        else:
            print(f"Error: {response.status_code}")


    return songs_that_get_appended

restore_playtlist = False    
def send_playlist_to_flask(playlist_name, songs, restoration=False):
    print(restoration)
    db = Database()
    db.connect()

    if restoration:
        songs_list = [(playlist_name, "ON-RESTORE", "ON-RESTORE","ON-RESTORE", "ON-RESTORE", song_uri)  for song_uri in songs]
        db.create_temp_playlist_songs_table(playlist_name, songs_list)
    else:
        songs_list = [(playlist_name, song.link, song.title,song.artist, song.album,song.spotify_uri)  for song in songs]
        db.create_temp_playlist_songs_table(playlist_name, songs_list)
   

if __name__ == '__main__':
    command = what_would_you_like_to_do()
    if command == "restore-playlist":
        playlist_name, songs = restore()
        send_playlist_to_flask(playlist_name, songs, restoration=True)
    # Assumes user opted Save new Playlist
    else:
        playlist_name = get_playlist_name()
        music_dir = get_music_dir()
        song_paths = get_song_address(music_dir)
        songs = Audd_api_call(song_paths)
        print("\n\nPrint Songs list:")
        print(songs)
        
        send_playlist_to_flask(playlist_name, songs)
    
    


