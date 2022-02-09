import pymysql
import json
from datetime import datetime, timedelta
import calendar
import config


def create_con():
        con = pymysql.connect(user=config.DB_LOGIN, host='127.0.0.1',
                              password=config.DB_PASS, database=config.DB_DATABASE)
        return con


def get_user_by_id(id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['user_id'] == id:
            return i


def get_user_by_email(email):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
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
    cursor.execute("INSERT INTO spotifier (email, name, avatar, subscription, date_end) VALUES (%s, %s, %s, %s, %s)",
                   (email, name, photo, False, date))
    cursor.close()
    con.commit()
    con.close()


def in_db(email):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['email'] == email:
            return email
    return None


def add_service(user_id, token, service):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    connected_services = None

    for i in rows:
        if i['user_id'] == user_id:
            if i['connected_services'] is not None:
                connected_services = json.loads(i['connected_services'])

    query = """ UPDATE spotifier
                        SET connected_services = %s
                        WHERE user_id = %s """
    data = ()
    if connected_services is None:
        data = (json.dumps({service: token}), user_id)
    if connected_services is not None:
        connected_services.update({service: token})
        data = (json.dumps(connected_services), user_id)

    cursor.execute(query, data)
    cursor.close()
    con.commit()
    con.close()


def get_token(user_id, service):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM spotifier")
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

    cursor.execute("SELECT * FROM spotifier")
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
        query = f""" UPDATE spotifier
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
    cursor.execute("SELECT * FROM spotifier")
    rows = cursor.fetchall()
    cursor.close()
    con.close()

    for i in rows:
        if i['user_id'] == user_id:
            if not only_photo:
                return i['name'], i['date_end'], i['subscription'], i['connected_services'], i['avatar']
            if only_photo:
                return i['avatar']


def user_payed(user_id, payment_id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    date = datetime.now()
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    date = str(date.day) + '.' + str(date.month)

    query = """ UPDATE spotifier
                          SET date_end = %s
                          WHERE user_id = %s """

    cursor.execute(query, (date, user_id))

    query = """ UPDATE spotifier
                        SET subscription = %s
                        WHERE user_id = %s """

    cursor.execute(query, (True, user_id))

    query = """ UPDATE spotifier
                        SET payment_id = %s
                        WHERE user_id = %s """

    cursor.execute(query, (payment_id, user_id))

    cursor.close()
    con.commit()
    con.close()


def delete_sub(user_id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    query = """ UPDATE spotifier
                        SET subscription = %s
                        WHERE user_id = %s """

    cursor.execute(query, (False, user_id))


    query = """ UPDATE spotifier
                        SET payment_id = %s
                        WHERE user_id = %s """

    cursor.execute(query, (None, user_id))

    cursor.close()
    con.commit()
    con.close()


def save_yookassa_id(user_id, id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    query = """ UPDATE spotifier
                            SET yookassa_id = %s
                            WHERE user_id = %s """

    cursor.execute(query, (id, user_id))

    cursor.close()
    con.commit()
    con.close()


def get_yookassa_id(user_id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    query = """ SELECT yookassa_id FROM spotifier WHERE user_id = %s """

    cursor.execute(query, (user_id,))

    cursor.close()
    con.close()

    return cursor.fetchone()


def get_info_all_users():
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    query = """SELECT user_id, payment_id, date_end FROM spotifier """

    cursor.execute(query)
    return cursor.fetchall()


def get_audio(audio, types, user_id):
    con = create_con()
    cursor = con.cursor(pymysql.cursors.DictCursor)

    query = """ SELECT * FROM spotifier"""

    cursor.execute(query)

    info = cursor.fetchall()
    tracks_db = None
    find_tracks = []
    for i in info:
        if i['user_id'] == user_id:
            tracks_db = json.loads(i[types])

    for i in tracks_db:
        for b in audio:
            if i['id'] == b['id'] and i['service'] == b['service']:
                find_tracks.append(i['title'] + ' ' + i['artist'])
    return find_tracks

