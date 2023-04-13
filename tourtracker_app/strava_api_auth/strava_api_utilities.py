import requests
from requests import HTTPError
from urllib.parse import urlencode
import polyline


def handle_strava_api_response(response):
    if response.ok:
        return response.json()
    else:
        if response.status_code == 400:
            raise HTTPError('Strava Auth Error')
        



def get_strava_activities(user, start_timestamp, end_timestamp):
    base_url = 'https://www.strava.com/api/v3/athlete/activities'
        # Get access token
    access_token = user.strava_access_token[0]

    # Check if access token has expired, and if so, refresh tokens
    if access_token.check_token_valid() == False:
        access_token.refresh_access_token(user.strava_refresh_token[0])

    headers = {'Authorization': 'Bearer ' + user.strava_access_token[0].access_token}
    params = dict(before=end_timestamp, after=start_timestamp, page=1, per_page=30)
    activities = []
    while True:
        full_url = base_url + ("?" + urlencode(params) if params else "")
        response = handle_strava_api_response(requests.get(full_url, headers=headers))
        for activity in response:
            if activity['sport_type'] != 'Ride':
                continue
            latlong = []
            points = polyline.decode(activity['map']['summary_polyline'])
            for point in points:
                latlong.append({'lat': point[0], 'lng': point[1]})
                activities.append({'activity_id': activity['id'],
                                    'activity_name': activity['name'],
                                    'activity_date': activity['start_date_local'],
                                    'polyline': activity['map']['summary_polyline'],
                                    'points': latlong})
            params['page'] += 1
            print("page number" + str(params['page']))
        return activities