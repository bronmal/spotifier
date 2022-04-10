from datetime import datetime, timedelta
import calendar
import json
import config
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select

connect_string = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
    config.DB_LOGIN, config.DB_PASS, 'localhost', 3306, config.DB_DATABASE)

engine = create_engine(connect_string)#convert_unicode=True, echo=True, future=True)

DeclarativeBase = declarative_base()


class User(DeclarativeBase):
    __tablename__ = 'test'

    user_id = sqlalchemy.Column('user_id', sqlalchemy.INTEGER, primary_key=True, autoincrement=True)
    email = sqlalchemy.Column('email', sqlalchemy.TEXT, nullable=False)
    name = sqlalchemy.Column('name', sqlalchemy.TEXT, nullable=False)
    avatar = sqlalchemy.Column('avatar', sqlalchemy.BLOB, nullable=True)
    tracks = sqlalchemy.Column('tracks', sqlalchemy.JSON, nullable=True)
    playlists = sqlalchemy.Column('playlists', sqlalchemy.TEXT, nullable=True,)
    artists = sqlalchemy.Column('artists', sqlalchemy.TEXT, nullable=True)
    albums = sqlalchemy.Column('albums', sqlalchemy.TEXT, nullable=True)
    subscription = sqlalchemy.Column('subscription', sqlalchemy.BOOLEAN, nullable=True)
    free_transfer = sqlalchemy.Column('free_transfer', sqlalchemy.INTEGER, nullable=True)
    yookassa_id = sqlalchemy.Column('yookassa_id', sqlalchemy.TEXT, nullable=True)
    payment_id = sqlalchemy.Column('payment_id', sqlalchemy.TEXT, nullable=True)
    date_end = sqlalchemy.Column('date_end', sqlalchemy.VARCHAR(6), nullable=False)
    connected_services = sqlalchemy.Column('connected_services', sqlalchemy.TEXT)
    refresh_tokens = sqlalchemy.Column('refresh_tokens', sqlalchemy.JSON, nullable=True)


DeclarativeBase.metadata.create_all(engine)


def create_session():
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def create_user(email, name, photo=None):
    session = create_session()
    date = datetime.now()
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    date = str(date.day) + '.' + str(date.month)

    user = User(
        email=email,
        name=name,
        avatar=photo,
        date_end=date,
        subscription=False,
        free_transfer=10
    )
    session.add(user)
    session.commit()


def get_user_by_id(id):
    session = create_session()
    s = select(User).where(User.user_id == id)
    try:
        return session.execute(s).one().User
    except:
        return None


def get_user_by_email(email):
    session = create_session()
    for i in session.query(User):
        if i.email == email:
            return i


def get_connected_services(id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == id:
            return json.loads(i.connected_services)


def in_db(email):
    session = create_session()
    for i in session.query(User):
        if i.email == email:
            session.close()
            return email
    return None


def add_service(user_id, token, service):
    session = create_session()
    connected_services = None

    for i in session.query(User):
        if i.user_id == user_id:
            if i.connected_services is not None:
                connected_services = json.loads(i.connected_services)

            if connected_services is None:
                i.connected_services = json.dumps({service: token})
            if connected_services is not None:
                connected_services.update({service: token})
                i.connected_services = json.dumps(connected_services)

            session.commit()
            session.close()
            break


def save_refresh_token(user_id, refresh_token):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            i.refresh_tokens = refresh_token
            session.commit()
            session.close()
            break


def remove_service(id, service):
    session = create_session()
    for i in session.query(User):
        if i.user_id == id:
            connected_services = json.loads(i.connected_services)
            del connected_services[service]
            i.connected_services = json.dumps(connected_services)
            session.commit()
            session.close()
            break


def get_token(user_id, service):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            try:
                tokens = json.loads(i.connected_services)
                session.close()
                return tokens[service]
            except:
                session.close()
                return None


def save_music(user_id, tracks=None, albums=None, playlists=None, artists=None):
    session = create_session()
    tr = tracks.copy()
    db_tracks = [tr, 'tracks']
    db_albums = [albums, 'albums']
    db_playlists = [playlists, 'playlists']
    db_artists = [artists, 'artists']
    music = [db_tracks] #db_artists, db_playlists, db_albums]
    for i in session.query(User):
        if i.user_id == user_id:
            if tracks:
                if i.tracks is not None:
                    for b in json.loads(i.tracks):
                        music[0][0].append(b)
                for b in music:
                    try:
                        i.tracks = json.dumps(b[0])
                        session.commit()
                        break
                    except Exception as err:
                        print(err)
                        break
    session.close()


def get_user_info_dashboard(user_id, only_photo=False):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            if not only_photo:
                session.close()
                return i.name, i.date_end, i.subscription, i.connected_services, i.avatar
            if only_photo:
                session.close()
                return i.avatar


def user_payed(user_id, payment_id):
    session = create_session()
    date = datetime.now()
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    date = str(date.day) + '.' + str(date.month)

    for i in session.query(User):
        if i.user_id == user_id:
            i.date_end = date
            i.subscription = True
            i.payment_id = payment_id
            session.commit()
            session.close()
            break


def delete_sub(user_id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            i.subscription = False
            i.payment_id = None
            session.commit()
            session.close()
            break


def check_sub(user_id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            if i.subscription == 0:
                session.close()
                return False
            if i.subscription == 1:
                session.close()
                return True


def check_free_transfer(user_id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            session.close()
            return i.free_transfer


def use_free_transfer(user_id, count):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            i.free_transfer = count
            session.commit()
            session.close()
            break


def save_yookassa_id(user_id, id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            i.yookassa_id = id
            session.commit()
            session.close()
            break


def get_yookassa_id(user_id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            session.close()
            return i.yookassa_id


def get_info_all_users():
    session = create_session()
    users = []
    for i in session.query(User):
        users.append({'user_id': i.user_id, 'payment_id': i.payment_id, 'date_end': i.date_end})
    session.close()
    return users


def get_audio(audio, types, user_id):
    session = create_session()
    tracks_db = None
    find_tracks = []
    for i in session.query(User):
        if i.user_id == user_id:
            types_ = {'tracks': i.tracks, 'albums': i.albums, 'playlists': i.playlists, 'artists': i.artists}
            tracks_db = json.loads(types_[types])

    for i in tracks_db:
        for b in audio:
            if i['id'] == int(b['id']):
                if i['service'] == b['service']:
                    if types == 'tracks':
                        find_tracks.append(i['title'] + ' ' + i['artist'])
                    if types == 'albums':
                        find_tracks.append(i['title'])
                    if types == 'artists':
                        find_tracks.append(i['title'])
    session.close()
    return find_tracks


def delete_cache(user_id):
    session = create_session()
    for i in session.query(User):
        if i.user_id == user_id:
            i.tracks = None
            session.commit()
            session.close()
            break