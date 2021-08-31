import vk_api
import requests
from mt_tester.utils import Account
from logger import log


dic = {'Ь': '', 'ь': '', 'Ъ': '', 'ъ': '', 'А': 'A', 'а': 'a', 'Б': 'B', 'б': 'b', 'В': 'V', 'в': 'v',
       'Г': 'G', 'г': 'g', 'Д': 'D', 'д': 'd', 'Е': 'E', 'е': 'e', 'Ё': 'E', 'ё': 'e', 'Ж': 'Zh', 'ж': 'zh',
       'З': 'Z', 'з': 'z', 'И': 'I', 'и': 'i', 'Й': 'I', 'й': 'i', 'К': 'K', 'к': 'k', 'Л': 'L', 'л': 'l',
       'М': 'M', 'м': 'm', 'Н': 'N', 'н': 'n', 'О': 'O', 'о': 'o', 'П': 'P', 'п': 'p', 'Р': 'R', 'р': 'r',
       'С': 'S', 'с': 's', 'Т': 'T', 'т': 't', 'У': 'U', 'у': 'u', 'Ф': 'F', 'ф': 'f', 'Х': 'Kh', 'х': 'kh',
       'Ц': 'Tc', 'ц': 'tc', 'Ч': 'Ch', 'ч': 'ch', 'Ш': 'Sh', 'ш': 'sh', 'Щ': 'Shch', 'щ': 'shch', 'Ы': 'Y',
       'ы': 'y', 'Э': 'E', 'э': 'e', 'Ю': 'Iu', 'ю': 'iu', 'Я': 'Ia', 'я': 'ia'}

alphabet = ['Ь', 'ь', 'Ъ', 'ъ', 'А', 'а', 'Б', 'б', 'В', 'в', 'Г', 'г', 'Д', 'д', 'Е', 'е', 'Ё', 'ё',
            'Ж', 'ж', 'З', 'з', 'И', 'и', 'Й', 'й', 'К', 'к', 'Л', 'л', 'М', 'м', 'Н', 'н', 'О', 'о',
            'П', 'п', 'Р', 'р', 'С', 'с', 'Т', 'т', 'У', 'у', 'Ф', 'ф', 'Х', 'х', 'Ц', 'ц', 'Ч', 'ч',
            'Ш', 'ш', 'Щ', 'щ', 'Ы', 'ы', 'Э', 'э', 'Ю', 'ю', 'Я', 'я']


class Auth:
    def __init__(self, login, password):
        self.login = login
        self.password = password
        self.session = requests.session()

    def auth(self, two_fa=False, code=None):
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
        print(response.text)


@log
def get_tracks(token, user_id):
    user = vk_api.VkApi(token=token)
    count = user.method('audio.getCount', values={'owner_id': user_id})
    result = user.method('audio.get', values={'count': count})
    print(result)
    title_author = []

    for i in result['items']:
        q = i['title'] + ' ' + i['artist']
        title_author.append(q)

    return title_author
