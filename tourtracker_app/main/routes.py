from flask import render_template, make_response, redirect, url_for, flash, request, app
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user
from tourtracker_app import db, jwt as jwt_extended
from tourtracker_app.models.tour_models import Tour, TourActivities
from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
from tourtracker_app.main import bp
from tourtracker_app.main.forms import TourForm
import polyline
from requests import HTTPError
from datetime import datetime, date
from tourtracker_app.strava_api_auth.strava_api_utilities import get_strava_activities

# TODO: remove auth elements from database tables
# TODO: do we want to use auth server uuid for all user ID or are we happy to transmit email/username over jwt?
# TODO: update tests


@jwt_extended.invalid_token_loader
def invalid_token(reason):
    return redirect(url_for('auth.login'))


@jwt_extended.unauthorized_loader
def unauthorised_loader(reason):
    return redirect(url_for('auth.login'))


@bp.route('/', methods=['GET'])
@bp.route('/index', methods=['GET'])
@jwt_required(optional=True, locations=['query_string'])
def index():
    print('in index route')
    if current_user:
        token = request.args.get('jwt')
        redirect_url = f"{url_for('main.user_profile')}?jwt={token}"
        return redirect(redirect_url)
        #return redirect(url_for('main.user_profile'))
    return render_template('index.html')


@bp.app_template_filter('timestamp_to_str')
def timestamp_to_str(timestamp):
    return date.fromtimestamp(timestamp)

@bp.route('/profile')
@jwt_required(locations=['query_string', 'headers'])
def user_profile():
    form = TourForm()
    print(current_user.username)
    if current_user.strava_athlete_id is not None: # TODO probably a better/more robust way to do this
        strava_authenticated = True
    else:
        strava_authenticated = False

    return render_template('user_profile.html',
                           username=current_user.username,
                           strava_authenticated=strava_authenticated,
                           is_admin=current_user.isadmin,
                           user_tours=current_user.tours,
                           form=form) #TODO put in logic for if we are not linked to strava


@bp.route('/tour/<uuid>', methods=['GET'])
@jwt_required()
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


@bp.route('/createtour', methods=['GET', 'POST'])
@jwt_required()
def create_tour():
    if request.method == 'GET':
        form = TourForm()
        if current_user.strava_athlete_id is not None:  # TODO probably a better/more robust way to do this
            strava_authenticated = True
        else:
            # FIXME is this code even reachable if we don't show create tour button
            # FIXME on user profile template? Guess user could follow direct URL
            strava_authenticated = False
        return render_template('create_tour.html',
                               strava_authenticated=strava_authenticated,
                               form=form)  # TODO put in logic for if we are not linked to strava
    if request.method == 'POST':
        form = TourForm()
        if form.validate_on_submit():
            tour_name = form.tour_name.data

            start_timestamp = (datetime(form.start_date.data.year, form.start_date.data.month, form.start_date.data.day)).timestamp()
            end_timestamp = (datetime(form.end_date.data.year, form.end_date.data.month, form.end_date.data.day)).timestamp()

            # if form.auto_refresh.data is True:
            #     refresh_interval = 21600
            #     last_refresh = int(round(datetime.now().timestamp()))
            # else:
            #     refresh_interval = None
            #     last_refresh = None

            tour = Tour(
                tour_name=tour_name,
                start_date=start_timestamp,
                end_date=end_timestamp,
                # auto_refresh=form.auto_refresh.data,
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

        flash('Site linking error!')
        print(form.errors)
        return redirect(url_for('main.user_profile'))


@bp.route('/tour/refresh/<uuid>', methods=['GET'])
@jwt_required()
def refresh_tour(uuid):
    tour = db.session.execute(db.select(Tour).filter_by(tour_uuid=uuid)).first()
    activities = get_strava_activities(current_user, tour[0].start_date, tour[0].end_date)
    for activity in activities:
        db.session.merge(TourActivities(
            strava_activity_id=activity['activity_id'],
            activity_name=activity['activity_name'],
            activity_date=activity['activity_date'],
            summary_polyline=activity['polyline'],
            parent_tour=tour[0].tour_uuid,
            user_id=current_user.uuid
        ))
    db.session.commit()
    return redirect(url_for('main.tour_detail', uuid=tour[0].tour_uuid))


@bp.route('/deletetour/<uuid>', methods=['GET'])
@jwt_required()
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


