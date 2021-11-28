import vk_api


class Vk:
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)
        self.user_id = self.api.method('users.get')[0]['id']
        self.count = self.api.method('audio.getCount', values={'owner_id': self.user_id})

    def tracks(self):
        return self.api.method('audio.get', values={'count': self.count})

    def playlists_albums(self):
        return self.api.method('audio.getPlaylists', values={'owner_id': self.user_id})

    def get_music(self, tracks, playlists, albums):
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
