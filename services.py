import json
import urllib.parse
import uuid
import requests
import vk_api
import yandex_music
from yandex_music.utils.difference import Difference
import deezer
import config
import db_orm as db
from auth import SpotAuth

count_tracks = 15


class Vk:
    def __init__(self, token, socket=None):
        self.api = vk_api.VkApi(token=token, api_version="5.131")
        self.api.RPS_DELAY = 1
        self.user_id = self.api.method('users.get')[0]['id']
        if socket:
            self.socket = socket

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
        try:
            music_tracks = self.tracks(offset)['items']
        except:
            music_tracks = None
        if music_tracks:
            for i in music_tracks:
                try:
                    tracks.append({'title': i['title'], 'artist': i['artist'],
                                   'photo': i['album']['thumb']['photo_1200'],
                                   'service': 'vk', 'id': str(uuid.uuid4())})
                except:
                    try:
                        tracks.append({'title': i['title'], 'artist': i['artist'],
                                       'service': 'vk', 'id': str(uuid.uuid4())})
                    except:
                        break
                ids += 1

        music_albums = self.playlists_albums(offset)['items']
        for i in music_albums:
            if i['album_type'] == 'playlist':
                try:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'photo': i['thumbs'][0]['photo_1200'], 'service': 'vk', 'id': str(uuid.uuid4())})
                except:
                    playlists.append({'title': i['title'], 'access_key': i['access_key'],
                                      'service': 'vk', 'id': str(uuid.uuid4())})
            if i['album_type'] == 'main_only':
                try:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'photo': i['photo']['photo_1200'],
                                   'service': 'vk', 'id': str(uuid.uuid4())})
                except:
                    albums.append({'title': i['title'], 'access_key': i['original'], 'service': 'vk',
                                   'id': str(uuid.uuid4())})
            ids += 1

        return tracks, playlists, albums, ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            values = {'q': i, 'owner_id': self.user_id}
            result = self.api.method('execute', values={'code': f'return API.audio.search({values});'})
            # result = self.api.method('audio.search', values={'q': i, 'owner_id': self.user_id}, raw=True)
            try:
                items.append({'id': result['items'][0]['id'], 'owner_id': result['items'][0]['owner_id']})
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_tracks(self, tracks, user_id, sub=config.TESTING):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in tracks_ids:
                values = {'audio_id': i['id'], 'owner_id': i['owner_id']}
                self.api.method('execute', values={'code': f'return API.audio.add({values});'})
                # self.api.method('audio.add', values={'audio_id': i['id'], 'owner_id': i['owner_id']})
        if not sub:
            count = 0
            for i in range(0, db.check_free_transfer(user_id)):
                try:
                    self.api.method('audio.add', values={'audio_id': tracks_ids[i]['id'],
                                                         'owner_id': tracks_ids[i]['owner_id']})
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def transfer_playlists(self, playlists, user_id, sub=config.TESTING):
        playlist_id = self.api.method('audio.addAlbum', values={'title': 'test'})
        print(playlist_id)


