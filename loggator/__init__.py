import requests, re, json
from event import LoggatorEvent
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup as bs
from cache import Cache
from utills import *
from db import SQL


cache = Cache()


class LoggatorScrapper:

    def __init__(self, db_path: str):
        self.db = SQL(db_path, initialize=True)
        self.num_of_pages = self.get_number_of_pages()


    def get_number_of_pages(self) -> int:
        soup = bs(self.get_page(1), 'html.parser')
        last_button = soup.body.header.find(id="content").div.ul.find_all('li')[-1].a
        return int(last_button.get('href').split('=')[-1])


    def scrap_events(self, start_page: int = 1):
        events = []

        for i in range(start_page, self.num_of_pages + 1):
            events.extend(self.get_events_in_page(i))
            cache.save()


    def get_page(self, n: int) -> str:
        if page_content := cache.get(f"page-{n}"):
            return page_content

        content = requests.get(f"https://loggator.com/recent_events?page={n}").content.decode()
        cache.set(f"page-{n}", content)

        return content


    def parse_event(self, tr) -> LoggatorEvent or None:
        links = re.findall(r'https?://[^\s"<>]+', str(tr))

        spam = ["https://d1die33kgxnq4e.cloudfront.net/assets/icons/sports/orienteering-c595df440c69407679ba34ccdbcb5eed.png"]
        links = [x for x in links if x not in spam]

        if not (loggator_link := links.pop(0)) or not links:
            return None

        date = tr.find('time').get('datetime')
        display_date = date.split('T')[0]
        
        name = tr.find('a', href=re.compile(r'events\.loggator\.com')).text.strip()
        
        
        try:
            class_id = loggator_link.split('/')[-1]
            event = LoggatorEvent(link=loggator_link, map=links[0], class_id=class_id, date=display_date, name=name)

            if self.db.event_or_map_exists(name=event.name, date=event.date, map_name=event.map):
                return None

            lat, lon = event.location['lat'], event.location['lon']
            
            self.db.insert_event(name=event.name, map_name=event.map, date=event.date, lat=event.location["lat"], lon=event.location["lon"],
                                 class_id=event.class_id, source="loggator", country=self.get_country(lat=lat, lon=lon))

            print_green(f"Event '{event.name}' added to the database.")

        except Exception as e:
            return print_red(f"Error getting event data: {e}")


    @staticmethod
    def get_country(lat: float, lon: float) -> str:
        lon = round(lon, 2)
        lat = round(lat, 2)

        if country := cache.get(f"country-{lon}-{lat}"):
            return country

        geolocator = Nominatim(user_agent="loggator_scrapper")
        location = geolocator.reverse(f"{lat},{lon}", language="en", exactly_one=True)
        
        if not location or not location.raw.get('address'):
            return "Unknown"
        
        country = location.raw['address'].get('country', 'Unknown')
        cache.set(f"country-{lon}-{lat}", country)
        return country


    def get_events_in_page(self, page_number: int) -> list[LoggatorEvent]:
        print(f"Getting events from page {page_number}")

        soup = bs(self.get_page(page_number), 'html.parser')
        tbody = soup.body.header.find(id="content").table.tbody

        events = []

        for tr in tbody.find_all('tr'):
            if event := self.parse_event(tr):
                events.append(event)

        return [event for event in events if not self.db.event_or_map_exists(event.link, event.date)]





if __name__ == '__main__':
    scrapper = LoggatorScrapper(db_path='../maps.db')
    scrapper.scrap_events(100)
