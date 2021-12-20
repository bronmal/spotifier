import os
import uuid
import config
import auth
import db
import services
from flask import Flask, session, request, redirect, render_template, json, send_from_directory, Response
from flask_login import current_user, login_user, logout_user, login_required
from flask_session import Session
from users import login, User

application = Flask(__name__)
login.init_app(application)

# login.login_view = '/auth'

application.config['SECRET_KEY'] = os.urandom(64)
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = '.flask_session/'
Session(application)

os.environ['SPOTIPY_CLIENT_ID'] = config.ID
os.environ['SPOTIPY_CLIENT_SECRET'] = config.SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = config.REDIRECT

caches_folder = '.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


@application.route('/')
@login_required
def main_page():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return render_template('index.html')


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
                name, email, photo = spot.name(request.args.get('code'))
                auth_in(email, name, photo)
                return redirect('/dashboard')
            except:
                return redirect('/auth')


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
def dashboard():
    tracks_vk, playlists_vk, albums_vk = [], [], []
    tracks_spot, playlists_spot, albums_spot, artists_spot = [], [], [], []

    vk_token = db.get_token(current_user.get_id(), 'vk')
    spotify_token = db.get_token(current_user.get_id(), 'spotify')
    if vk_token:
        api_vk = services.Vk(vk_token)
        tracks_vk, playlists_vk, albums_vk = api_vk.get_music()
    if spotify_token:
        api_spotify = services.Spotify(spotify_token)
        tracks_spot, playlists_spot, artists_spot, albums_spot = api_spotify.get_music()

    db.save_music(current_user.get_id(), tracks=tracks_vk + tracks_spot, albums=albums_vk + albums_spot,
                  playlists=playlists_vk + playlists_spot, artists=artists_spot)

    name, date_end, subscription, services_connected, avatar = db.get_user_info_dashboard(
        current_user.get_id())
    return render_template('app.html', name=name, data_end=date_end, avatar=avatar), json.dumps(
        {'subscription': subscription,
         'services': services_connected, 'tracks': tracks_vk + tracks_spot, 'albums': albums_vk + albums_spot,
         'playlists': playlists_vk + playlists_spot, 'artists': artists_spot})
    # добавить обработчик создания нового токена, во избежании устаревания токена


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


@application.route('/add_spotify', methods=['POST'])
@login_required
def add_spotify():
    if request.method == 'POST':
        if request.args.get('code'):
            try:
                spot = auth.SpotAuth()
                spot.save_token(request.args.get('code'), current_user.get_id())
                return redirect('/dashboard')
            except:
                return redirect('/auth')



@application.errorhandler(401)
def err_401(e):
    return 'не авторизован'


@application.route('/.well-known')
def apple_pay():
    return send_from_directory('static', 'apple-developer-merchantid-domain-association')


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 5000)), host='127.0.0.1')
