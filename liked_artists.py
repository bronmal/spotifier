count = 0


def sp_liked_artists(spot):
    ranges = ['short_term', 'medium_term', 'long_term']
    result = ''
    global count
    while True:
        for sp_range in ['short_term', 'medium_term', 'long_term']:
            print("range:", sp_range)

            result = spot.current_user_top_artists(time_range=sp_range, limit=50)

            for i, item in enumerate(result['items']):
                print(i, item['name'])
        count += 50
        if result['next'] is None:
            break