class Spotify:
    def __init__(self, token, user_id, socket=None):
        self.prefix = 'https://api.spotify.com/v1'
        self.spot = SpotAuth(token=token, user_id=user_id)
        self.ids = 0
        try:
            self.spot_id = self.spot.get('me')['id']
        except:
            self.spot.refresh_token()
            if self.spot.token:
                self.spot_id = self.spot.get('me')['id']
        if socket:
            self.socket = socket

    def tracks(self, offset):
        tracks = []
        result = self.spot.get('me/tracks', {'limit': count_tracks, 'offset': offset})
        for item in result['items']:
            track = item['track']
            tracks.append({'title': track['name'], 'artist': track['artists'][0]['name'],
                           'album': track['album']['name'], 'photo': track['album']['images'][0]['url'],
                           'service': 'spotify', 'id': str(uuid.uuid4())})
            self.ids += 1
        return tracks

    def playlists(self, offset):
        playlists = []
        result = self.spot.get('me/playlists', {'limit': count_tracks, 'offset': offset})
        for i, item in enumerate(result['items']):
            tracks_spot = self.spot.get('playlists/{}/tracks'.format(item['id']))

            if tracks_spot['next'] is not None:
                tracks = []
                while tracks_spot['next'] is not None:
                    if len(tracks_spot['items']) > 0:
                        for b in tracks_spot['items']:
                            tracks.append(b['track']['name'] + ' ' + b['track']['artists'][0]['name'])
                    tracks_spot = self.spot.get(tracks_spot['next'][27:])

                for b in tracks_spot['items']:
                    tracks.append(b['track']['name'] + ' ' + b['track']['artists'][0]['name'])

                playlists.append({'title': item['name'], 'id': str(uuid.uuid4()), 'tracks': tracks, 'service': 'spotify'})

            else:
                tracks = []
                if len(tracks_spot['items']) > 0:
                    for b in tracks_spot['items']:
                        tracks.append(b['track']['name'] + ' ' + b['track']['artists'][0]['name'])
                playlists.append(
                    {'title': item['name'], 'id': str(uuid.uuid4()), 'tracks': tracks, 'service': 'spotify'})

        return playlists

    def artists(self, offset):
        artists = []
        for sp_range in ['short_term', 'medium_term', 'long_term']:
            result = self.spot.get('me/top/artists', {'limit': count_tracks, 'offset': offset})
            for i, item in enumerate(result['items']):
                artists.append({'title': item['name'], 'id': str(uuid.uuid4()), 'photo': item['images'][0]['url'],
                                'service': 'spotify'})
                self.ids += 1
            return artists

    def albums(self, offset):
        albums = []
        result = self.spot.get('me/albums', {'limit': count_tracks, 'offset': offset})
        for i, item in enumerate(result['items']):
            albums.append(
                {'title': item['album']['name'], 'id': str(uuid.uuid4()), 'photo': item['album']['images'][0]['url'],
                 'service': 'spotify'})
            self.ids += 1
        return albums

    def get_music(self, offset, ids):
        self.ids = ids
        return self.tracks(offset), self.playlists(offset), \
               self.artists(offset), self.albums(offset), self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.spot.get('search', {'q': i, 'type': 'track', 'limit': 1})
            self.socket.emit('audio_found', {'data': 1})
            try:
                items.append(result['tracks']['items'][0]['id'])
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_tracks(self, tracks, user_id, sub=config.TESTING):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in range(0, len(tracks_ids), 50):
                chunk = tracks_ids[i:i + 50]
                self.spot.put("me/tracks/?ids=" + ",".join(chunk))
        if not sub:
            chunk = tracks_ids[0:db.check_free_transfer(user_id)]
            self.spot.put("me/tracks/?ids=" + ",".join(chunk))
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

    def search_albums_ids(self, albums, user_id):
        items = []
        albums_db = db.get_audio(albums, 'albums', user_id)
        for i in albums_db:
            result = self.spot.get('search', {'q': i, 'type': 'album', 'limit': 1})
            try:
                items.append(result['albums']['items'][0]['id'])
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_albums(self, albums, user_id):
        albums_ids = self.search_albums_ids(albums, user_id)
        for i in range(0, len(albums_ids), 50):
            chunk = albums_ids[i:i + 50]
            self.spot.put("me/albums?ids=" + ",".join(chunk))

    def search_artists_ids(self, artists, user_id):
        items = []
        albums_db = db.get_audio(artists, 'artists', user_id)
        for i in albums_db:
            result = self.spot.get('search', {'q': i, 'type': 'artist', 'limit': 1, 'market': 'RS'})
            try:
                items.append(result['artists']['items'][0]['id'])
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_artists(self, artists, user_id):
        artists_ids = self.search_artists_ids(artists, user_id)
        for i in range(0, len(artists_ids), 50):
            chunk = artists_ids[i:i + 50]
            self.spot.put("me/following?type=artist&ids=" + ",".join(chunk))

    def transfer_playlists(self, playlists, user_id):
        playlists_ids = db.get_audio(playlists, 'playlists', user_id)
        users_playlists = self.spot.get('me/playlists', {'limit': 50})['items']
        for i in users_playlists:
            for b in playlists_ids:
                if i['name'] == b['title']:
                    playlists_ids.remove(b)

        for i in playlists_ids:
            playlist_id = self.spot.post('users/{}/playlists'.format(self.spot_id),
                                         json.dumps({'name': i['title']}))['id']
            tracks_ids = []
            for b in i['tracks']:
                result = self.spot.get('search', {'q': b, 'type': 'track', 'limit': 1})
                try:
                    tracks_ids.append(result['tracks']['items'][0]['uri'])
                    self.socket.emit('audio_found', {'data': 1})
                except:
                    self.socket.emit('audio_found', {'data': 0})
            for b in range(0, len(tracks_ids), 50):
                chunk = tracks_ids[b:b + 50]
                self.spot.post("playlists/{}/tracks".format(playlist_id), json.dumps({'uris': chunk}))


