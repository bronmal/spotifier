import os
import uuid
import config
import auth
import db_orm as db
import kassa
import services
from flask import Flask, session, request, redirect, render_template, json, send_from_directory, Response
from flask_login import current_user, login_user, logout_user, login_required
from flask_session import Session
from flask_babel import Babel, _
from flask_babel_js import BabelJS
from users import login, User

application = Flask(__name__)
login.init_app(application)

# login.login_view = '/auth'

application.config['SECRET_KEY'] = os.urandom(64)
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = '.flask_session/'
Session(application)
babel = Babel(application)
babel_js = BabelJS(application)

os.environ['SPOTIPY_CLIENT_ID'] = config.SPOTIFY_ID
os.environ['SPOTIPY_CLIENT_SECRET'] = config.SPOTIFY_SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = config.SPOTIFY_REDIRECT


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(config.Config.LANGUAGES)


caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


@application.route('/')
@login_required
def main_page():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return redirect('/dashboard')#render_template('index.html')


@login.user_loader
def load_user(id):
    user = User(db.get_user_by_id(int(id)))
    return user


@application.route('/img')
def serve_img():
    return Response(db.get_user_info_dashboard(current_user.get_id(), True))


def auth_in(email, name, photo):
    if db.in_db(email):
        user = User(db.get_user_by_email(email))
        login_user(user)
    else:
        db.create_user(email, name, photo)
        user = User(db.get_user_by_email(email))
        login_user(user)


@application.route('/auth')
def authorization():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())
    if current_user.is_authenticated:
        return redirect('/dashboard')

    vkont = auth.VkAuth()
    spot = auth.SpotAuth()
    gle = auth.GoogleAuth()
    yad = auth.YandexAuth()

    url_google = gle.create_link()
    session['google_state'] = url_google[1]

    urls = dict()
    urls.update({'vk': vkont.create_link()})
    urls.update({'spotify': spot.create_link()})
    urls.update({'google': url_google[0]})
    urls.update({'yandex': yad.create_link()})

    return render_template('auth.html', google=urls['google'], vk=urls['vk'], spotify=urls['spotify'],
                           yandex=urls['yandex'])


@application.route('/auth_vk')
def vk():
    if request.args.get('code'):
        vkont = auth.VkAuth()
        info = vkont.info(request.args.get('code'))
        try:
            email = info['email']
            token = info['access_token']
            user_get = vkont.name(token)
            name = user_get[0]['first_name'] + ' ' + user_get[0]['last_name']
            photo = vkont.avatar(token)
            auth_in(email, name, photo)
            return redirect('/dashboard')
        except Exception as err:
            print(err)
            return redirect('/auth')


@application.route('/auth_spotify')
def spotify():
    if current_user.get_id() is None:
        if request.args.get('code'):
            try:
                spot = auth.SpotAuth()
                spot.get_token(request.args.get('code'))
                name, email, photo = spot.get_name()
                auth_in(email, name, photo)
                spot.save_token(current_user.get_id())
                return redirect('/dashboard')
            except:
                return redirect('/auth')
    if current_user.get_id():
        if request.args.get('code'):
            spot = auth.SpotAuth(user_id=current_user.get_id())
            spot.get_token(request.args.get('code'))
            # name, email, photo = spot.get_name()
            spot.save_token(current_user.get_id())
            return redirect('/dashboard')


@application.route('/auth_google')
def google():
    try:
        gle = auth.GoogleAuth()
        name, email, photo = gle.name(session['google_state'], request.url)
        auth_in(email, name, photo)
        return redirect('/dashboard')
    except Exception as err:
        print(err)
        return redirect('/auth')


@application.route('/auth_yandex')
def yandex():
    try:
        if request.args.get('code'):
            yad = auth.YandexAuth()
            name, email, photo = yad.get_info(request.args.get('code'))
            auth_in(email, name, photo)
            return redirect('/dashboard')
    except Exception as err:
        print(err)
        return redirect('/auth')


