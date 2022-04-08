import urllib.parse
import requests
import vk_api
import spotipy
import yandex_music
import deezer
import config
import db_orm as db

count_tracks = 15


class Vk:
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)
        self.user_id = self.api.method('users.get')[0]['id']

    def tracks(self, offset):
        try:
            return self.api.method('audio.get', values={'count': count_tracks, 'offset': offset})
        except:
            return None

    def playlists_albums(self, offset):
        return self.api.method('audio.getPlaylists', values={'owner_id': self.user_id, 'count': count_tracks,
                                                             'offset': offset})

    def get_music(self, offset, ids):
        tracks = []
        playlists = []
        albums = []
        music_tracks = self.tracks(offset)['items']
        if music_tracks:
            for i in music_tracks:
                try:
                    tracks.append({'title': i['title'], 'artist': i['artist'],
                                   'photo': i['album']['thumb']['photo_1200'],
                                   'service': 'vk', 'id': ids})
                except:
                    try:
                        tracks.append({'title': i['title'], 'artist': i['artist'],
                                       'service': 'vk', 'id': ids})
                    except:
                        break
                ids += 1

        music_albums = self.playlists_albums(offset)['items']
        for i in music_albums:
            if i['album_type'] == 'playlist':
                try:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'photo': i['thumbs'][0]['photo_1200'], 'service': 'vk', 'id': ids})
                except:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'service': 'vk', 'id': ids})
            if i['album_type'] == 'main_only':
                try:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'photo': i['photo']['photo_1200'],
                                   'service': 'vk', 'id': ids})
                except:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'service': 'vk',
                                   'id': ids})
            ids += 1

        return tracks, playlists, albums, ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.api.method('audio.search', values={'q': i, 'owner_id': self.user_id})
            items.append({'id': result['items'][0]['id'], 'owner_id': result['items'][0]['owner_id']})
        return items

    def transfer_tracks(self, tracks, user_id, sub=True):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in tracks_ids:
                self.api.method('audio.add', values={'audio_id': i['id'], 'owner_id': i['owner_id']})
        if not sub:
            count = 0
            for i in range(0, config.LIMIT):
                try:
                    self.api.method('audio.add', values={'audio_id': tracks_ids[i]['id'],
                                                         'owner_id': tracks_ids[i]['owner_id']})
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)


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
        self.ids = 0

    def tracks(self, offset, ids):
        tracks = []
        result = self.spot.current_user_saved_tracks(limit=count_tracks, offset=offset)
        for item in result['items']:
            track = item['track']
            tracks.append({'title': track['name'], 'artist': track['artists'][0]['name'],
                           'album': track['album']['name'], 'photo': track['album']['images'][0]['url'],
                           'service': 'spotify', 'id': ids})
            ids += 1
        self.ids = ids
        return tracks

    def playlists(self, offset, ids):
        playlists = []
        result = self.spot.current_user_playlists(limit=count_tracks, offset=offset)
        for i, item in enumerate(result['items']):
            playlists.append({'title': item['name'], 'id': ids, 'photo': item['images'][0]['url'],
                              'service': 'spotify'})
            ids += 1
        return playlists

    def artists(self, offset, ids):
        artists = []
        for sp_range in ['short_term', 'medium_term', 'long_term']:
            result = self.spot.current_user_top_artists(time_range=sp_range, limit=count_tracks, offset=offset)
            for i, item in enumerate(result['items']):
                artists.append({'title': item['name'], 'id': ids, 'photo': item['images'][0]['url'],
                                'service': 'spotify'})
                ids += 1
            return artists

    def albums(self, offset, ids):
        albums = []
        result = self.spot.current_user_saved_albums(limit=count_tracks, offset=offset)
        for i, item in enumerate(result['items']):
            albums.append({'title': item['album']['name'], 'id': ids, 'photo': item['album']['images'][0]['url'],
                           'service': 'spotify'})
            ids += 1
        return albums

    def get_music(self, offset, ids):
        return self.tracks(offset, ids), self.playlists(offset, ids),\
               self.artists(offset, ids), self.albums(offset, ids), self.ids

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
                chunk = tracks_ids[i:i + 50]
                self.spot.current_user_saved_tracks_add(chunk)
        if not sub:
            chunk = tracks_ids[0:config.LIMIT]
            self.spot.current_user_saved_tracks_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

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
            chunk = albums_ids[i:i + 50]
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
            chunk = playlists_ids[i:i + 50]
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
            chunk = artists_ids[i:i + 50]
            self.spot.user_follow_artists(chunk)


