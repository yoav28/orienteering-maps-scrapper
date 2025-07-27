from event import LoggatorEvent
import json


class Cache:

    def __init__(self):
        try:
            with open(".cache.json", "r") as f:
                self.cache = json.loads(f.read())
                print("Cache loaded from file")

        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cache = {}


    def set(self, key, value):
        self.cache[key] = value


    def get(self, key):
        return self.cache.get(key)


    def delete(self, key):
        if key in self.cache:
            del self.cache[key]


    def clear(self):
        self.cache.clear()


    def save(self):
        with open(".cache.json", "w") as f:
            f.write(json.dumps(self.cache, indent=4))
