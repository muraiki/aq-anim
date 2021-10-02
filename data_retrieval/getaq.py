import requests

API_URL = 'https://api.purpleair.com/v1/sensors'


def main() -> None:
    with open('.api_key') as fh:
        apikey = fh.readline().strip()

    headers = {'X-API-Key': apikey}

    data = {
        'fields': 'name,private,last_seen,latitude,longitude,position_rating,pm1.0,pm2.5,pm10.0',
        'location_type': 0,  # Outside
        'max_age': 86400,
        'nwlat': 40.506830,
        'nwlng': -80.088923,
        'selat': 40.378196,
        'selng': -79.852636
    }

    r = requests.get(
        API_URL,
        params=data,
        headers=headers
    )

    print(r.text)


if __name__ == '__main__':
    main()
