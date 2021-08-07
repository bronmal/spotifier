from functools import wraps
from time import time
from datetime import datetime
PATH = "spotifier.log"



def log(func):

    @wraps(func)
    def inner(*args, **kwargs):
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        with open(PATH, 'a') as file:
            file.write(f"[{today}] : {func.__name__} function executed with args {args, kwargs} \n")

        result = func(*args, **kwargs)
        return result
    
    return inner