count = 0


def sp_liked_artists(spot):
    result = ''
    global count
    while True:
        result = spot.current_user_playlists(limit=50, offset=count)
        for i, item in enumerate(result['items']):
            print("%d %s" % (i, item['name']))
        count += 50
        print(count)
        if result['next'] is None:
            break