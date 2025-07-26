import time, sqlite3, requests, threading, os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from event import Event
from utills import *



class LiveloxScrapper:
    def __init__(self, country: str | None = None, max_events: int = 1000, db_path: str = "maps.db"):
        self.counter = 0
        self.country = country
        self.db_path = db_path
        self.max_events = max_events
        self.lock = threading.Lock()
        
        self.cookies = {
            'culture': 'en-US',
            '__stripe_mid': os.getenv('LIVELOX_COOKIE_STRIPE_MID'),
            'userContextToken': os.getenv('LIVELOX_COOKIE_USER_CONTEXT_TOKEN'),
            '.AspNetCore.Session': os.getenv('LIVELOX_COOKIE_ASPNETCORE_SESSION'),
        }
        
        self.conn, self.cursor = self.initialize_db()


    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                name TEXT,
                class_id INTEGER,
                map TEXT,
                lat REAL,
                lon REAL,
                date TEXT,
                country TEXT
            )
        ''')
        conn.commit()
        
        return conn, cursor


    def scrap_events(self, start_date: datetime = None, days_delta: int = 10):
        if start_date is None:
            start_date = datetime.now()

        end_date = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        current_date = start_date


        with ThreadPoolExecutor(max_workers=100) as executor:
            
            # 2014-08-01 is the oldest day
            while self.counter < self.max_events and end_date >= start_date:
                to_date = current_date.strftime("%Y-%m-%d")
                from_date = (current_date - timedelta(days=days_delta)).strftime("%Y-%m-%d")

                try:
                    print(f"Searching events in {self.country} ({from_date}, {to_date})")
                    
                    res = requests.post(
                        url="https://www.livelox.com/Home/SearchEvents",
                        headers={
                            'accept': 'application/json, text/javascript',
                            'content-type': 'application/json',
                            'x-requested-with': 'XMLHttpRequest'
                        },
                        json={
                            "countryId": country_code(self.country),
                            "timePeriod": "customTimePeriod",
                            "from": from_date,
                            "to": to_date,
                            "orderBy": "participantCount",
                            "maxNumberOfResults": 100_000
                        },
                        timeout=10
                    )
                    res.raise_for_status()
                    events = res.json()

                except requests.exceptions.RequestException as e:
                    print_red(f"Error fetching events: {e}")
                    time.sleep(10)
                
                    current_date -= timedelta(days=days_delta)
                    continue

                if not events:
                    print_red("No events found in this period.")
                    current_date -= timedelta(days=days_delta)
                    continue

                for e in events:
                    if self.counter >= self.max_events:
                        break
                        
                    if self.verify_event(e):
                        executor.submit(self.scrap_event, e)
                
                if self.counter >= self.max_events:
                    print_red("Max events reached, stopping scrapper.")
                    break

                current_date -= timedelta(days=days_delta)
                time.sleep(1)


        print_green("Scrapping finished.")

    
    
    def verify_event(self, e) -> bool:
        if any(p.get('key') == 'HasPassword' and str(p.get('value')) == 'True' for p in e.get('properties', [])):
            return False

        name = e.get('name')
        
        if not name:
            return False

        if not e.get('classes') or not e.get('location'):
            print_red(f"Skipping event '{name}' due to missing data. {e.get('classes')}, {e.get('location')}")
            return False
        
        
        date = e['timeInterval']['start'].split('T')[0]

        self.cursor.execute("SELECT 1 FROM events WHERE name = ? AND date = ?", (name, date))
        if self.cursor.fetchone() is not None:
            return False
        
        return True
        
    
    def scrap_event(self, e):
        event = Event(
            name=e.get('name'),
            country=e.get('countryName'),
            event_id=e['classes'][0]['id'],
            date=e['timeInterval']['start'].split('T')[0],
            location=(e['location']['latitude'], e['location']['longitude'])
        )

        try:
            event.get_map(self.cookies)
            
        except Exception as ex:
            print_red(f"Error getting map for event '{event.name}': {ex}")

        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
    
        if event.map:
            cursor.execute('''
                INSERT INTO events (name, class_id, map, lat, lon, country, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (event.name, event.id, event.map, event.location[0], event.location[1], event.country, event.date))
            print_green(f"Event '{event.name}' added to the database.")
        
        
        else:
            cursor.execute('''
                INSERT INTO events (name, class_id, map, lat, lon, country, date)
                VALUES (?, ?, NULL, ?, ?, ?, ?)
            ''', (event.name, event.id, event.location[0], event.location[1], event.country, event.date))
            print(f"Event '{event.name}' added to the database without map.")
        
        
        
        conn.commit()
        conn.close()
        
        with self.lock:
            self.counter += 1
            
            


if __name__ == '__main__':
    scrapper = LiveloxScrapper(max_events=100000, country=None)
    scrapper.scrap_events(start_date=datetime(2025, 7, 24), days_delta=14)
