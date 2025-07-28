# Orienteering Maps Scraper

This project is a Python-based web scraper for downloading orienteering maps from various sources. It currently supports Loggator, Livelox and OMaps, with the ability to extend to other services.

## Disclaimer

This tool is intended for educational use only. Please respect the terms of service of the websites you are scraping.


## Features

- Fetches event data from Loggator, Livelox and OMaps.
- Downloads map images associated with events.
- Stores event and map data in a local SQLite database.

## Project Structure

```

|-- livelox/
|   |-- __init__.py
|   |-- event.py
|   |-- get_map.py
|-- loggator/
|   |-- __init__.py
|   |-- .cache.json
|   |-- cache.py
|   |-- event.py
|   |-- livelox.py
|-- omaps/
|   |-- __init__.py
```