class Yandex:
    def __init__(self, login=None, password=None, token=None):
        if login and password:
            self.api = yandex_music.Client.from_credentials(login, password)
        if token:
            self.api = yandex_music.Client.from_token(token)
        self.api.report_new_fields = False
        self.api.report_new_fields_callback = False
        self.ids = 0

    def save_token(self, user_id):
        db.add_service(user_id, self.api.token, 'yandex')

    def tracks(self, ids):
        tracks = []
        items = self.api.users_likes_tracks()
        for i in items:
            track = i.fetch_track()
            tracks.append({'title': track['title'], 'artist': track['artists'][0]['name'],
                           'album': track['albums'][0]['title'], 'service': 'yandex', 'id': ids})
            ids += 1
        self.ids = ids
        return tracks

    def albums(self):
        albums = []
        items = self.api.users_likes_albums()
        count = 0
        for i in items:
            albums.append({'title': i['album']['title'], 'artist': i['album']['artists'][0]['name'],
                           'service': 'yandex', 'id': count})
            count += 1
        return albums

    def artists(self):
        artists = []
        items = self.api.users_likes_artists()
        count = 0
        for i in items:
            artists.append({'title': i['artist']['name'], 'service': 'yandex', 'id': count})
            count += 1
        return artists

    def playlists(self):
        playlists = []
        items = self.api.users_likes_playlists()
        count = 0
        for i in items:
            playlists.append({'title': i['playlist']['title'], 'service': 'yandex', 'id': count})
            count += 1
        return playlists

    def get_music(self, ids):
        return self.tracks(ids), self.albums(), self.artists(), self.playlists(), self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='track')
            items.append(result.tracks.results[0].track_id)
        return items

    def transfer_tracks(self, tracks, user_id, sub=True):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in range(0, len(tracks_ids), 20):
                chunk = tracks_ids[i:i + 20]
                self.api.users_likes_tracks_add(chunk)
        if not sub:
            chunk = tracks_ids[0:config.LIMIT]
            self.api.users_likes_tracks_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

    def search_albums_ids(self, albums, user_id):
        items = []
        tracks_db = db.get_audio(albums, 'albums', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='album')
            items.append(result.albums.results[0].id)
        return items

    def transfer_albums(self, albums, user_id, sub=True):
        albums_ids = self.search_albums_ids(albums, user_id)
        if sub:
            for i in range(0, len(albums_ids), 20):
                chunk = albums_ids[i:i + 20]
                self.api.users_likes_albums_add(chunk)
        if not sub:
            chunk = albums_ids[0:config.LIMIT]
            self.api.users_likes_albums_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

    def search_artists_ids(self, artists, user_id):
        items = []
        tracks_db = db.get_audio(artists, 'artists', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='artist')
            items.append(result.artists.results[0].id)
        return items

    def transfer_artists(self, artists, user_id, sub=True):
        artists_ids = self.search_artists_ids(artists, user_id)
        if sub:
            for i in range(0, len(artists_ids), 20):
                chunk = artists_ids[i:i + 20]
                self.api.users_likes_artists_add(chunk)
        if not sub:
            chunk = artists_ids[0:config.LIMIT]
            self.api.users_likes_artists_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

    def search_playlists_ids(self, playlists, user_id):
        items = []
        tracks_db = db.get_audio(playlists, 'playlists', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='playlist')
            items.append(result.playlists.results[0].id)
        return items

    def transfer_playlists(self, playlists, user_id, sub=True):
        playlists_ids = self.search_playlists_ids(playlists, user_id)
        if sub:
            for i in range(0, len(playlists_ids), 20):
                chunk = playlists_ids[i:i + 20]
                self.api.users_likes_playlists_add(chunk)
        if not sub:
            chunk = playlists_ids[0:config.LIMIT]
            self.api.users_likes_playlists_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))


