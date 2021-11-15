import os
import uuid
import config
import auth
from flask import Flask, session, request, redirect, render_template, json, send_from_directory
from flask_session import Session

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


@application.route('/')
def main_page():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return render_template('index.html')


@application.route('/auth')
def authorization():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    vkont = auth.VkAuth()
    spot = auth.SpotAuth()
    gle = auth.GoogleAuth()

    url_google = gle.create_link()
    session['google_state'] = url_google[1]

    urls = dict
    urls.update({'vk': vkont.create_link()})
    urls.update({'spotify': spot.create_link()})
    urls.update({'google': url_google[0]})

    return render_template('auth.html', url=url_google[0])


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
            print(email, name)
            # сохранить в бд имя и email
            return email
        except:
            return redirect('/auth')


@application.route('/auth_spotify')
def spotify():
    if request.args.get('code'):
        try:
            spot = auth.SpotAuth()
            name, email = spot.name(request.args.get('code'))
            return name
        except:
            return redirect('/auth')


@application.route('/auth_google')
def google():
    try:
        gle = auth.GoogleAuth()
        name, email = gle.name(session['google_state'], request.url)
        return email
    except Exception as err:
        print(err)
        return redirect('/auth')


@application.route('/.well-known')
def apple_pay():
    return send_from_directory('static', 'apple-developer-merchantid-domain-association')


@application.route('/receiver.html')
def mailru_():
    return render_template('_receiver.html')


if __name__ == '__main__':
    application.run(threaded=True, debug=True, port=int(os.environ.get("PORT", 8080)), host='0.0.0.0')
