import urllib.parse
import config
import vk_api
import spotipy
import requests
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
import db_orm as db


class VkAuth:
    def __init__(self, login=None, password=None):
        self.login = login
        self.password = password
        self.session = requests.session()

    @staticmethod
    def create_link():
        params = urllib.parse.urlencode({
            'client_id': 7938876,
            'redirect_uri': config.URL + '/auth_vk',
            'display': 'popup',
            'scope': 'email',
            'response_type': 'code'
        })
        return 'https://oauth.vk.com/authorize' + '?' + params

    @staticmethod
    def info(code):
        return requests.get('https://oauth.vk.com/access_token', params={
            'client_id': 7938876,
            'client_secret': '7kjFGKtvWD2f2aKBRq13',
            'redirect_uri': config.URL + '/auth_vk',
            'code': code
        }).json()

    @staticmethod
    def name(token):
        vk = vk_api.VkApi(token=token)
        name = vk.method('users.get')
        return name

    @staticmethod
    def avatar(token):
        vk = vk_api.VkApi(token=token)
        photo_url = vk.method('users.get', values={'fields': 'photo_100'})[0]['photo_100']
        photo = requests.get(photo_url).content
        return photo

    def connect(self, two_fa=False, code=None):
        return self.session.get('https://oauth.vk.com/token', params={
            'grant_type': 'password',
            'client_id': '6146827',
            'client_secret': 'qVxWRF1CwHERuIrKBnqe',
            'username': self.login,
            'password': self.password,
            'v': '5.131',
            '2fa_supported': '1',
            'force_sms': '1' if two_fa else '0',
            'code': code if two_fa else None
        }).json()

    def validate_phone(self, response):
        response = self.session.get("https://api.vk.com/method/auth.validatePhone",
                                    params={'sid': response['validation_sid'], 'v': '5.131'})


class SpotAuth:
    def __init__(self):
        self.spot = None
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

    def create_link(self):
        return self.auth_manager.get_authorize_url()

    def name(self, code):
        self.auth_manager.get_access_token(code, as_dict=False)
        self.spot = spotipy.Spotify(auth_manager=self.auth_manager)
        photo = None
        try:
            photo_url = self.spot.me()['images'][0]['url']
            photo = requests.get(photo_url).content
        except:
            photo_url = None
        return self.spot.me()['display_name'], self.spot.me()['email'], photo

    def save_token(self, code, user_id):
        token = self.auth_manager.get_access_token(code, as_dict=False,  check_cache=False)
        db.add_service(user_id, token, 'spotify')


class GoogleAuth:
    def __init__(self):
        self.session = OAuth2Session(config.GOOGLE_ID, config.GOOGLE_SECRET,
                                     scope='openid email profile',
                                     redirect_uri=config.URL + '/auth_google')
        self.oauth2_tokens = None

    def build_credentials(self):
        return google.oauth2.credentials.Credentials(
            self.oauth2_tokens['access_token'],
            refresh_token=self.oauth2_tokens['refresh_token'],
            client_id=config.GOOGLE_ID,
            client_secret=config.GOOGLE_SECRET,
            token_uri=config.GOOGLE_ACCESS_TOKEN_URI)

    def create_link(self):
        url, state = self.session.create_authorization_url(config.GOOGLE_AUTHORIZATION_URL)
        return url, state

    def name(self, state, full_url):
        self.session = OAuth2Session(config.GOOGLE_ID, config.GOOGLE_SECRET,
                                     scope='openid email profile',
                                     state=state,
                                     redirect_uri=config.URL + '/auth_google')
        self.oauth2_tokens = self.session.fetch_access_token(
            config.GOOGLE_ACCESS_TOKEN_URI,
            authorization_response=full_url)
        credentials = self.build_credentials()
        oauth2_client = googleapiclient.discovery.build(
            'oauth2', 'v2',
            credentials=credentials)
        photo = requests.get(oauth2_client.userinfo().get().execute()['picture']).content
        return oauth2_client.userinfo().get().execute()['name'], oauth2_client.userinfo().get().execute()['email'], \
               photo


class YandexAuth:
    @staticmethod
    def create_link():
        return f'https://oauth.yandex.ru/authorize?response_type=code&client_id={config.YANDEX_ID}'

    @staticmethod
    def get_info(code):
        response = requests.post('https://oauth.yandex.ru/token', data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': config.YANDEX_ID,
            'client_secret': config.YANDEX_PASSWORD
        })

        info = requests.get('https://login.yandex.ru/info', params={
            'format': 'json',
            'with_openid_identity': 'yes',
            'oauth_token': response.json()['access_token']
        }).json()

        photo_url = f"https://avatars.yandex.net/get-yapic/{info['default_avatar_id']}/islands-200"
        photo = requests.get(photo_url).content

        return info['last_name']+info['first_name'], info['default_email'], photo
