from enum import Enum


class Browser(Enum):
    Firefox = 1
    Chrome = 2
    Edge = 3


class Account:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.valid = True

