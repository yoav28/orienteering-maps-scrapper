import subprocess, json


def clean_event(x: dict) -> dict or None:
    # dict_keys(['id', 'timeInterval', 'name', 'countryId', 'countryName', 'countryFlagUrl', 'organisers', 'icon', 'location', 'boundingPolygonVertices', 'participantCount', 'classCount', 'eventAccessMode', 'relevance', 'publicationTime', 'classes', 'properties', 'isRelay', 'allowMergeAllRelayLegs'])

    wanted_keys = ['id', 'name', 'location', 'classes']

    # if any of the keys missing return None
    if any(key not in x for key in wanted_keys):
        return None

    return {key: x[key] for key in wanted_keys}


url = 'https://www.livelox.com/Home/SearchEvents'
order_by = 'participantCount'
max_number_of_results = 999999
from_date = '2024-09-15'
to_date = '2024-09-30'
lon = 17.9276064
lat = 59.4473886
countryId = 207

request = f"""
curl '{url}' \
    -H 'accept: application/json, text/javascript, */*; q=0.01' \
    -H 'accept-language: en-US,en;q=0.9,he;q=0.8,sv;q=0.7' \
    -H 'content-type: application/json' \
    -H 'cookie: ple=true; .AspNetCore.Session=CfDJ8ALxyBbXf41ItuOgHL56OXlyJgXrDwVSsfBz7%2FIek05phmI8iQA1SRZBH%2FvhD6Mg2WdVj4gzd0siMR3gIM2B3tnzp6u380DvTtDmx8D1qe%2BiWoHr3qjIJan%2BG7P%2FoCh%2FVOqzmavkvSYXmbD9dKWuux3%2FSqTSJknyAQDn0SbKf2fN; culture=de-DE; ut=30a1775a9fac4c5dafb3c15f40814591649e318336704db392fc6e55d1f8ad8c; pld=%7B%22personId%22%3A175433%2C%22token%22%3A%22840be38e04404b27acd4b310fa52bc1b%22%7D' \
    -H 'origin: https://www.livelox.com' \
    -H 'priority: u=1, i' \
    -H 'referer: https://www.livelox.com/?tab=allEvents&timePeriod=customTimePeriod&from=2024-09-30&to=2024-09-15&country=SWE&sorting=participantCount' \
    -H 'sec-ch-ua: "Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "macOS"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36' \
    -H 'x-requested-with: XMLHttpRequest' \
    --data-raw '{{"organisedByMyOrganisationsOnly":false,"countryId":{countryId},"timePeriod":"customTimePeriod","from":"{from_date}","to":"{to_date}T22:00:00.000Z","text":"","orderBy":"{order_by}","geoCoordinate":{{"latitude":{lat},"longitude":{lon}}},"properties":null,"maxNumberOfResults":{max_number_of_results}}}'
"""

response = subprocess.run(request, shell=True, capture_output=True)
output = response.stdout.decode('utf-8')
# load output as json
...

events_ = json.loads(output)
events = []

for event in events_:
    if e := clean_event(event):
        events.append(e)

print(events)
