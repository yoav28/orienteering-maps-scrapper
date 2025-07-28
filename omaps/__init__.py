import time, requests
from concurrent.futures import ThreadPoolExecutor
from utills import *
from db import SQL


class OmapsScrapper:

    def __init__(self, db_path: str, country: str):
        self.db_path = db_path
        self.country = country
        self.db = SQL(self.db_path, initialize=True)


    def scrap_maps(self):
        print("Starting to scrape maps from omaps.net...")
        
        country_code = {
            "Sweden": "se",
            "Norway": "no",
            "Australia": "au",
        }[self.country]
        
        url = f'https://www.omaps.net/{country_code}/Home/LoadMaps'

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
        print("Fetched", len(maps), "maps from omaps.net.")

        with ThreadPoolExecutor(max_workers=300) as executor:
            for i in range(500, len(maps)):
                map_data = maps[i]
                print(i, end=' - ')
                if self.verify_map(map_data):
                    executor.submit(self.scrap_map, map_data)
                    # self.scrap_map(map_data)
                    
        print_green("All valid maps have been processed.")


    def scrap_map(self, map_data):
        map_id = map_data['id']
        name = map_data['name']

        map_url = self.get_map_url(map_id)

        if not map_url:
            return print_red(f"Failed to get map URL for map {map_id}")

        db = SQL(self.db_path, initialize=False)

        if db.map_exists(map_name=map_url):
            return print_red(f"Map {name} already exists in the database.")

        source = {
            "Sweden": "omaps",
            "Norway": "omaps-no",
            "Australia": "omaps-au",
        }[self.country]
        
        db.insert_event(map_name=map_url, date=map_data['createdTime'].split('T')[0], lat=map_data['south'], lon=map_data['west'],
                        class_id=map_id, name=name, source=source, country=self.country)

        return print_green(f"Map '{name}' added to the database.")


    @staticmethod
    def get_map_url(map_id: int) -> str:
        tic = time.perf_counter()
        url = f"https://www.omaps.net/se/Home/MapImage/{map_id}"

        res = requests.get(url)
        if res.status_code != 200:
            raise Exception(f"Failed to fetch map image: {res.status_code} {res.text}")
        
        toc = time.perf_counter()
        print(f"Fetched map image for {map_id} in {toc - tic:.2f} seconds.")

        return res.url


    def verify_map(self, map_data):
        if map_data['newerMapExists']:
            print_red("Newer version of the map exists, skipping...", map_data['id'])
            return False

        if not map_data['hasImage']:
            print_red("Map does not have an image, skipping...", map_data['id'])
            return False

        if map_data['status'] != 'published':
            print_red("Map is not published, skipping...", map_data['id'])
            return False
    

        lon = map_data['west']
        lat = map_data['south']
        map_id = map_data['id']
        name = map_data['name']
        date = map_data['createdTime'].split('T')[0]

        if not all([map_id, name, lat, lon, date]):
            print_red(f"Missing data for map {map_id}: {name}, {lat}, {lon}, {date}")
            return False

        return not self.db.event_exists(name, date)


if __name__ == '__main__':
    scrapper = OmapsScrapper(db_path='../maps.db', country="Australia")
    scrapper.scrap_maps()
