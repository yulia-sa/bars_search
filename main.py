import json
import folium
from yandex_geocoder import Client
from geopy import distance
from flask import Flask

BARS_COUNT = 5
BARS_FILE = 'bars.json'


def get_user_coordinates():
    """ Получаем координаты пользователя от геокодера Yandex.

    Меняем местами координаты, полученные от Yandex (долгота, широта), на (широта, долгота), 
    т.к. GeoPy принимает координаты в формате (широта, долгота).
    """
    user_location = input("Где вы находитесь?: ")
    user_coordinates = Client.coordinates(user_location)
    user_coordinates_swapped = user_coordinates[::-1]

    return user_coordinates_swapped


def load_bars_info_from_file(BARS_FILE):
    with open(BARS_FILE, "r", encoding="CP1251") as bars_file:
        bars = json.load(bars_file)

    return bars


def get_all_bars_distance(user_coordinates, bars):

    bars_with_distance_from_user = []

    for bar in bars:
        distance_from_user = distance.distance(user_coordinates,
                                               (bar['geoData']['coordinates'][1],
                                                bar['geoData']['coordinates'][0])).km

        bar_with_distance = {
            'title': bar['Name'],
            'longitude': bar['geoData']['coordinates'][0],
            'latitude': bar['geoData']['coordinates'][1],
            'distance': distance_from_user
        }

        bars_with_distance_from_user.append(bar_with_distance)

    return bars_with_distance_from_user


def get_bar_distance(bar):
    return bar['distance']


def get_nearest_bars(bars_with_distance):
    nearest_bars = sorted(bars_with_distance, key=get_bar_distance)[:BARS_COUNT]
    return nearest_bars


def create_map(user_coordinates, nearest_bars):
    folium_map = folium.Map(
        location=[user_coordinates[0], user_coordinates[1]],
        zoom_start=16,
        tiles='Stamen Terrain'
    )

    user_tooltip = 'Вы здесь'
    folium.CircleMarker(
        [user_coordinates[0], user_coordinates[1]],
        tooltip=user_tooltip,
        color='#cc3333',
        fill=True,
        fill_color='#cc3333'
    ).add_to(folium_map)

    for bar in nearest_bars:
        bar_distance = round(bar['distance'] * 1000)
        bar_name = bar['title']
        tooltip = bar['title']
        folium.Marker(
            [bar['latitude'], bar['longitude']],
            popup='<i>{} {} {}</i>'.format(bar_name, bar_distance, 'м'),
            tooltip=tooltip
        ).add_to(folium_map)

    folium_map.save('index.html')


def read_map():
    with open('index.html') as file:
        return file.read()


def main():
    user_coordinates = get_user_coordinates()
    bars = load_bars_info_from_file(BARS_FILE)
    bars_with_distance = get_all_bars_distance(user_coordinates, bars)
    nearest_bars = get_nearest_bars(bars_with_distance)
    create_map(user_coordinates, nearest_bars)


if __name__ == '__main__':
    main()
    app = Flask(__name__)
    app.add_url_rule('/', 'Map', read_map)
    app.run('0.0.0.0')
