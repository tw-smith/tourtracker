from flask import render_template, make_response, jsonify, redirect, current_app, request, url_for
from flask_login import login_required, current_user
from tourtracker_app import db
from tourtracker_app.models.auth_models import User, OriginSite, UserActivities
from tourtracker_app.models.strava_api_models import StravaAccessToken
from tourtracker_app.main import bp
from tourtracker_app.main.forms import StravaActivitiesForm
import polyline
from urllib.parse import urlencode
import requests
from datetime import datetime
import time



@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.user_profile'))
    return render_template('index.html')


@bp.route('/profile')
@login_required
def user_profile():
    form = StravaActivitiesForm()

    if current_user.strava_athlete_id is not None: # TODO probably a better/more robust way to do this
        strava_authenticated = True
    else:
        strava_authenticated = False

    return render_template('user_profile.html', email=current_user.email, strava_authenticated=strava_authenticated, form=form) #TODO put in logic for if we are not linked to strava


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
        full_url = base_url + ("?" + urlencode(params) if params else "") #TODO check if token is valid
        response = requests.get(full_url, headers=headers)
        response = response.json()
        print(response)
        if (not response):
            break
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
                               'points': latlong})
        params['page'] += 1
        print("page number" + str(params['page']))
    return activities
    



@bp.route('/get_activities_auto', methods=['POST'])
def get_activities_auto():
    current_timestamp = int(round(datetime.now().timestamp()))
    # content_type = request.headers.get('Content-Type')
    # if content_type != 'application/json;charset=utf-8':
    #     return 'Content Type not supported!'
    request_origin = request.headers.get('Origin')
    site = db.session.execute(db.select(OriginSite).filter_by(site_url=request_origin)).first()
    if site:
        if (site.last_refresh + site.refresh_interval) < current_timestamp:
            activities = get_strava_activities(site.user, site.start_date, current_timestamp)
            return make_response(activities, 200)
        activities = db.session.execute(db.Select(UserActivities).filter_by(origin_site=request_origin)).all()
        return make_response(activities, 200)


@bp.route('/get_activities', methods=['POST'])
def get_activities():
    content_type = request.headers.get('Content-Type')
    if content_type != 'application/json;charset=utf-8':
        return 'Content Type not supported!'
    json = request.json
    date_format = "%Y-%m-%d"
    epoch = datetime(1970,1,1)
    start_date = json['startDate']
    end_date = json['endDate']
    start_timestamp = (datetime.strptime(start_date, date_format) - epoch).total_seconds()
    end_timestamp = (datetime.strptime(end_date, date_format) - epoch).total_seconds()
    # base_url = 'https://www.strava.com/api/v3/athlete/activities'

    # Get access token
    # access_token = current_user.strava_access_token[0]

    # # Check if access token has expired, and if so, refresh tokens
    # if access_token.check_token_valid() == False:
    #     access_token.refresh_access_token(current_user.strava_refresh_token[0])

    # headers = {'Authorization': 'Bearer ' + current_user.strava_access_token[0].access_token}
    # params = dict(before=end_timestamp, after=start_timestamp, page=1, per_page=30)
    # activities = []
    # while True:
    #     full_url = base_url + ("?" + urlencode(params) if params else "") #TODO check if token is valid
    #     response = requests.get(full_url, headers=headers)
    #     response = response.json()
    #     print(response)
    #     if (not response):
    #         break
    #     for activity in response:
    #         if activity['sport_type'] != 'Ride':
    #             continue
    #         latlong = []
    #         points = polyline.decode(activity['map']['summary_polyline'])
    #         for point in points:
    #             latlong.append({'lat': point[0], 'lng': point[1]})
    #         activities.append({'activity_id': activity['id'],
    #                            'activity_name': activity['name'],
    #                            'activity_date': activity['start_date_local'],
    #                            'points': latlong})
    #     params['page'] += 1
    #     print("page number" + str(params['page']))
    activities = get_strava_activities(current_user, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    return make_response(activities, 200)
