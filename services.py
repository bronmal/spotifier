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
