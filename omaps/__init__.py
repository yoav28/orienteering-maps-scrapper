from utills import *
from db import SQL

import requests


class OmapsScrapper:

    def __init__(self, db_path: str):
        self.db = SQL(db_path, initialize=True)


    def get_map_url(self, map_id: int) -> str:
        url = f"https://www.omaps.net/se/Home/MapImage/{map_id}"

        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch map image: {res.status_code} {res.text}")

        return res.url


    def scrap(self):
        url = 'https://www.omaps.net/se/Home/LoadMaps'

        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }

        response = requests.post(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch maps: {response.status_code} {response.text}")

        data = response.json()
        maps = data['maps']

        for map_data in maps[:10]:
            if not self.verify_map(map_data):
                print_red(f"Map {map_data['id']} is not valid or has newer version.")
                continue

            self.scrap_map(map_data)


    def scrap_map(self, map_data):
        lon = map_data['west']
        lat = map_data['south']
        map_id = map_data['id']
        name = map_data['name']
        date = map_data['createdTime'].split('T')[0]

        if not all([map_id, name, lat, lon, date]):
            print_red(f"Missing data for map {map_id}: {name}, {lat}, {lon}, {date}")

        map_url = self.get_map_url(map_id)
        if self.db.event_exists(name=name, date=date):
            return print_red(f"Map {name} already exists in the database.")

        if not map_url:
            return print_red(f"Failed to get map URL for map {map_id}")

        if self.db.map_exists(map_name=map_url):
            return print_red(f"Map {name} already exists in the database.")

        self.db.insert_event(name=name, map_name=map_url, date=date, lat=lat, lon=lon,
                             class_id=map_id, source="omaps", country="Sweden")

        return print_green(f"Map '{name}' added to the database.")


    @staticmethod
    def verify_map(map_data):
        if map_data['status'] != 'published':
            return False

        if map_data['newerMapExists']:
            return False

        if not map_data['hasImage']:
            return False

        return True


if __name__ == '__main__':
    scrapper = OmapsScrapper(db_path='../maps.db')
    scrapper.scrap()
