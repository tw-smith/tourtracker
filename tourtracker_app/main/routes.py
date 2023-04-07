from flask import render_template, make_response, jsonify, redirect, current_app, request, url_for, flash
from flask_login import login_required, current_user
from tourtracker_app import db
from tourtracker_app.models.auth_models import User, Tour, TourActivities
from tourtracker_app.models.strava_api_models import StravaAccessToken
from tourtracker_app.main import bp
from tourtracker_app.main.forms import TourForm
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
    form = TourForm()
    if current_user.strava_athlete_id is not None: # TODO probably a better/more robust way to do this
        strava_authenticated = True
    else:
        strava_authenticated = False

    user_tours = current_user.tours

    return render_template('user_profile.html', email=current_user.email, strava_authenticated=strava_authenticated, user_tours=user_tours, form=form) #TODO put in logic for if we are not linked to strava


@bp.route('/tour/<uuid>', methods=['GET'])
@login_required
def tour_detail(uuid):
    tour = db.session.execute(db.select(Tour).filter_by(tour_uuid=uuid)).first()
    tour = tour[0]
    return render_template('tourdetail.html', tour=tour)

@bp.route('/tour/embed/<uuid>', methods=['GET'])
def tour_embed(uuid):
    tour = db.session.execute(db.select(Tour).filter_by(tour_uuid=uuid)).first()
    tour = tour[0]
    return render_template('tourembed.html', tour=tour)


@bp.route('/tour/data/<uuid>', methods=['GET'])
def get_tour_activities(uuid):
    tour_activities_result = db.session.execute(db.select(TourActivities.strava_activity_id, 
                                                          TourActivities.activity_name,
                                                          TourActivities.activity_date,
                                                          TourActivities.summary_polyline).filter_by(parent_tour=uuid).order_by(TourActivities.activity_date.asc())).all()

    tour_activities = []
    for row in tour_activities_result:
        row_dict = row._asdict()
        points = polyline.decode(row_dict['summary_polyline'])
        latlong = []
        for point in points:
            latlong.append({'lat': point[0], 'lng': point[1]})
        row_dict['points'] = latlong
        row_dict.pop('summary_polyline')
        tour_activities.append(row_dict)
    return make_response(tour_activities, 200)


@bp.route('/createtour', methods=['POST'])
@login_required
def create_tour():
    form = TourForm()
    print(form.site_url.data)
    if form.validate_on_submit():
        tour_name = form.tour_name.data
        site_url = form.site_url.data

        date_format = "%Y-%m-%d"
        epoch = datetime(1970, 1, 1)

        start_timestamp = (datetime(form.start_date.data.year, form.start_date.data.month, form.start_date.data.day)).timestamp()
        end_timestamp = (datetime(form.end_date.data.year, form.end_date.data.month, form.end_date.data.day)).timestamp()

        if form.auto_refresh.data is True:
            refresh_interval = 21600
            last_refresh = int(round(datetime.now().timestamp()))
        else:
            refresh_interval = None
            last_refresh = None

        tour = Tour(
            tour_name=tour_name,
            site_url=site_url,
            start_date=start_timestamp,
            end_date=end_timestamp,
            refresh_interval=refresh_interval,
            last_refresh=last_refresh,
            user_id=current_user.uuid
        )
        db.session.add(tour)
        db.session.commit()

        activities = get_strava_activities(current_user, start_timestamp, end_timestamp)
        for activity in activities:
            new_activity = TourActivities(
                strava_activity_id=activity['activity_id'],
                activity_name=activity['activity_name'],
                activity_date=activity['activity_date'],
                summary_polyline=activity['polyline'],
                parent_tour=tour.tour_uuid,
                user_id=current_user.uuid
            )
            db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('main.tour_detail', uuid=tour.tour_uuid))


        
        # TODO return a url of the form /tour/uuid or tour?uuid=uuid here. Then pull that uuid from the URL into the TS script to make the GET
        # request necessary to draw the map

        # TODO make sure only the owner can view this page. But does this then impact our ability to respond to the TS GET request from anyone?
        # if we make a route /tour/data/<uuid> return only a json and /tour/uuid return the rendered tour admin page then we should be good

    flash('Site linking error!')
    print(form.errors)
    return redirect(url_for('main.user_profile'))


@bp.route('/deletetour/<uuid>', methods=['GET'])
@login_required
def delete_tour(uuid):
    tour = db.session.execute(db.select(Tour).filter_by(tour_uuid=uuid)).first()

    if tour[0].user.uuid == current_user.uuid:
        db.session.delete(tour[0])
        db.session.commit()
        return redirect(url_for('main.user_profile'))
    else:
        print('naughty')
        return redirect(url_for('main.index'))
    # TODO make sure user can only delete their own tours


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
                               'polyline': activity['map']['summary_polyline'],
                               'points': latlong})
        params['page'] += 1
        print("page number" + str(params['page']))
    return activities