class Yandex:
    def __init__(self, login=None, password=None, token=None, socket=None):
        if login and password:
            self.api = yandex_music.Client.from_credentials(login, password)
        if token:
            self.api = yandex_music.Client.from_token(token)
        self.api.report_new_fields = False
        self.api.report_new_fields_callback = False
        self.ids = 0
        if socket:
            self.socket = socket

    def save_token(self, user_id):
        db.add_service(user_id, self.api.token, 'yandex')

    def tracks(self, ids):
        tracks = []
        items = self.api.users_likes_tracks()
        for i in items:
            track = i.fetch_track()
            tracks.append({'title': track['title'], 'artist': track['artists'][0]['name'],
                           'album': track['albums'][0]['title'], 'service': 'yandex', 'id': str(uuid.uuid4())})
            ids += 1
        self.ids = ids
        return tracks

    def albums(self):
        albums = []
        items = self.api.users_likes_albums()
        count = 0
        for i in items:
            albums.append({'title': i['album']['title'], 'artist': i['album']['artists'][0]['name'],
                           'service': 'yandex', 'id': str(uuid.uuid4())})
            count += 1
        return albums

    def artists(self):
        artists = []
        items = self.api.users_likes_artists()
        count = 0
        for i in items:
            artists.append({'title': i['artist']['name'], 'service': 'yandex', 'id': str(uuid.uuid4())})
            count += 1
        return artists

    def playlists(self):
        playlists = []
        liked_playlists = self.api.users_playlists_list()
        user_playlists = self.api.users_likes_playlists()
        count = 0
        for i in user_playlists:
            info = self.api.playlists_list(i['playlist'].playlist_id)
            tracks_ya = info[0].fetch_tracks()
            tracks = []
            for b in tracks_ya:
                try:
                    tracks.append(b['track']['title'] + ' ' + b['track']['artists'][0].name)
                except:
                    tracks.append(b['track']['title'])
            playlists.append({'title': i['playlist']['title'], 'tracks': tracks,
                              'service': 'yandex', 'id': str(uuid.uuid4())})
            count += 1

        for i in liked_playlists:
            info = self.api.playlists_list(i.playlist_id)
            tracks_ya = info[0].fetch_tracks()
            tracks = []
            for b in tracks_ya:
                try:
                    tracks.append(b['track']['title'] + ' ' + b['track']['artists'][0].name)
                except:
                    tracks.append(b['track']['title'])
            playlists.append({'title': i['title'], 'tracks': tracks,
                              'service': 'yandex', 'id': str(uuid.uuid4())})
        return playlists

    def get_music(self, ids):
        return self.tracks(ids), self.albums(), self.artists(), self.playlists(), self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='track')
            try:
                items.append(result.tracks.results[0].track_id)
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_tracks(self, tracks, user_id, sub=config.TESTING):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in range(0, len(tracks_ids), 20):
                chunk = tracks_ids[i:i + 20]
                self.api.users_likes_tracks_add(chunk)
        if not sub:
            chunk = tracks_ids[0:db.check_free_transfer(user_id)]
            self.api.users_likes_tracks_add(chunk)
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - len(chunk))

    def search_albums_ids(self, albums, user_id):
        items = []
        tracks_db = db.get_audio(albums, 'albums', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='album')
            try:
                items.append(result.albums.results[0].id)
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_albums(self, albums, user_id, sub=config.TESTING):
        albums_ids = self.search_albums_ids(albums, user_id)
        if sub:
            for i in range(0, len(albums_ids), 20):
                chunk = albums_ids[i:i + 20]
                self.api.users_likes_albums_add(chunk)

    def search_artists_ids(self, artists, user_id):
        items = []
        tracks_db = db.get_audio(artists, 'artists', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='artist')
            try:
                items.append(result.artists.results[0].id)
                self.socket.emit('audio_found', {'data': 1})
            except:
                self.socket.emit('audio_found', {'data': 0})
        return items

    def transfer_artists(self, artists, user_id, sub=config.TESTING):
        artists_ids = self.search_artists_ids(artists, user_id)
        if sub:
            for i in range(0, len(artists_ids), 20):
                chunk = artists_ids[i:i + 20]
                self.api.users_likes_artists_add(chunk)

    def search_playlists_ids(self, playlists, user_id):
        items = []
        tracks_db = db.get_audio(playlists, 'playlists', user_id)
        for i in tracks_db:
            result = self.api.search(i, type_='playlist')
            items.append(result.playlists.results[0].id)
        return items

    def transfer_playlists(self, playlists, user_id, sub=config.TESTING):
        playlists_ids = db.get_audio(playlists, 'playlists', user_id)
        user_playlists = self.api.users_playlists_list()
        for i in user_playlists:
            for b in playlists_ids:
                if b['title'] == i['title']:
                    playlists_ids.remove(b)

        for i in playlists_ids:
            playlist = self.api.users_playlists_create(i['title'])
            tracks = []
            for b in i['tracks']:
                track = type
                try:
                    track = self.api.search(b, type_='track')
                except:
                    continue
                try:
                    tracks.append({'id': track.tracks.results[0].id, 'album_id': track.tracks.results[0].albums[0].id})
                    self.socket.emit('audio_found', {'data': 1})
                except:
                    self.socket.emit('audio_found', {'data': 0})
            diff = Difference().add_insert(0, tracks)
            self.api.users_playlists_change(playlist.kind, diff.to_json())


