import os
import uuid
import config
import spotipy
from flask import Flask, session, request, redirect, render_template, json, flash
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
    return redirect('/result')


@application.route('/result')
def waiting_page():
    return render_template('replacing.html')


@application.route('/transfer')
def transfer():
    login = session['login_vk']
    password = session['password_vk']
    tracks = get_tracks(login, password)
    errors_transfer = search_add(session['spotify'], tracks)
    return json.dumps({'errors': errors_transfer})


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 8080)), host='0.0.0.0')
