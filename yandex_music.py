from flask import Blueprint

yandex = Blueprint('yandex-music', __name__, template_folder='templates', static_folder='static')


@yandex.route('/')
def main():
    return 'test'
