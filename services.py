import vk_api


class Vk:
    def __init__(self, token):
        self.api = vk_api.VkApi(token=token)

    def tracks(self):
        return self.api.method('audio.get')
