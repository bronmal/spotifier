import pymysql
import json
from logger import log

@log
def create_con():
    con = pymysql.connect(user='bronmal', host='bronmal.mysql.eu.pythonanywhere-services.com',
                          password='andrey5550100', database='bronmal$pay')
    return con

@log
def in_db(logins):
    con = create_con()
    global find
    find = False
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()
    if rows == ():
        return False
    for i in rows:
        if i['login'] == logins:
            find = True
            return True
    if find is False:
        return False

@log
def create_user(logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("INSERT INTO spotifier (login, payed, transfered) VALUES (%s, %s, %s)", (logins, False, None))
    cursor.close()
    con.commit()
    con.close()

@log
def fill_tracks(tracks, logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    db_tracks = None
    for i in rows:
        if i['login'] == logins:
            if i['transfered'] is not None:
                db_tracks = json.loads(i['transfered'])['tracks']
            if i['transfered'] is None:
                db_tracks = None



    query = """ UPDATE spotifier
                    SET transfered = %s
                    WHERE login = %s """
    data = ()
    if db_tracks is None:
        data = (json.dumps({'tracks': tracks}), logins)
    if db_tracks is not None:
        sort_tracks = tracks.copy()
        for i in tracks:
            if i in db_tracks:
                sort_tracks.remove(i)
        data = (json.dumps({'tracks': db_tracks + sort_tracks}), logins)

    cursor.execute(query, data)
    cursor.close()
    con.commit()
    con.close()

@log
def check_not_transferred(tracks, logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    db_tracks = None
    for i in rows:
        if i['login'] == logins:
            if i['transfered'] is not None:
                db_tracks = json.loads(i['transfered'])['tracks']
            if i['transfered'] is None:
                db_tracks = None

    cursor.close()
    con.commit()
    con.close()

    if db_tracks is None:
        return tracks
    if db_tracks is not None:
        sort_tracks = tracks.copy()
        for i in tracks:
            if i in db_tracks:
                sort_tracks.remove(i)
        return sort_tracks

@log
def fill_id(logins, id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    for i in rows:
        if i['login'] == logins:
            query = """ UPDATE spotifier
                                SET pay_id = %s
                                WHERE login = %s """
            data = (id, logins)
            cursor.execute(query, data)
            cursor.close()
            con.commit()
            con.close()

@log
def get_id(logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()
    for i in rows:
        if i['login'] == logins:
            return i['pay_id']

@log
def user_pay(logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    for i in rows:
        if i['login'] == logins:
            query = """ UPDATE spotifier
                                SET payed = %s
                                WHERE login = %s """
            data = (True, logins)
            cursor.execute(query, data)
            cursor.close()
            con.commit()
            con.close()
        else:
            cursor.close()
            con.commit()
            con.close()

@log
def check_pay(logins):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['login'] == logins:
            if i['payed'] == 1:
                return True
            if i['payed'] == 0:
                return False