class Deezer:
    def __init__(self, token=None):
        self.api = deezer.Client(app_id=config.DEEZER_ID, app_secret=config.SPOTIFY_SECRET, access_token=token)
        self.ids = 0

    @staticmethod
    def create_url():
        params = urllib.parse.urlencode({'app_id': config.DEEZER_ID,
                                         'redirect_uri': config.DEEZER_REDIRECT,
                                         'perms': 'basic_access,email,manage_library,'
                                                  'offline_access,manage_community,'
                                                  'delete_library,listening_history'})
        return 'https://connect.deezer.com/oauth/auth.php' + '?' + params

    @staticmethod
    def save_token(code, user_id):
        response = requests.post('https://connect.deezer.com/oauth/access_token.php',
                                 params={'app_id': config.DEEZER_ID,
                                         'secret': config.DEEZER_SECRET_KEY,
                                         'code': code,
                                         'output': 'json'})
        token = response.json()['access_token']
        db.add_service(user_id, token, 'deezer')

    def tracks(self, ids):
        tracks = []
        items = self.api.get_user_tracks()
        for i in items:
            tracks.append({'title': i.title, 'artist': i.artist.name, 'album': i.album.title,
                           'service': 'deezer', 'id': ids})
            ids += 1
        return tracks

    def albums(self):
        albums = []
        items = self.api.get_user_albums()
        count = 0
        for i in items:
            albums.append({'title': i.title, 'artist': i.artist.name, 'service': 'deezer', 'id': count})
            count += 1
        return albums

    def artists(self):
        artists = []
        items = self.api.get_user_artists()
        count = 0
        for i in items:
            artists.append({'title': i.name, 'service': 'deezer', 'id': count})
            count += 1
        return artists

    def get_music(self,):
        return self.tracks(0), self.albums(), self.artists(), self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.api.search(i, ordering='TRACK_ASC')
            for i in result:
                items.append(i.id)
                break
        return items

    def transfer_tracks(self, tracks, user_id, sub=True):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in tracks_ids:
                try:
                    self.api.add_user_track(i)
                except:
                    pass
        if not sub:
            chunk = tracks_ids[0:config.LIMIT]
            count = 0
            for i in chunk:
                try:
                    self.api.add_user_track(i)
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def search_albums_ids(self, albums, user_id):
        items = []
        albums_db = db.get_audio(albums, 'albums', user_id)
        for i in albums_db:
            result = self.api.search(i, ordering='ALBUM_ASC')
            for i in result:
                items.append(i.album.id)
                break
        return items

    def transfer_albums(self, albums, user_id, sub=True):
        albums_ids = self.search_albums_ids(albums, user_id)
        if sub:
            for i in albums_ids:
                try:
                    self.api.add_user_album(i)
                except:
                    pass
        if not sub:
            chunk = albums_ids[0:config.LIMIT]
            count = 0
            for i in chunk:
                try:
                    self.api.add_user_album(i)
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def search_artists_ids(self, artists, user_id):
        items = []
        artists_db = db.get_audio(artists, 'artists', user_id)
        for i in artists_db:
            result = self.api.search(i, ordering='ARTIST_ASC')
            for i in result:
                items.append(i.artist.id)
                break
        return items

    def transfer_artists(self, artists, user_id, sub=True):
        artists_ids = self.search_artists_ids(artists, user_id)
        if sub:
            for i in artists_ids:
                try:
                    self.api.add_user_artist(i)
                except:
                    pass
        if not sub:
            chunk = artists_ids[0:config.LIMIT]
            count = 0
            for i in chunk:
                try:
                    self.api.add_user_artist(i)
                    count += 1
                except: pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

