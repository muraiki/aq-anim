import argparse
from datetime import datetime, timezone
from decimal import Decimal
from typing import Tuple, Dict
import json

import requests
import aqi

API_URL = 'https://api.purpleair.com/v1/sensors'

FIELDS = ('name', 'private', 'last_seen', 'latitude', 'longitude', 'position_rating', 'pm1.0', 'pm2.5', 'pm10.0')
ALL_FIELDS = tuple(['id'] + list(FIELDS))
# Record tuple will be one longer than FIELDS, since an integer id is always included first.
Record = Tuple[int, int, str, int, int, float, float, int, float, float, float]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Fetch PurpleAir API data for a bounded region and calculate the EPA IAQI. Outputs the result to '
                    'STDOUT as line-delimited JSON.',
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


def parse_record(fields: Tuple[str], record: Record) -> Dict:
    """
    Takes a sensor's record from the PurpleAir API, calculates the EPA IAQI for PM 2.5, and returns a dictionary.
    :param fields: A string tuple of the names to use for the items in the record.
    :param record: The array returned by the PurpleAir API.
    :return: A dictionary with keys corresponding to those found in `fields`, plus key epa_iaqi_25.
    """
    assert len(fields) == len(record)
    stats = {k: v for k, v in zip(fields, record)}
    if stats['pm2.5'] <= 500:
        stats['epa_iaqi_25'] = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(stats['pm2.5']), algo=aqi.ALGO_EPA)
        assert isinstance(stats['epa_iaqi_25'], Decimal)
        stats['epa_iaqi_25'] = int(stats['epa_iaqi_25'])
    else:
        # EPA AQI is undefined for pm2.5 > 500.
        # https://www.airnow.gov/aqi/aqi-basics/extremely-high-levels-of-pm25/
        stats['epa_iaqi_25'] = None
    return stats


def iso_date(d: float) -> str:
    """
    Convert a float timestamp to an ISO 8601 format string in UTC.
    :param d: A timestamp.
    :return: A string ISO 8601 UTC datetime.
    """
    return datetime.fromtimestamp(d, tz=timezone.utc).isoformat()


def main() -> None:
    args = parse_args()

    if args.apikey is not None:
        apikey = args.apikey
    else:
        with open(args.keyfile) as fh:
            apikey = fh.readline().strip()

    headers = {'X-API-Key': apikey}

    params = {
        'fields': ','.join(FIELDS),
        'location_type': 0,  # Outside
        'max_age': args.maxage,
        'nwlat': args.nwlat,
        'nwlng': args.nwlng,
        'selat': args.selat,
        'selng': args.selng
    }

    r = requests.get(
        API_URL,
        params=params,
        headers=headers
    )

    data = r.json()

    readings = []
    for record in data['data']:
        parsed = parse_record(ALL_FIELDS, record)

        for plain_key in ['api_version', 'location_type', 'max_age', 'firmware_default_version']:
            parsed[plain_key] = data[plain_key]

        parsed['time_stamp'] = iso_date(data['time_stamp'])
        parsed['data_time_stamp'] = iso_date(data['data_time_stamp'])
        parsed['last_seen'] = iso_date(parsed['last_seen'])

        readings.append(parsed)

    print('\n'.join([json.dumps(reading) for reading in readings]))


if __name__ == '__main__':
    main()
