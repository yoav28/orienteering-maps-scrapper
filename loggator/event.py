from bs4 import BeautifulSoup as bs
import requests


class LoggatorEvent:

    def __init__(self, name: str, link: str, map: str, class_id: str, date: str, location: dict[str: float] = None):
        self.class_id = class_id
        self.date = date
        self.link = link
        self.name = name
        self.map = map

        if location:
            self.location = location

        else:
            self.location = self.get_location()


    def __str__(self):
        return self.link.split('/')[-1]


    def get_event_data(self) -> str:
        event = self.link.split('/')[-1]
        content = requests.get(f"https://events.loggator.com/{event}").content.decode()
        return content


    def get_location(self) -> dict[str: float]:
        content = self.get_event_data()
        s = bs(content, 'html.parser')

        lat = s.head.find('meta', {'property': 'place:location:latitude'}).get('content')
        lon = s.head.find('meta', {'property': 'place:location:longitude'}).get('content')

        return {
            "lat": round(float(lat), 10),
            "lon": round(float(lon), 10)
        }