@application.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@application.route('/dashboard')
@login_required
def dashboard():
    session['ids'] = 0
    db.delete_cache(current_user.get_id())
    name, date_end, subscription, services_connected, avatar = db.get_user_info_dashboard(
        current_user.get_id())
    if db.get_user_by_id(current_user.get_id()).subscription == 0:
        return render_template('app.html', name=name, data_end='', avatar=avatar,
                               kassa=kassa.create_payment(current_user.get_id()), kassa_text=_('Оформить подписку'))
    if db.get_user_by_id(current_user.get_id()).subscription == 1:
        return render_template('app.html', name=name, data_end=date_end, avatar=avatar,
                               kassa='/disconnect_sub', kassa_text=_('Отключить подписку'))
    # добавить обработчик создания нового токена, во избежание устаревания токена


@application.route('/get_services', methods=['GET'])
@login_required
def get_services():
    services_with_token = db.get_connected_services(current_user.get_id())
    services_name = []
    for i in services_with_token:
        services_name.append(i)
    return json.dumps(services_name)


@application.route('/delete_service', methods=['GET'])
@login_required
def delete_service():
    service = request.args.get('service')
    db.remove_service(current_user.get_id(), service)
    return json.dumps({'success': True})


@application.route('/get_audio', methods=['POST', 'GET'])
@login_required
def send_audio():
    service_name = request.args.get('service')
    offset = int(request.args.get('offset'))
    service_token = db.get_token(current_user.get_id(), service_name)
    tracks, playlists, albums, artists = [], [], [], []

    if service_name == 'vk':
        api_vk = services.Vk(service_token)
        tracks, playlists, albums, ids = api_vk.get_music(offset, session['ids'])
        session['ids'] = ids

    if service_name == 'spotify':
        api_spotify = services.Spotify(service_token)
        tracks, playlists, artists, albums, ids = api_spotify.get_music(offset, session['ids'])
        session['ids'] = ids

    if service_name == 'yandex':
        api_yandex = services.Yandex(token=service_token)
        tracks, albums, artists, playlists, ids = api_yandex.get_music(session['ids'])
        session['ids'] = ids

    if service_name == 'deezer':
        api_deezer = services.Deezer(token=service_token)
        tracks, albums, artists, ids = api_deezer.get_music()
        session['ids'] = ids

    db.save_music(current_user.get_id(), tracks=tracks)
    print(service_name, tracks)

    return json.dumps({'tracks': tracks,
                       'albums': albums,
                       'playlists': playlists,
                       'artists': artists})


@application.route('/send_audio', methods=['POST'])
def get_audio():
    if request.method == 'POST':
        tracks = request.json['tracks']
        albums = request.json['albums']
        playlists = request.json['playlists']
        artists = request.json['artists']
        to_service = request.json['to_service']

        vk_token = db.get_token(current_user.get_id(), 'vk')
        spotify_token = db.get_token(current_user.get_id(), 'spotify')
        yandex_token = db.get_token(current_user.get_id(), 'yandex')
        deezer_token = db.get_token(32, 'deezer')

        if to_service == 'spotify':
            if spotify_token:
                api = services.Spotify(spotify_token)
                if db.check_sub(current_user.get_id()):
                    api.transfer_tracks(tracks, current_user.get_id())
                    api.transfer_albums(albums, current_user.get_id())
                    api.transfer_artists(artists, current_user.get_id())
                    # api.transfer_playlists(playlists, 27)
                if not db.check_sub(current_user.get_id()) and db.check_free_transfer(current_user.get_id()) > 0:
                    api.transfer_tracks(tracks, current_user.get_id(), False)
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': _('Ошибка: добавьте сервис Spotify')})

        if to_service == 'vk':
            if vk_token:
                api = services.Vk(vk_token)
                if db.check_sub(current_user.get_id()):
                    api.transfer_tracks(tracks, current_user.get_id())
                if not db.check_sub(current_user.get_id()) and db.check_free_transfer(current_user.get_id()) > 0:
                    api.transfer_tracks(tracks, current_user.get_id(), False)
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': _('Ошибка: добавьте сервис Vk')})

        if to_service == 'yandex':
            if yandex_token:
                api = services.Yandex(token=yandex_token)
                if db.check_sub(current_user.get_id()):
                    api.transfer_tracks(tracks, current_user.get_id())
                    api.transfer_albums(albums, current_user.get_id())
                    api.transfer_artists(artists, current_user.get_id())
                    # api.transfer_playlists(playlists, 32)
                if not db.check_sub(current_user.get_id()) and db.check_free_transfer(current_user.get_id()) > 0:
                    api.transfer_tracks(tracks, current_user.get_id(), False)
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': _('Ошибка: добавьте сервис Yandex')})

        if to_service == 'deezer':
            if deezer_token:
                api = services.Deezer(token=deezer_token)
                if db.check_sub(32):
                    api.transfer_tracks(tracks, current_user.get_id())
                    api.transfer_albums(albums, current_user.get_id())
                    api.transfer_artists(artists, 32)
                if not db.check_sub(32) and db.check_free_transfer(32) > 0:
                    api.transfer_tracks(tracks, 32, False)
                return json.dumps({'success': True})
            else:
                return json.dumps({'success': False, 'error': _('Ошибка: добавьте сервис Deezer')})


