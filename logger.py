from functools import wraps
from time import time
from datetime import datetime
from mt_tester.utils import Account
PATH = "spotifier.log"



def log(func):

    @wraps(func)
    def inner(*args, **kwargs):
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        print_str = ""
        for i in args:
            if isinstance(i, Account):
                print_str += i.login
            else:
                print_str += i
        with open(PATH, 'a') as file:
            file.write(f"[{today}] : {func.__name__} function executed with args ({print_str}) \n")

        result = func(*args, **kwargs)
        return result
    
    return inner