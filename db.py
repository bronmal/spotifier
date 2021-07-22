import pymysql

con = pymysql.connect(user='u1420413_default', host='31.31.198.4',
                      password='8jPn8m4hUX27uPYY', database='u1420413_pay')


def create_user(login):
    with con.cursor() as cursor:
        pay = [login, False, None]
        query = 'INSERT INTO pay (pay) VALUES (%s)'
        cursor.executemany(query, pay)
        con.commit()
        with con.cursor() as cursor:
            query = 'SELECT pay FROM pay'
            cursor.execute(query)
            for row in cursor:
                print(row[0])
