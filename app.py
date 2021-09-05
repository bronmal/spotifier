import os
import uuid
import config
import spotipy
import db
import kassa
from flask import Flask, session, request, redirect, render_template, json
from flask_session import Session
from get_tracks import get_tracks, Auth
from add_spotify import search_add
from logger import log
import json

application = Flask(__name__)
application.config['SECRET_KEY'] = os.urandom(64)
application.config['SESSION_TYPE'] = 'filesystem'
application.config['SESSION_FILE_DIR'] = './flask_session/'
Session(application)

os.environ['SPOTIPY_CLIENT_ID'] = config.ID
os.environ['SPOTIPY_CLIENT_SECRET'] = config.SECRET
os.environ['SPOTIPY_REDIRECT_URI'] = config.REDIRECT


caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)


def session_cache_path():
    return caches_folder + session.get('uuid')


@application.route('/')
@log
def main_page():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return render_template('index.html')


@application.route('/auth_vk', methods=['get', 'post'])
@log
def vk():
    if not session.get('uuid'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('vk_form.html')


@application.route('/get_auth_data', methods=['POST'])
@log
def get_auth_data():
    vk_login = Auth(request.json['login'], request.json['pass'])
    session['vk_account'] = vk_login
    response = vk_login.auth()
    print(response)
    if 'validation_sid' in response:
        vk_login.validate_phone(response)
        return json.dumps({'2fa_required': True})
    if 'access_token' in response:
        session['user_id'] = response['user_id']
        session['token'] = response['access_token']
        return json.dumps({'2fa_required': False})
    if 'captcha_sid' in response:
        return json.dumps({'wrong_password': True})
    if response['error_type'] == 'username_or_password_is_incorrect':
        return json.dumps({'wrong_password': True})


@application.route('/get_code', methods=['POST', 'GET'])
@log
def get_code():
    vk_login = session['vk_account']
    code = request.json['code']
    if request.method == 'POST':
        response = vk_login.auth(True, code)
        if 'access_token' in response:
            session['user_id'] = response['user_id']
            session['token'] = response['access_token']
            return json.dumps({'success': True})
        if 'access_token' not in response:
            return json.dumps({'success': False})
        

@application.route('/auth_spotify')
@log
def spotify():
    if not session.get('uuid'):
        return redirect('/')

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-private '
                                                     'playlist-modify-public ugc-image-upload',
                                               cache_path=session_cache_path(), show_dialog=True)

    if request.args.get("code"):
        auth_manager.get_access_token(request.args.get("code"), as_dict=False)
        return redirect('/auth_spotify')

    if not auth_manager.get_cached_token():
        auth_url = auth_manager.get_authorize_url()
        return render_template('spotify_form.html', auth_url=auth_url)

    spot = spotipy.Spotify(auth_manager=auth_manager)
    session['spotify'] = spot
    session['login_sp'] = spot.me()['id']
    return redirect('/result')


@application.route('/result')
@log
def waiting_page():
    if not session.get('uuid'):
        return redirect('/')
    else:
        try:
            vk = session['vk_account']
            spotify = session['login_sp']
            return render_template('replacing.html')
        except:
            return redirect('/')


@application.route('/transfer')
@log
def transfer():
    account_vk = session['vk_account']
    login_sp = session['login_sp']
    logins = f'{account_vk.login}, {login_sp}'
    tracks = get_tracks(session['token'], session['user_id'])
    session['tracks'] = tracks

    if db.in_db(logins) is False:
        db.create_user(logins)

    payed = db.check_pay(logins)

    if len(tracks) <= config.MAX_TRACKS and payed is False:
        transferred_tracks = db.check_not_transferred(tracks, logins)
        db.fill_tracks(transferred_tracks, logins)
        errors_transfer = search_add(session['spotify'], transferred_tracks)
        return json.dumps({'errors': errors_transfer})

    if len(tracks) > config.MAX_TRACKS and payed is False:
        sorted_tracks = tracks.copy()
        while len(sorted_tracks) != config.MAX_TRACKS:
            sorted_tracks.pop()
        transferred_tracks = db.check_not_transferred(sorted_tracks, logins)
        db.fill_tracks(transferred_tracks, logins)
        errors_transfer = search_add(session['spotify'], transferred_tracks)
        return json.dumps({'errors': errors_transfer})

    if payed:
        transferred_tracks = db.check_not_transferred(tracks, logins)
        db.fill_tracks(transferred_tracks, logins)
        errors_transfer = search_add(session['spotify'], transferred_tracks)
        return json.dumps({'errors': errors_transfer})


@application.route('/pay')
@log
def pay():
    login_vk = session['vk_account'].login
    login_sp = session['login_sp']
    logins = f'{login_vk}, {login_sp}'
    tracks = session['tracks']
    session.pop('vk_account')
    session.pop('login_sp')
    payed = db.check_pay(logins)

    if len(tracks) >= config.MAX_TRACKS and payed is False:
        info = kassa.rest(logins)
        url_to_pay = info.confirmation.confirmation_url
        return json.dumps({'url_to_pay': url_to_pay})
    else:
        return json.dumps({'url_to_pay': None})


@application.route('/check')
@log
def check():
    logins = request.args.get("login")
    id = db.get_id(logins)
    payed = kassa.check(id)
    if payed is True:
        db.user_pay(logins)
    return redirect('/')


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 8080)), host='0.0.0.0')  # .restart-app
