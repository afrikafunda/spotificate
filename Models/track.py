class Track:
    def __init__(self, link , title, artist, album, spotify_uri=None):
        """
        Initialize a Track instance.
        
        :param title: Title of the song
        :param artist: Artist of the song
        :param album: Album of the song
        :param spotify_uri: Spotify URI of the song (optional)
        """
        self.link = link
        self.title = title
        self.artist = artist
        self.album = album
        self.spotify_uri = spotify_uri
        
    def __repr__(self):
        return f"Track(link='{self.link}', title='{self.title}', artist='{self.artist}', album='{self.album}', spotify_uri='{self.spotify_uri}')"
    
    def get_title(self):
        """
        Get the title of the track.
        
        :return: Title of the track
        """
        return self.title
    
    def get_artist(self):
        """
        Get the artist of the track.
        
        :return: Artist of the track
        """
        return self.artist
    
    def get_album(self):
        """
        Get the album of the track.
        
        :return: Album of the track
        """
        return self.album
    
    def get_spotify_uri(self):
        """
        Get the Spotify URI of the track.
        
        :return: Spotify URI of the track
        """
        return self.spotify_uri