class Deezer:
    def __init__(self, token=None):
        self.api = deezer.Client(app_id=config.DEEZER_ID, app_secret=config.SPOTIFY_SECRET, access_token=token)
        self.base_url = 'https://api.deezer.com/'
        self.token = token
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
        perms = "basic_access,email,offline_access,manage_library,manage_community,delete_library,listening_history"
        response = requests.post('https://connect.deezer.com/oauth/access_token.php',
                                 params={'app_id': config.DEEZER_ID,
                                         'secret': config.DEEZER_SECRET_KEY,
                                         'code': code,
                                         'perms': perms,
                                         'output': 'json'})
        token = response.json()['access_token']
        db.add_service(user_id, token, 'deezer')

    def get(self, method, params={}):
        params.update({'access_token': self.token})
        response = requests.get(self.base_url + method, params=params)
        return response.json()

    def post(self, method, params={}):
        params.update({'access_token': self.token})
        response = requests.post(self.base_url + method, params=params)
        return response.json()

    def tracks(self):
        tracks = []
        items = self.api.get_user_tracks()
        for i in items:
            tracks.append({'title': i.title, 'artist': i.artist.name, 'album': i.album.title,
                           'service': 'deezer', 'id': str(uuid.uuid4())})
        return tracks

    def albums(self):
        albums = []
        items = self.api.get_user_albums()
        for i in items:
            albums.append({'title': i.title, 'artist': i.artist.name, 'service': 'deezer', 'id': str(uuid.uuid4())})
        return albums

    def artists(self):
        artists = []
        items = self.api.get_user_artists()
        for i in items:
            artists.append({'title': i.name, 'service': 'deezer', 'id': str(uuid.uuid4())})
        return artists

    def playlists(self):
        playlists = []
        items = self.get('user/me/playlists')
        for i in items['data']:
            tracks = []
            track_items = requests.get(i['tracklist'], params={'access_token': self.token}).json()
            if track_items['total'] > 0:
                if len(track_items['data']) == 25:
                    while track_items.get('next'):
                        for b in track_items['data']:
                            try:
                                tracks.append(b['title'] + ' ' + b['artist']['name'])
                            except:
                                tracks.append(b['title'])
                        track_items = requests.get(track_items['next'], {'access_token': self.token}).json()

                    if (len(track_items['data']) == 25) and (not track_items.get('next')):
                        for b in track_items['data']:
                            try:
                                tracks.append(b['title'] + ' ' + b['artist']['name'])
                            except:
                                tracks.append(b['title'])

                if (len(track_items['data']) < 25) and len(track_items['data']) > 0:
                    for b in track_items['data']:
                        try:
                            tracks.append(b['title'] + ' ' + b['artist']['name'])
                        except:
                            tracks.append(b['title'])

            playlists.append({'title': i['title'], 'service': 'deezer', 'tracks': tracks, 'id': str(uuid.uuid4())})
        return playlists

    def get_music(self, ):
        return self.tracks(), self.albums(), self.artists(), self.playlists(), self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.api.search(i, ordering='TRACK_ASC')
            for i in result:
                items.append(i.id)
                break
        return items

    def transfer_tracks(self, tracks, user_id, sub=config.TESTING):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in tracks_ids:
                try:
                    self.api.add_user_track(i)
                except:
                    pass
        if not sub:
            chunk = tracks_ids[0:db.check_free_transfer(user_id)]
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

    def transfer_albums(self, albums, user_id, sub=config.TESTING):
        albums_ids = self.search_albums_ids(albums, user_id)
        if sub:
            for i in albums_ids:
                try:
                    self.api.add_user_album(i)
                except:
                    pass

    def search_artists_ids(self, artists, user_id):
        items = []
        artists_db = db.get_audio(artists, 'artists', user_id)
        for i in artists_db:
            result = self.api.search(i, ordering='ARTIST_ASC')
            for i in result:
                items.append(i.artist.id)
                break
        return items

    def transfer_artists(self, artists, user_id, sub=config.TESTING):
        artists_ids = self.search_artists_ids(artists, user_id)
        if sub:
            for i in artists_ids:
                try:
                    self.api.add_user_artist(i)
                except:
                    pass

    def transfer_playlists(self, playlists, user_id, sub=config.TESTING):
        playlists = db.get_audio(playlists, 'playlists', user_id)
        de_playlists = self.get('user/me/playlists')['data']
        if sub:
            for i in playlists:
                for b in de_playlists:
                    if i['title'] == b['title']:
                        playlists.remove(i)

            for i in playlists:
                errors = 0
                tracks = []
                playlist_id = self.post('user/me/playlists', params={'title': i['title']})['id']

                for b in i['tracks']:
                    result = self.api.search(b, ordering='TRACK_ASC')
                    if len(result) > 0:
                        tracks.append(result[0].id)

                    if len(result) == 0:
                        errors += 1
                    print(f"Найдено {len(tracks)} из {len(i['tracks'])}")
                    print(f"Не найдено {errors} \n")

                for b in range(0, len(tracks), 50):
                    chunk = str(tracks[b:b + 50]).replace('[', '').replace(']', '')
                    self.post(f"playlist/{playlist_id}/tracks", params={'songs': chunk})


