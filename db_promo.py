import pymysql
from db import ssh


@ssh
def create_con():
    con = pymysql.connect(user='bronmal', host='bronmal.mysql.eu.pythonanywhere-services.com',
                          password='andrey5550100', database='bronmal$pay')
    return con


def save_promo(login, promo):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    query = """INSERT INTO promo(vk, promo, use_count) 
            VALUES (%s, %s, %s)"""
    data = (login, promo)
    cursor.execute(query, data)
    cursor.close()
    con.commit()
    con.close()


def check_availability(login):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT vk, promo FROM promo;")
    vk = cursor.fetchall()
    for i in vk:
        if login == i['vk']:
            cursor.close()
            con.close()
            return i['promo']
    cursor.close()
    con.close()
    return None


def get_all_promo():
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT promo FROM promo;")
    promos = cursor.fetchall()
    cursor.close()
    con.close()
    return promos