@application.route('/add_vk', methods=['get', 'post'])
@login_required
def add_vk():
    if not session.get('uuid'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('vk_form_test.html')


@application.route('/get_auth_data', methods=['POST'])
@login_required
def get_auth_data():
    vk_login = auth.VkAuth(request.json['login'], request.json['pass'])
    session['vk_account'] = vk_login
    response = vk_login.connect()
    if 'validation_sid' in response:
        vk_login.validate_phone(response)
        return json.dumps({'2fa_required': True})
    if 'access_token' in response:
        session['user_id'] = response['user_id']
        session['token'] = response['access_token']
        db.add_service(current_user.get_id(), response['access_token'], 'vk')
        return json.dumps({'2fa_required': False})
    if 'captcha_sid' in response:
        return json.dumps({'wrong_password': True})
    if response['error_type'] == 'username_or_password_is_incorrect':
        return json.dumps({'wrong_password': True})


@application.route('/get_code', methods=['POST', 'GET'])
@login_required
def get_code():
    vk_login = session['vk_account']
    code = request.json['code']
    if request.method == 'POST':
        response = vk_login.connect(True, code)
        if 'access_token' in response:
            session['user_id'] = response['user_id']
            db.add_service(current_user.get_id(), response['access_token'], 'vk')
            return json.dumps({'success': True})
        if 'access_token' not in response:
            return json.dumps({'success': False})


@application.route('/add_yandex', methods=['GET', 'POST'])
@login_required
def add_yandex():
    if request.method == 'GET':
        return render_template('yandex_form_test.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        yandex_api = services.Yandex(username, password)
        yandex_api.save_token(current_user.get_id())
        return redirect('/dashboard')


@application.route('/add_deezer', methods=['GET', 'POST'])
@login_required
def add_deezer():
    if request.method == 'POST':
        services.Deezer.save_token(request.args.get('code'), current_user.get_id())
        return redirect('/dashboard')


@application.errorhandler(401)
def err_401(e):
    return _('не авторизован')


@application.route('/.well-known')
def apple_pay():
    return send_from_directory('static', 'apple-developer-merchantid-domain-association')


@application.route('/check_payment')
@login_required
def check_payment():
    yookassa_id = db.get_yookassa_id(int(request.args.get('login')))
    info_payment = kassa.check(yookassa_id)
    if info_payment.paid is True and info_payment.payment_method.saved is True:
        db.user_payed(current_user.get_id(), info_payment.payment_method.id)
        return redirect('/dashboard')
    else:
        return redirect('/')


@application.route('/disconnect_sub')
@login_required
def disconnect_sub():
    db.delete_sub(current_user.get_id())
    return redirect('/dashboard')


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 5000)), host='127.0.0.1')
