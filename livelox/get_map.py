import requests, os



def get_map(class_id: int):
    try:
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9,he;q=0.8,sv;q=0.7',
            'content-type': 'application/json',
            'origin': 'https://www.livelox.com',
            'priority': 'u=1, i',
            'referer': f'https://www.livelox.com/Viewer/SM2025-Medel-Stafett-traning-Norra-Mosaren/Bana-A?classId={class_id}',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest',
        }
                
        json_data = {
            'eventId': None,
            'classIds': [
                class_id,
            ],
            'courseIds': None,
            'relayLegs': [],
            'relayLegGroupIds': [],
            'routeReductionProperties': {
                'distanceTolerance': 1,
                'speedTolerance': 0.1,
            },
            'includeMap': True,
            'includeCourses': True,
        }

        response = requests.post('https://www.livelox.com/Data/ClassBlob', cookies=cookies, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()

        if "general" in data and "classBlobUrl" in data["general"]:
            blob_url = data["general"]["classBlobUrl"]
            if "map-image" in blob_url:
                return blob_url
            
            map_response = requests.get(blob_url)
            map_response.raise_for_status()
            
            map_data = map_response.json()["map"]

            if map_data.get("isHidden"):
                raise ValueError("The map is hidden and cannot be accessed.")

            return map_data["images"][0]["url"]

        if "map" in data:
            return data["map"]["images"][0]["url"]


        raise ValueError("Class blob URL not found in the response.")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    
    except (ValueError, KeyError) as e:
        print(f"An error occurred: {e}")
        return None
