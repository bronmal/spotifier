from flask_login import LoginManager, UserMixin

login = LoginManager()


class User(UserMixin):
    def __init__(self, user):
        self.user = user

    def email(self):
        return self.user.email

    def name(self):
        return self.user.name

    def get_id(self):
        return self.user.user_id

    def is_authenticated(self):
        try:
            self.get_id()
            return True
        except:
            return False

    @classmethod
    def get(cls, id):
        try:
            return cls(id)
        except UserWarning:
            return None
