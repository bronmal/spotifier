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
    db_tracks = str()
    for i in rows:
        if i['login'] == logins:
            db_tracks = i['transfered']


    query = """ UPDATE spotifier
                    SET transfered = %s
                    WHERE login = %s """
    data = (json.dumps({'tracks': tracks}), logins)

    cursor.execute(query, data)
    cursor.close()
    con.commit()
