import base64


def search_add(spot, q):
    user_id = spot.me()['id']
    try:
        if 'Vk music by Spotifier' not in spot.user_playlists(user_id)['items'][0]['name']:
            spot.user_playlist_create(user_id, name='Vk music by Spotifier', description='Этот плейлист был создан '
                                                                                         'сайтом '
                                                                                         'spotifier.ru; Перенос музыки '
                                                                                         'из Vk в Spotify в один клик')
    except:
        spot.user_playlist_create(user_id, name='Vk music by Spotifier', description='Этот плейлист был создан сайтом '
                                                                                     'spotifier.ru; Перенос музыки '
                                                                                     'из Vk в Spotify в один клик')

    errors_transfer = []
    id_playlist = None
    playlists = spot.user_playlists(user_id)['items']
    for i in playlists:
        if i['name'] == 'Vk music by Spotifier':
            id_playlist = i['id']

    with open('created by spotifier.jpg', 'rb') as image_file:
        image = base64.b64encode(image_file.read())
    spot.playlist_upload_cover_image(id_playlist, image)

    items = []
    for i in q:
        result = spot.search(i, type='track', limit=1)
        try:
            items.append(result['tracks']['items'][0]['id'])
        except:
            errors_transfer.append(i)

    for b in range(0, len(items), 100):
        chunk = items[b:b+100]
        spot.playlist_add_items(id_playlist, chunk)

    return errors_transfer
