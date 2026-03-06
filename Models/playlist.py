class Playlist:
    def __init__(self, name, songs):
        self.name = name
        self.songs = []

    def add_song(self, song):
        if song not in self.songs:
            self.songs.append(song)
    
    def remove_song(self, song):
        if song in self.songs:
            self.songs.remove(song)
    
    def get_songs(self):
        return self.songs
    
    #  def __repr__(self):
    #     return 