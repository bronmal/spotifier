import pymysql
import json

con = pymysql.connect(user='u1420413_default', host='31.31.198.4',
                      password='8jPn8m4hUX27uPYY', database='u1420413_pay')


def in_db(logins):
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    if rows == ():
        return False
    for i in rows:
        if i['login'] == logins:
            return True
        if i['login'] != logins:
            return False


def create_user(logins):
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("INSERT INTO spotifier (login, payed, transfered) VALUES (%s, %s, %s)", (logins, False, None))
    cursor.close()
    con.commit()


def fill_tracks(tracks, logins):
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


def check_not_transferred(tracks, logins):
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

    if db_tracks is None:
        return tracks
    if db_tracks is not None:
        sort_tracks = tracks.copy()
        for i in tracks:
            if i in db_tracks:
                sort_tracks.remove(i)
        return sort_tracks


def fill_id(logins, id):
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


def get_id(logins):
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    for i in rows:
        if i['login'] == logins:
            return i['pay_id']
