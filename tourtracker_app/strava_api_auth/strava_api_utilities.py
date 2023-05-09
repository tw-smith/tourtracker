import requests
#from tourtracker_app.strava_api_auth.error_handlers import StravaBadRequestException

from urllib.parse import urlencode
import polyline


def handle_strava_api_response(response):
    from tourtracker_app.strava_api_auth.error_handlers import StravaBadRequestException
    # print(response)
    if response:
        response_json = response.json()
        if response.ok:
            return response_json
        else:
            if response.status_code == 400 or response.status_code == 401:
                raise StravaBadRequestException(response_json['message'])
            if response.status_code == 429:
                raise StravaBadRequestException(response_json['message'])
        

def strava_request_header_prep(user):
    # Check access token validity and refresh if required
    access_token = user.strava_access_token[0]
    if access_token.check_token_valid() is False:
        access_token.refresh_access_token(user.strava_refresh_token[0])

    # Set request headers
    return {'Authorization': 'Bearer ' + user.strava_access_token[0].access_token}


def get_individual_strava_activity(user, activity_id):
    base_url = 'https://www.strava.com/api/v3/activities'
    headers = strava_request_header_prep(user)
    full_url = base_url + '/' + str(activity_id)
    response = handle_strava_api_response(requests.get(full_url, headers=headers))
    return response


def get_strava_activities(user, start_timestamp, end_timestamp):
    base_url = 'https://www.strava.com/api/v3/athlete/activities'
    headers = strava_request_header_prep(user)
    params = dict(before=end_timestamp, after=start_timestamp, page=1, per_page=30)
    activities = []
    full_url = base_url + ("?" + urlencode(params) if params else "")
    print(full_url)
    print(headers)
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
    return activities
