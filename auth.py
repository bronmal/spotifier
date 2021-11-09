import json
import urllib.parse
import requests
import config


def vk_create_link():
    params = urllib.parse.urlencode({
        'client_id': 7938876,
        'redirect_uri': config.URL + '/auth',
        'display': 'popup',
        'scope': 'email',
        'response_type': 'code'
    })
    return 'https://oauth.vk.com/authorize' + '?' + params


def vk_get_token(code):
    session = requests.session()
    response = session.get('https://oauth.vk.com/access_token', params={
        'client_id': 7938876,
        'client_secret': '7kjFGKtvWD2f2aKBRq13',
        'redirect_uri': config.URL + '/auth',
        'code': code
    }).json()
    print(response.get('email'))