class Napster:
    def __init__(self, token=None, user_id=None):
        self.api = None
        self.token = token
        self.user_id = user_id
        self.ids = 0
        try:
            self.refresh_token = db.get_refr_token(user_id, 'napster')
        except:
            self.refresh_token = None
        self.base_url = 'https://api.napster.com/v2.2/'

    @staticmethod
    def create_url():
        params = urllib.parse.urlencode({'client_id': config.NAPSTER_KEY,
                                         'redirect_uri': config.NAPSTER_REDIRECT,
                                         'response_type': 'code'})
        return 'https://api.napster.com/oauth/authorize' + '?' + params

    def get_token(self, code, user_id):
        response = requests.post('https://api.napster.com/oauth/access_token', {
            'client_id': config.NAPSTER_KEY,
            'client_secret': config.NAPSTER_SECRET,
            'response_type': 'code',
            'grant_type': 'authorization_code',
            'redirect_uri': config.NAPSTER_REDIRECT,
            'code': code
        }).json()

        self.token = response['access_token']
        self.refresh_token = response['refresh_token']

    def refr_token(self):
        response = requests.post('https://api.napster.com/oauth/access_token', {
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token',
            'client_id': config.NAPSTER_KEY,
            'client_secret': config.NAPSTER_SECRET
        })
        self.token = response.json()['access_token']
        self.refresh_token = response.json()['refresh_token']
        self.save_token()

    def get(self, method, params=None):
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token)
        }

        response = requests.get(self.base_url + method, params, headers=headers)
        if response.status_code == 401:
            try:
                if response.json()['error']['message'] == 'The access token expired':
                    self.refr_token()
                    self.get(method, params)
            except:
                pass
            try:
                if response.json()['code'] == 'UnauthorizedError':
                    self.refr_token()
                    self.get(method, params)
            except:
                pass
        return response.json()

    def post(self, method, params=None, send_json=None):
        headers = {
            'Authorization': 'Bearer {token}'.format(token=self.token),
            'Content-Type': 'application/json'
        }

        response = requests.post(self.base_url + method, params=params, json=send_json, headers=headers)
        a = 9872634

    def get_music(self, offset, ids):
        self.ids = ids
        tracks = []
        albums = []
        playlists = []
        artists = []
        items = self.get('me/favorites', {'offset': offset, 'limit': 15})
        for i in items['favorites']['data']['tracks']:
            tracks.append({'title': i['name'], 'artist': i['artistName'], 'album': i['albumName'],
                           'service': 'napster', 'id': str(uuid.uuid4())})
            self.ids += 1
        items = self.get('me/library/artists', {'offset': offset, 'limit': 15})
        for i in items['artists']:
            artists.append({'title': i['name'], 'id': str(uuid.uuid4()), 'photo': None, 'service': 'napster'})
            self.ids += 1

        items = self.get('me/library/albums', {'offset': offset, 'limit': 15})
        for i in items['albums']:
            albums.append({'title': i['name'], 'id': str(uuid.uuid4()), 'photo': None,
                           'service': 'napster'})
            self.ids += 1
        return tracks, albums, artists, self.ids

    def search_tracks_ids(self, tracks, user_id):
        items = []
        tracks_db = db.get_audio(tracks, 'tracks', user_id)
        for i in tracks_db:
            result = self.get('search', {'query': i, 'type': 'track'})
            for i in result['search']['data']['tracks']:
                items.append(i['id'])
                break
        return items

    def transfer_tracks(self, tracks, user_id, sub=config.TESTING):
        tracks_ids = self.search_tracks_ids(tracks, user_id)
        if sub:
            for i in tracks_ids:
                try:
                    self.post('me/favorites', send_json={'favorites': [{'id': i}]})
                except:
                    pass
        if not sub:
            chunk = tracks_ids[0:db.check_free_transfer(user_id)]
            count = 0
            for i in chunk:
                try:
                    self.post('me/favorites', {'favorites': [{'id': i}]})
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def search_albums_ids(self, albums, user_id):
        items = []
        tracks_db = db.get_audio(albums, 'albums', user_id)
        for i in tracks_db:
            result = self.get('search', {'query': i, 'type': 'album'})
            for i in result['search']['data']['tracks']:
                items.append(i['id'])
                break
        return items

    def transfer_albums(self, albums, user_id, sub=config.TESTING):
        albums_ids = self.search_albums_ids(albums, user_id)
        if sub:
            for i in albums_ids:
                try:
                    self.post('me/favorites', send_json={'favorites': [{'id': i}]})
                except:
                    pass
        if not sub:
            chunk = albums_ids[0:db.check_free_transfer(user_id)]
            count = 0
            for i in chunk:
                try:
                    self.post('me/favorites', {'favorites': [{'id': i}]})
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def search_artists_ids(self, artists, user_id):
        items = []
        tracks_db = db.get_audio(artists, 'artists', user_id)
        for i in tracks_db:
            result = self.get('search', {'query': i, 'type': 'artists'})
            for i in result['search']['data']['tracks']:
                items.append(i['id'])
                break
        return items

    def transfer_artists(self, artists, user_id, sub=config.TESTING):
        artists_ids = self.search_artists_ids(artists, user_id)
        if sub:
            for i in artists_ids:
                try:
                    self.post('me/favorites', send_json={'favorites': [{'id': i}]})
                except:
                    pass
        if not sub:
            chunk = artists_ids[0:db.check_free_transfer(user_id)]
            count = 0
            for i in chunk:
                try:
                    self.post('me/favorites', {'favorites': [{'id': i}]})
                    count += 1
                except:
                    pass
            db.use_free_transfer(user_id, db.check_free_transfer(user_id) - count)

    def save_token(self):
        db.add_service(self.user_id, self.token, 'napster')
        db.save_refresh_token(self.user_id, self.refresh_token(), 'napster')
