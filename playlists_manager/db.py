import sqlite3
import time

class Database:
    def __init__(self, db_file='data/playlists.db'):
        self.db_file = db_file
        self.connection = None
        self.restore = False

    def connect(self):
        """Connect to the SQLite database."""
        self.connection = sqlite3.connect(self.db_file)
        self.connection.execute("PRAGMA foreign_keys = 1")  # Foreign key support
        self.create_tables()  # Create tables on connection

    def close(self):
        """Close the SQLite database connection."""
        if self.connection:
            self.connection.close()

            

    def create_tables(self):
        """Create the necessary tables."""
        create_songs_table = """
        CREATE TABLE IF NOT EXISTS Songs (
            song_link TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            spotify_uri TEXT UNIQUE
        );
        """

        create_playlists_table = """
        CREATE TABLE IF NOT EXISTS Playlists (
            playlist_name TEXT PRIMARY KEY
        );
        """

        create_songs_added_table = """
        CREATE TABLE IF NOT EXISTS Songs_added (
            playlist_name TEXT,
            spotify_uri TEXT,
            FOREIGN KEY (playlist_name) REFERENCES Playlists(playlist_name),
            FOREIGN KEY (spotify_uri) REFERENCES Songs(spotify_uri),
            PRIMARY KEY (playlist_name, spotify_uri)
        );
        """

        create_unadded_songs_table = """
        CREATE TABLE IF NOT EXISTS Unadded_songs (
            playlist_name TEXT,
            spotify_uri TEXT,
            FOREIGN KEY (playlist_name) REFERENCES Playlists(playlist_name),
            FOREIGN KEY (spotify_uri) REFERENCES Songs(spotify_uri),
            PRIMARY KEY (playlist_name, spotify_uri)
        );
        """

        cursor = self.connection.cursor()
        cursor.execute(create_songs_table)
        cursor.execute(create_playlists_table)
        cursor.execute(create_songs_added_table)
        cursor.execute(create_unadded_songs_table)
        self.connection.commit()

    def create_playlist_with_songs(self, playlist_name, songs):
        """Create a playlist and add a batch of songs to it."""
        cursor = self.connection.cursor()
        cursor.execute("INSERT OR IGNORE INTO Playlists (playlist_name) VALUES (?)", (playlist_name,))
        
        # song_link = song[2]
        # song_title = song[3]
        # song_artist =  song[4]
        # song_uri = song[6]

        # song_data = [(song.link, song.title, song.artist, song.spotify_uri) for song in songs]
        song_data = []
        for song in songs:
            song_link = song[2]
            song_title = song[3]
            song_artist =  song[4]
            song_uri = song[6]
            song_data.append((song_link, song_title, song_artist, song_uri))

        print("Song data prepared for insertion:", song_data)
        insert_query = """
        INSERT OR REPLACE INTO Songs (song_link, artist, title, spotify_uri)
        VALUES (?, ?, ?, ?)
        """
        
        if song_data:
            cursor.executemany(insert_query, song_data)
        for song in songs:
            if song[6] == "Unavailable":
                cursor.execute(
                    "INSERT OR REPLACE INTO Unadded_songs (playlist_name, spotify_uri) VALUES (?, ?)",
                    (playlist_name, song[6])
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO Songs_added (playlist_name, spotify_uri) VALUES (?, ?)", 
                    (playlist_name, song[6])
                )

        self.connection.commit()
    def history(self):
        """Prints out available Playlists"""
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT playlist_name
        FROM Playlists
        """, )

        playlists = cursor.fetchall()

        print("Here's your History of saved Playlists: ")
        for playlist in playlists:
            print(f"- {playlist[0]}")

        return [row[0] for row in playlists]
        


    def restore_playlist(self, playlist_name):
        """Restore a playlist by retrieving all associated song URIs."""
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT spotify_uri
        FROM Songs_added
        WHERE playlist_name = ?
        """, (playlist_name,))
        
        uris = [row[0] for row in cursor.fetchall()]
        return playlist_name ,uris
    
    def create_temp_playlist_songs_table(self, playlist_name, song_uris):
        """
        Create a temporary table to store the playlist name and associated song URIs.
        One playlist can have multiple songs. This version uses executemany() for efficiency.
        """
        cursor = self.connection.cursor()

        # Create a temporary table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Temp_Playlist_Songs (
            playlist_Id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_name TEXT,
            song_link TEXT,
            song_title TEXT,
            song_artist TEXT,
            song_album TEXT,
            spotify_uri TEXT
        );
        """)

        # Prepare the data as a list of tuples, where each tuple is (playlist_name, spotify_uri)
        # data = [(playlist_name, uri) for uri in song_uris]

        cursor.executemany(
            "INSERT INTO Temp_Playlist_Songs (playlist_name, song_link,song_title, song_artist, song_album, spotify_uri) VALUES (?, ?, ?, ?, ?, ?)",
            song_uris
        )

        self.connection.commit()
        print("Created Temporary Table")

    def playlist_name_and_song(self):
        """Get the last playlist and its associated song URIs."""
        cursor = self.connection.cursor()
        
        # Get the last playlist (by order of insertion)
        cursor.execute("SELECT playlist_name FROM Temp_Playlist_Songs ORDER BY playlist_Id DESC LIMIT 1") 
        last_playlist = cursor.fetchone()  # Fetch just the last playlist
        
        if last_playlist is None:
            return None  # No playlists available
        
        playlist_name = last_playlist[0]  # Extract the playlist name
        print(f"This is your playlist {playlist_name}")

        # Get the song URIs for the last playlist
        cursor.execute("""
        SELECT *
        FROM Temp_Playlist_Songs
        WHERE playlist_name = ?
        """, (playlist_name,))
        
        print("Retrieved Playlist named and Song URIs")

        # song_datas = []
        
        # print(cursor.fetchall)

        song_datas = [(row[0],row[1],row[2], row[3], row[4], row[5], row[6]) for row in cursor.fetchall()]
        # uris = [row[0] for row in cursor.fetchall()]
        # uris = [row[0] for row in cursor.fetchall()]
        # uris = [row[0] for row in cursor.fetchall()]
        # uris = [row[0] for row in cursor.fetchall()]
        print("This is song datas: ")
        print(song_datas)
        self.drop_table("Temp_Playlist_Songs")
        return playlist_name, song_datas
    


    def drop_table(self, table_name):
        """Drop a specified table from the database."""
        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        self.connection.commit()
        print(f"Deleted {table_name} table")




# My test usage:
if __name__ == "__main__":
    db = Database()
    db.connect()
    
    # Adding a new playlist and songs
    playlist_name = "My Playlist"
    songs = [
        {"song_link": "song1_link", "artist": "Artist 1", "song_name": "Song 1", "spotify_uri": "spotify:track:1"},
        {"song_link": "song2_link", "artist": "Artist 2", "song_name": "Song 2", "spotify_uri": "spotify:track:2"},
        {"song_link": "song3_link", "artist": "Artist 3", "song_name": "Song 3", "spotify_uri": "spotify:track:3"}
    ]
    
    try:
        db.create_playlist_with_songs(playlist_name, songs)
        print(f"Playlist '{playlist_name}' created with {len(songs)} songs.")
        
        # Restoring the playlist
        restored_songs = db.restore_playlist(playlist_name)
        print(f"Restored songs from '{playlist_name}':")
        for song in restored_songs:
            print(song)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()
