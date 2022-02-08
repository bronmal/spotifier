import vk_api
import requests
import spotipy


class Vk:
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)
        self.user_id = self.api.method('users.get')[0]['id']
        self.count = self.api.method('audio.getCount', values={'owner_id': self.user_id})

    def tracks(self):
        return self.api.method('audio.get', values={'count': self.count})

    def playlists_albums(self):
        return self.api.method('audio.getPlaylists', values={'owner_id': self.user_id})

    def get_music(self):
        tracks = []
        playlists = []
        albums = []
        music_tracks = self.tracks()['items']
        for i in music_tracks:
            try:
                tracks.append({'title': i['title'], 'artist': i['artist'], 'photo': i['album']['thumb']['photo_1200'],
                               'service': 'vk'})
            except:
                tracks.append({'title': i['title'], 'artist': i['artist'], 'service': 'vk'})

        music_albums = self.playlists_albums()['items']
        for i in music_albums:
            if i['album_type'] == 'playlist':
                try:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'photo': i['thumbs'][0]['photo_1200'], 'service': 'vk'})
                except:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'], 'service': 'vk'})
            if i['album_type'] == 'main_only':
                try:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'photo': i['photo']['photo_1200'],
                                   'service': 'vk'})
                except:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'service': 'vk'})

        return tracks, playlists, albums


class Spotify:
    def __init__(self, token):
        self.prefix = 'https://api.spotify.com/v1'
        self.token = token
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private '
                                                              'playlist-modify-public ugc-image-upload '
                                                              'user-library-read '
                                                              'playlist-read-private '
                                                              'user-top-read '
                                                              'user-read-email',
                                                        show_dialog=True)
        self.spot = spotipy.Spotify(auth_manager=self.auth_manager)
        self.count = 0

    def tracks(self):
        tracks = []
        while True:
            result = self.spot.current_user_saved_tracks(limit=50, offset=self.count)
            for item in result['items']:
                track = item['track']
                tracks.append({'title': track['name'], 'artist': track['artists'][0]['name'],
                               'album': track['album']['name'], 'photo': track['album']['images'][0]['url'],
                               'service': 'spotify'})
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return tracks

    def playlists(self):
        playlists = []
        while True:
            result = self.spot.current_user_playlists(limit=50, offset=self.count)
            for i, item in enumerate(result['items']):
                playlists.append({'title': item['name'], 'id': i, 'photo': item['images'][0]['url'],
                                  'service': 'spotify'})
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return playlists

    def artists(self):
        artists = []
        while True:
            for sp_range in ['short_term', 'medium_term', 'long_term']:
                print("range:", sp_range)
                result = self.spot.current_user_top_artists(time_range=sp_range, limit=self.count)
                for i, item in enumerate(result['items']):
                    artists.append({'title': item['name'], 'id': i, 'photo': item['images'][0]['url'],
                                    'service': 'spotify'})
                self.count += 50
            if result['next'] is None:
                self.count = 0
                return artists

    def albums(self):
        albums = []
        while True:
            result = self.spot.current_user_saved_albums(limit=50, offset=self.count)
            for i, item in enumerate(result['items']):
                albums.append({'title': item['album']['name'], 'id': i, 'photo': item['album']['images'][0]['url'],
                               'service': 'spotify'})
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return albums

    def get_music(self):
        return self.tracks(), self.playlists(), self.artists(), self.albums()

