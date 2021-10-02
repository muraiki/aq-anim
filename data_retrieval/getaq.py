import argparse
import requests

API_URL = 'https://api.purpleair.com/v1/sensors'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Fetch PurpleAir API data for a bounded region and output the result to STDOUT.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--nwlat',
        type=float,
        default=40.506830,
        help='The northwest bounding box latitude.'
    )

    parser.add_argument(
        '--nwlng',
        type=float,
        default=-80.088923,
        help='The northwest bounding box longitude.'
    )

    parser.add_argument(
        '--selat',
        type=float,
        default=40.378196,
        help='The southeast bounding box latitude.'
    )

    parser.add_argument(
        '--selng',
        type=float,
        default=-79.852636,
        help='The southeast bounding box longitude.'
    )

    parser.add_argument(
        '--maxage',
        type=int,
        default=60 * 60,
        help='Only get results from sensors updated in this past number of seconds.'
    )

    parser.add_argument(
        '--keyfile',
        type=str,
        default='.api_key',
        help='Path to a file containing the API key.'
    )

    parser.add_argument(
        '--apikey',
        type=str,
        default=None,
        help='An API key. If specified, overrides --keyfile.'
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.apikey is not None:
        apikey = args.apikey
    else:
        with open(args.keyfile) as fh:
            apikey = fh.readline().strip()

    headers = {'X-API-Key': apikey}

    data = {
        'fields': 'name,private,last_seen,latitude,longitude,position_rating,pm1.0,pm2.5,pm10.0',
        'location_type': 0,  # Outside
        'max_age': args.maxage,
        'nwlat': args.nwlat,
        'nwlng': args.nwlng,
        'selat': args.selat,
        'selng': args.selng
    }

    r = requests.get(
        API_URL,
        params=data,
        headers=headers
    )

    print(r.text)


if __name__ == '__main__':
    main()
