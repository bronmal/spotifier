import pymysql
import json
from datetime import datetime, timedelta
import calendar
import sshtunnel


def create_con():
        con = pymysql.connect(user='mysql', host='127.0.0.1',
                              password='', database='spotifier')
        return con


def get_user_by_id(id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['user_id'] == id:
            return i


def get_user_by_email(email):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['email'] == email:
            return i


def create_user(email, name):
    date = datetime.now()
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("INSERT INTO users (email, name, subscription, date_end) VALUES (%s, %s, %s, %s)",
                   (email, name, False, date))
    cursor.close()
    con.commit()
    con.close()


def in_db(email):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['email'] == email:
            return email
    return None


def add_service(user_id, token):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    connected_services = None
    for i in rows:
        if i['user_id'] == user_id:
            if i['connected_services'] is not None:
                connected_services = json.loads(i['connected_services'])
            if i['connected_services'] is None:
                connected_services = None

    query = """ UPDATE users
                        SET connected_services = %s
                        WHERE user_id = %s """
    data = ()
    if connected_services is None:
        data = (json.dumps({'vk': token}), user_id)
    if connected_services is not None:
        data = (json.dumps({'tracks': token}), user_id)

    cursor.execute(query, data)
    cursor.close()
    con.commit()
    con.close()


def get_token(user_id, service):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['user_id'] == user_id:
            tokens = json.loads(i['connected_services'])
            return tokens[service]


def save_music(user_id, tracks=None, albums=None, playlists=None, artists=None):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    db_tracks = None
    db_albums = None
    db_playlists = None
    db_artists = None
    for i in rows:
        if i['user_id'] == user_id:
            if tracks:
                if i['tracks'] is not None:
                    db_tracks = json.loads(i['tracks'])
                if i['tracks'] is None:
                    pass

            if albums:
                if i['albums'] is not None:
                    db_albums = json.loads(i['albums'])
                if i['albums'] is None:
                    pass

            if playlists:
                if i['playlists'] is not None:
                    db_playlists = json.loads(i['playlists'])
                if i['playlists'] is None:
                    pass

            if artists:
                if i['artists'] is not None:
                    db_artists = json.loads(i['artists'])
                if i['artists'] is None:
                    pass

    query = """ UPDATE users
                        SET connected_services = %s
                        WHERE user_id = %s """
    data = ()
    if connected_services is None:
        data = (json.dumps({'vk': token}), user_id)
    if connected_services is not None:
        data = (json.dumps({'tracks': token}), user_id)

    cursor.execute(query, data)
    cursor.close()
    con.commit()
    con.close()
