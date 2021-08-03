from os import PathLike
from utils import Account


def parse_accounts(Path:PathLike = None):
    sp_accounts = []
    vk_accounts = []
    try:
        with open(Path) as file:
            for line in file:
                login = ''
                password = ''
                line.rstrip()
                if line.find('sp:') != -1:
                    index = 0
                    if line.find('login:') != -1:
                        line = line[line.find('login:') + 6:]
                        if line.find('password:') != -1:
                            index = line.find('password:')
                            login = line[:index].replace(' ', '')
                            password = line[index + 9:].rstrip().replace(' ', '')
                            sp_account = Account(login, password)
                            sp_accounts.append(sp_account)
                        else:
                            pass
                    else:
                        pass
                elif line.find('vk:') != -1:
                    index = 0
                    if line.find('login:') != -1:
                        line = line[line.find('login:') + 6:]
                        if line.find('password:') != -1:
                            index = line.find('password:')
                            login = line[:index].replace(' ', '')
                            password = line[index + 9:].rstrip().replace(' ', '')
                            vk_account = Account(login, password)
                            vk_accounts.append(vk_account)
                        else:
                            pass
                    else:
                        pass       
    except:
        print("Wrong PATH!")


    return vk_accounts,sp_accounts
    
    
    

    