import pymysql
import json
from datetime import datetime, timedelta
import calendar


def create_con():
        con = pymysql.connect(user='bronmal', host='127.0.0.1',
                              password='1q2w3e4r5', database='spotifier')
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


def create_user(email, name, photo):
    date = datetime.now()
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    date = str(date.day) + '.' + str(date.month)
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("INSERT INTO users (email, name, avatar, subscription, date_end) VALUES (%s, %s, %s, %s, %s)",
                   (email, name, photo, False, date))
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
            try:
                tokens = json.loads(i['connected_services'])
                return tokens[service]
            except:
                return None


def save_music(user_id, tracks=None, albums=None, playlists=None, artists=None):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    db_tracks = [tracks, 'tracks']
    db_albums = [albums, 'albums']
    db_playlists = [playlists, 'playlists']
    db_artists = [artists, 'artists']
    music = [db_artists, db_playlists, db_albums, db_tracks]
    for i in rows:
        if i['user_id'] == user_id:
            if tracks:
                if i['tracks'] is not None:
                    music[3].append(json.loads(i['tracks']))
                if i['tracks'] is None:
                    music[3].append([None])

            if albums:
                if i['albums'] is not None:
                    music[2].append(json.loads(i['tracks']))
                if i['albums'] is None:
                    music[2].append([None])

            if playlists:
                if i['playlists'] is not None:
                    music[1].append(json.loads(i['tracks']))
                if i['playlists'] is None:
                    music[1].append([None])

            if artists:
                if i['artists'] is not None:
                    music[0].append(json.loads(i['tracks']))
                if i['artists'] is None:
                    music[0].append([None])
            break

    for i in music:
        query = f""" UPDATE users
                                SET {i[1]} = %s
                                WHERE user_id = %s """
        try:
            data = (json.dumps(i[0]), user_id)
            cursor.execute(query, data)
        except Exception as err:
            print(err)

    cursor.close()
    con.commit()
    con.close()


def get_user_info_dashboard(user_id, only_photo=False):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['user_id'] == user_id:
            if not only_photo:
                return i['name'], i['date_end'], i['subscription'], i['connected_services'], i['avatar']
            if only_photo:
                return i['avatar']
