import sqlite3


class Database:
    def __init__(self, db_file='data/playlists.db'):
        self.db_file = db_file
        self.connection = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_file)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.create_tables()

    def close(self):
        if self.connection:
            self.connection.close()

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Songs (
            song_link TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            spotify_uri TEXT UNIQUE
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Playlists (
            playlist_name TEXT,
            user_id TEXT NOT NULL,
            PRIMARY KEY (playlist_name, user_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Songs_added (
            playlist_name TEXT,
            user_id TEXT NOT NULL,
            spotify_uri TEXT,
            PRIMARY KEY (playlist_name, user_id, spotify_uri)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Unadded_songs (
            playlist_name TEXT,
            user_id TEXT NOT NULL,
            spotify_uri TEXT,
            PRIMARY KEY (playlist_name, user_id, spotify_uri)
        );
        """)

        self.connection.commit()

    def create_playlist_with_songs(self, playlist_name, user_id, tracks):
        """
        tracks: list of Track objects
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO Playlists (playlist_name, user_id) VALUES (?, ?)",
            (playlist_name, user_id)
        )

        for track in tracks:
            cursor.execute(
                "INSERT OR REPLACE INTO Songs (song_link, title, artist, spotify_uri) VALUES (?, ?, ?, ?)",
                (track.link, track.title, track.artist, track.spotify_uri)
            )
            if track.spotify_uri == 'Unavailable':
                cursor.execute(
                    "INSERT OR REPLACE INTO Unadded_songs (playlist_name, user_id, spotify_uri) VALUES (?, ?, ?)",
                    (playlist_name, user_id, track.spotify_uri)
                )
            else:
                cursor.execute(
                    "INSERT OR REPLACE INTO Songs_added (playlist_name, user_id, spotify_uri) VALUES (?, ?, ?)",
                    (playlist_name, user_id, track.spotify_uri)
                )

        self.connection.commit()

    def history(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT playlist_name FROM Playlists WHERE user_id = ?",
            (user_id,)
        )
        return [row[0] for row in cursor.fetchall()]

    def restore_playlist(self, playlist_name, user_id):
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT spotify_uri FROM Songs_added WHERE playlist_name = ? AND user_id = ?",
            (playlist_name, user_id)
        )
        uris = [row[0] for row in cursor.fetchall()]
        return playlist_name, uris