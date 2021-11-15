import urllib.parse
import config
import vk_api
import spotipy
import requests
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery


class VkAuth:
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


class SpotAuth:
    def __init__(self):
        self.spot = None
        self.auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private '
                                                              'playlist-modify-public ugc-image-upload '
                                                              'user-library-read '
                                                              'playlist-read-private '
                                                              'user-top-read '
                                                              'user-read-email',
                                                        show_dialog=True)

    def create_link(self):
        return self.auth_manager.get_authorize_url()

    def name(self, code):
        self.auth_manager.get_access_token(code, as_dict=False)
        self.spot = spotipy.Spotify(auth_manager=self.auth_manager)
        return self.spot.me()['display_name'], self.spot.me()['email']


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
        return oauth2_client.userinfo().get().execute()['name'], oauth2_client.userinfo().get().execute()['email']
