import uuid
from flask import Blueprint, request, session, render_template, redirect

yandex_music = Blueprint('yandex-music', __name__, template_folder='templates', static_folder='static')


@yandex_music.route('/')
def main():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    return render_template('yandex/index.html')


@yandex_music.route('/auth', methods=['GET', 'POST'])
def yandex():
    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    if request.method == 'GET':
        return render_template('yandex/yandex_form.html')
