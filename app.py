import os
import time
import uuid
import config
import spotipy
import db
import kassa
from flask import Flask, session, request, redirect, render_template, json, flash, url_for
from flask_session import Session
from get_tracks import get_tracks, valid
from add_spotify import search_add

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


def database_work(logins, tracks):
    if db.in_db(logins) is False:
        db.create_user(logins)
        db.fill_tracks(tracks, logins)
    elif db.in_db(logins) is True:
        db.fill_tracks(tracks, logins)


@application.route('/')
def main_page():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return render_template('index.html')


@application.route('/auth_vk', methods=['get', 'post'])
def vk():
    if not session.get('uuid'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('vk_form.html')

    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        is_valid = valid(login, password)
        if is_valid is True:
            session['login_vk'] = login
            session['password_vk'] = password
            return redirect('/auth_spotify')
        if is_valid is False:
            flash('Пароль не верный, попробуйте еще раз', 'error')
            return redirect('/auth_vk')


@application.route('/auth_spotify')
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
    session['login_sp'] = spot.me()
    return redirect('/result')


@application.route('/result')
def waiting_page():
    return render_template('replacing.html')


@application.route('/transfer')
def transfer():
    login_vk = session['login_vk']
    password_vk = session['password_vk']
    login_sp = session['login_sp']['external_urls']['spotify']
    logins = f'{login_vk}, {login_sp}'
    tracks = get_tracks(login_vk, password_vk)
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
def pay():
    login_vk = session['login_vk']
    login_sp = session['login_sp']['external_urls']['spotify']
    logins = f'{login_vk}, {login_sp}'
    tracks = session['tracks']
    payed = db.check_pay(logins)

    if len(tracks) > config.MAX_TRACKS and payed is False:
        info = kassa.rest(logins)
        url_to_pay = info.confirmation.confirmation_url
        return json.dumps({'url_to_pay': url_to_pay})
    else:
        return json.dumps({'url_to_pay': None})


@application.route('/check')
def check():
    logins = request.args.get("login")
    id = db.get_id(logins)
    payed = kassa.check(id)
    if payed is True:
        db.user_pay(logins)
    return redirect('/')


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 8080)), host='0.0.0.0')  # .restart-app
