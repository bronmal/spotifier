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
