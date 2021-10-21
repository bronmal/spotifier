import random
import db_promo


def create_promo(count):
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    code = ''
    for i in range(0, count):
        slice_start = random.randint(0, len(code_chars) - 1)
        code += code_chars[slice_start: slice_start + 1]
    return code


def unique_promo(promo):
    promos = db_promo.get_all_promo()
    for i in promos:
        if i == promo:
            return False
    return True

