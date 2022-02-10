import vk_api
import spotipy

import db


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
        count_tr = 0
        for i in music_tracks:
            try:
                tracks.append({'title': i['title'], 'artist': i['artist'], 'photo': i['album']['thumb']['photo_1200'],
                               'service': 'vk', 'id': count_tr})
            except:
                tracks.append({'title': i['title'], 'artist': i['artist'], 'service': 'vk', 'id': count_tr})
            count_tr += 1

        music_albums = self.playlists_albums()['items']
        count_al_pl = 0
        for i in music_albums:
            if i['album_type'] == 'playlist':
                try:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'photo': i['thumbs'][0]['photo_1200'], 'service': 'vk', 'id': count_al_pl})
                except:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'service': 'vk', 'id': count_al_pl})
            if i['album_type'] == 'main_only':
                try:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'photo': i['photo']['photo_1200'],
                                   'service': 'vk', 'id': count_al_pl})
                except:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'service': 'vk',
                                   'id': count_al_pl})
            count_al_pl += 1

        return tracks, playlists, albums


class Spotify:
    def __init__(self, token):
        self.prefix = 'https://api.spotify.com/v1'
        self.token = token
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private '
                                                              'playlist-modify-public ugc-image-upload '
                                                              'user-library-read '
                                                              'user-library-modify '
                                                              'user-follow-modify '
                                                              'user-follow-read '
                                                              'playlist-read-private '
                                                              'user-top-read '
                                                              'user-read-email',
                                                        show_dialog=True)
        self.spot = spotipy.Spotify(auth_manager=self.auth_manager)
        self.count = 0

    def tracks(self):
        tracks = []
        count = 0
        while True:
            result = self.spot.current_user_saved_tracks(limit=50, offset=self.count)
            for item in result['items']:
                track = item['track']
                tracks.append({'title': track['name'], 'artist': track['artists'][0]['name'],
                               'album': track['album']['name'], 'photo': track['album']['images'][0]['url'],
                               'service': 'spotify', 'id': count})
                count += 1
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return tracks

    def playlists(self):
        playlists = []
        count = 0
        while True:
            result = self.spot.current_user_playlists(limit=50, offset=self.count)
            for i, item in enumerate(result['items']):
                playlists.append({'title': item['name'], 'id': count, 'photo': item['images'][0]['url'],
                                  'service': 'spotify'})
                count += 1
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return playlists

    def artists(self):
        artists = []
        count = 0
        while True:
            for sp_range in ['short_term', 'medium_term', 'long_term']:
                result = self.spot.current_user_top_artists(time_range=sp_range, limit=self.count)
                for i, item in enumerate(result['items']):
                    artists.append({'title': item['name'], 'id': i, 'photo': item['images'][0]['url'],
                                    'service': 'spotify'})
                    count += 1
                self.count += 50
            if result['next'] is None:
                self.count = 0
                return artists

    def albums(self):
        albums = []
        count = 0
        while True:
            result = self.spot.current_user_saved_albums(limit=50, offset=self.count)
            for i, item in enumerate(result['items']):
                albums.append({'title': item['album']['name'], 'id': i, 'photo': item['album']['images'][0]['url'],
                               'service': 'spotify'})
                count += 1
            self.count += 50
            if result['next'] is None:
                self.count = 0
                return albums

    def get_music(self):
        return self.tracks(), self.playlists(), self.artists(), self.albums()

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.spot.search(i, type='track', limit=1)
            try:
                items.append(result['tracks']['items'][0]['id'])
            except:
                pass  # TODO отправлять неперенесенные треки
        return items

    def transfer_tracks(self, tracks, user_id, sub=True):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in range(0, len(tracks_ids), 50):
                chunk = tracks_ids[i:i+50]
                self.spot.current_user_saved_tracks_add(chunk)
        if not sub:
            chunk = tracks_ids[0:9]
            self.spot.current_user_saved_tracks_add(chunk)

    def search_albums_ids(self, albums, user_id):
        items = []
        albums_db = db.get_audio(albums, 'albums', user_id)
        for i in albums_db:
            result = self.spot.search(i, type='album', limit=1)
            try:
                items.append(result['albums']['items'][0]['id'])
            except:
                pass  # TODO отправлять неперенесенные треки
        return items

    def transfer_albums(self, albums, user_id):
        albums_ids = self.search_albums_ids(albums, user_id)
        for i in range(0, len(albums_ids), 50):
            chunk = albums_ids[i:i+50]
            self.spot.current_user_saved_albums_add(chunk)

    def search_playlists_ids(self, playlists, user_id):
        items = []
        albums_db = db.get_audio(playlists, 'playlists', user_id)
        for i in albums_db:
            result = self.spot.search(i, type='playlist', limit=1)
            try:
                items.append(result['playlist']['items'][0]['id'])
            except:
                pass  # TODO отправлять неперенесенные треки
        return items

    def transfer_playlists(self, playlists, user_id):
        playlists_ids = self.search_albums_ids(playlists, user_id)
        for i in range(0, len(playlists_ids), 50):
            chunk = playlists_ids[i:i+50]
            self.spot.current_user_playlists(chunk)

    def search_artists_ids(self, artists, user_id):
        items = []
        albums_db = db.get_audio(artists, 'artists', user_id)
        for i in albums_db:
            result = self.spot.search(i, type='artist', limit=1)
            try:
                items.append(result['artists']['items'][0]['id'])
            except:
                pass  # TODO отправлять неперенесенные треки
        return items

    def transfer_artists(self, artists, user_id):
        artists_ids = self.search_artists_ids(artists, user_id)
        for i in range(0, len(artists_ids), 50):
            chunk = artists_ids[i:i+50]
            self.spot.user_follow_artists(chunk)
