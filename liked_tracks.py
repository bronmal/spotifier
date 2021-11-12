count = 0


def sp_liked_tracks(spot):
    result = ''

    while True:
        result = spot.current_user_saved_tracks(limit=50, offset=count)
        for item in result['items']:
            track = item['track']
            print("%32.32s %s" % (track['artists'][0]['name'], track['name']))
        count += 50
        print(count)
        if result['next'] is None:
            break
