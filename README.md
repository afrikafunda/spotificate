# Offline Songs to Spotify Playlist

I built this app to help you convert offline songs into a Spotify playlist using **Audd.io's song recognition API**. Follow the steps below to get started.

## Requirements

- **Audd.io API Key**: 
  - Sign up for a free account at [Audd.io](https://audd.io/).
  - Create your API key from the [Audd.io Dashboard](https://dashboard.audd.io/).
  - In the "main.py" file replace "API_KEY" with your actual api key.
  - Install Flask & Python
  
- **Spotify Account**: You'll need a Spotify account to create or restore playlists.

## How to Run the App

1. **Clone the Repository**: git clone   h  ttps://github.com/afrikafunda/OfflineSongsToSpotifyPlaylist.git
   cd OfflineSongsToSpotifyPlaylist

2. **Run the Flask App**:
In one terminal, start the Flask app by running: python run_flask.py
**Do not click the localhost link yet.** You'll return to this after completing the next step.

3. **Run the Main Application**:
In another terminal, run the main app: python main.py python main.py

    You'll be prompted with the following options:
    
    What would you like to do? Here are your options:
    - save-playlist
    - restore-playlist
    - history
    Please enter a command:
    Follow the Step until you are where you need to be

5. **Final Step**:
Go back to the terminal where the Flask app is running and click the following link to finalize the playlist creation or restoration: [http://127.0.0.1:5000](http://127.0.0.1:5000).

6. **Enjoy Your Playlist!**
Your playlist should now be created or restored on Spotify.

