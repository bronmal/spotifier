URL = 'http://127.0.0.1:5000'
LIMIT = 9
TESTING = True

DB_LOGIN = 'mysql'
DB_PASS = '1q2w3e4r5'
DB_DATABASE = 'spotifier'

SHOP_ID = 822381
SHOP_TOKEN = 'test_Z0bQfQgOZa2d_KbHJmo4j65IfoiG7OPfdCLvfrz5VtE'

SPOTIFY_ID = 'b1fa88d88e3042d8b40e21af7e55a0ba'
SPOTIFY_SECRET = '0b6e4567fb7b4cf0b60243579bccf94c'
SPOTIFY_REDIRECT = f'{URL}/auth_spotify'

GOOGLE_ID = '835837949353-evpleoubufejftjurlln3as591072457.apps.googleusercontent.com'
GOOGLE_SECRET = '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'
GOOGLE_AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
GOOGLE_ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'

YANDEX_ID = '0b9c2c40111e4accbf1fd0129e2a3910'
YANDEX_PASSWORD = '0163828d485842a3a40d4a6780b9d028'

DEEZER_ID = 527262
DEEZER_SECRET_KEY = '9d0efed71f127a12e58b9e057d9cb2f3'
DEEZER_REDIRECT = f'{URL}/add_deezer'

LASTFM_KEY = '6cddd7f7f30775e9c8970f39504f41b3'
LASTFM_SECRET = '811ebd41610df4fc80edf9bc7d6982a5'
LASTFM_REDIRECT = f'{URL}/add_lastfm'

NAPSTER_KEY = 'NjhiMjRlNmUtOTljZi00ZTE2LWFmZWUtZDZjZTYxMGJhZmE2'
NAPSTER_SECRET = 'NDViYzY0M2EtMGM1My00YWQ2LTkwZTItYTlhZGIzMGQwYmZh'
NAPSTER_ID = 'f8caf26b-587a-400b-961d-17586e4a6a2f'
NAPSTER_REDIRECT = f'{URL}/add_napster'


class Config(object):
    LANGUAGES = ['ru', 'en', 'es', 'fr', 'de']
