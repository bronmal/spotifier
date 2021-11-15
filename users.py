from flask_login import LoginManager, UserMixin
import db

login = LoginManager()


class User(UserMixin):
    def __init__(self, user):
        self.user = user

    def email(self):
        return self.user['email']

    def name(self):
        return self.user['name']

    def get_id(self):
        return self.user['user_id']


@login.user_loader
def load_user(id):
    user = User(db.get_user_by_id(int(id)))
    return user
