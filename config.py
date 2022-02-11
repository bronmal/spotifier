URL = 'http://127.0.0.1:5000'
LIMIT = 9

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




class Config(object):
    LANGUAGES = ['ru', 'en', 'es', 'fr', 'de']
