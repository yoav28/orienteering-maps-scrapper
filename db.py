import sqlite3


class SQL:

    def __init__(self, path: str, initialize: bool = False):
        self.db_path = path

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        if initialize:
            self.initialize_db()


    def initialize_db(self):
        # Table: events
        # - id: Unique identifier for the event (integer, auto-incrementing, primary key, NOT NULL)
        # - name: Name of the event (text)
        # - class_id: Class ID of the event (text)
        # - map: Map associated with the event (text, can be NULL)
        # - lat: Latitude of the event (real)
        # - lon: Longitude of the event (real)
        # - date: Date of the event (text)
        # - country: Country where the event is held (text)
        # - source: Source of the event (text, can be NULL)

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                name TEXT,
                class_id TEXT,
                map TEXT,
                lat REAL,
                lon REAL,
                date TEXT,
                country TEXT,
                source TEXT
            )
        ''')

        self.conn.commit()


    def event_exists(self, name: str, date: str) -> bool:
        self.cursor.execute("SELECT 1 FROM events WHERE name = ? AND date = ?", (name, date))
        return self.cursor.fetchone() is not None


    def map_exists(self, map_name: str) -> bool:
        self.cursor.execute("SELECT 1 FROM events WHERE map = ?", (map_name,))
        return self.cursor.fetchone() is not None


    def event_or_map_exists(self, name: str, date: str, map_name: str | None) -> bool:
        self.cursor.execute("SELECT 1 FROM events WHERE (name = ? AND date = ?) OR (map = ?)", (name, date, map_name))
        return self.cursor.fetchone() is not None


    def insert_event(self, name: str, class_id: str, map_name: str | None, lat: float, lon: float, country: str, date: str, source: str):
        self.cursor.execute('''
            INSERT INTO events (name, class_id, map, lat, lon, country, date, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, str(class_id), map_name, lat, lon, country, date, source))

        self.conn.commit()


    def close(self):
        self.conn.close()


def remove_duplicates():
    answer = input("Do you want to remove duplicate events? (y/n): ").strip().lower()

    if answer != 'y':
        return print("Skipping duplicate removal.")

    db = SQL('maps.db', initialize=False)

    db.cursor.execute("""
        DELETE FROM events
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM events
            WHERE map IS NOT NULL
            GROUP BY map
        ) AND map IS NOT NULL;
        """)

    db.conn.commit()
    return db.conn.close()
