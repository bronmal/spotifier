from functools import wraps
from time import time
from datetime import datetime
from mt_tester.utils import Account
import vk_api
import json
PATH = "spotifier.log"



def log(func):

    @wraps(func)
    def inner(*args, **kwargs):
        today = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
        print_str = ""
        for i in args:
            if isinstance(i, Account):
                user = vk_api.VkApi(i.login, i.password)
                json_dict = ""
                id = ""
                try:
                    user.auth()
                    with open("vk_config.v2.json") as file:
                        json_dict = file.read()
                    json_dict = json.loads(json_dict)
                except:
                    pass  
                if not (type(json_dict) == str):
                    id = json_dict[i.login]['cookies'][1]['value']
                print_str += i.login + f"  VK ID: {id}"
            else:
                print_str += str(i)
        with open(PATH, 'a') as file:
            file.write(f"[{today}] : {func.__name__} function executed with args ({print_str}) \n")

        result = func(*args, **kwargs)
        return result
    
    return inner