import json
import urllib.parse
import config
import vk_api


def vk_create_link():
    params = urllib.parse.urlencode({
        'client_id': 7938876,
        'redirect_uri': config.URL + '/auth',
        'display': 'popup',
        'scope': 'email',
        'response_type': 'token'
    })
    return 'https://oauth.vk.com/authorize' + '?' + params


def vk_auth(token):
    vk = vk_api.VkApi(token=token)
    name = vk.method('users.get')
    print(name)
