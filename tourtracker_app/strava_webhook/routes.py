from tourtracker_app.strava_webhook import bp
from functools import wraps
import requests
from flask import current_app, request, make_response, render_template, flash, redirect, url_for
from urllib.parse import urlencode
from flask_login import login_required, current_user
from tourtracker_app.models.strava_api_models import StravaWebhookSubscription
from tourtracker_app.models.tour_models import TourActivities, Tour
from tourtracker_app.models.auth_models import User
from tourtracker_app import db
from tourtracker_app.strava_api_auth.strava_api_utilities import get_individual_strava_activity
from datetime import datetime

#FIXME does the subscribe endpoint need a @login_required decorator as well?
@bp.route('/subscribe')
async def create_webhook_subscription():
    payload = dict(client_id=current_app.config['STRAVA_CLIENT_ID'], 
                   client_secret=current_app.config['STRAVA_CLIENT_SECRET'],
                   callback_url=current_app.config['STRAVA_WEBHOOK_CALLBACK_URL'], 
                   verify_token=current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN'])
    base_url = current_app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.post(base_url, data=payload)
    if response.ok:
        response_json = response.json()
        strava_webhook_subscription = StravaWebhookSubscription(
            subscription_id=response_json['id']
        )
        db.session.add(strava_webhook_subscription)
        db.session.commit()
    else:
        flash('Webhook subscription error!')
    return redirect(url_for('strava_webhook.webhook_admin'))


@bp.route('/view')
@login_required
def view_webhook_subscription():
    params = dict(client_id=current_app.config['STRAVA_CLIENT_ID'],
                  client_secret=current_app.config['STRAVA_CLIENT_SECRET'])
    base_url = current_app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.get(base_url + ("?" + urlencode(params)))
    return render_template('webhook_admin.html', subscription_info=response.json())



@bp.route('/delete')
@login_required
def delete_webhook_subscription():
    row = db.session.execute(db.Select(StravaWebhookSubscription)).first()
    subscription_id = row[0].subscription_id
    payload = dict(client_id=current_app.config['STRAVA_CLIENT_ID'], 
                   client_secret=current_app.config['STRAVA_CLIENT_SECRET'])
    base_url = current_app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.delete(base_url + '/' + str(subscription_id), data=payload)
    if response.status_code == 204:
        db.session.delete(row[0])
        db.session.commit()
        flash('Delete successful')
    else:
        flash('Some error while deleting!')
        flash(response.json())
    return redirect(url_for('strava_webhook.webhook_admin'))

@bp.route('/callback', methods=['GET', 'POST'])
def webhook_response():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')
        if verify_token != current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN']:
            body = {'message': 'bad verify token'}
            return make_response(body, 400)
        else:
            body = {'hub.challenge': challenge}
            return make_response(body, 200)
    if request.method == 'POST': #TODO this might need to be async to return 200 to strava within 2 secs
        print('in post branch')
        post_body = request.get_json()
        print(post_body)
        if post_body['object_type'] == 'athlete':
            #TODO do athelete stuff
            return make_response({}, 200)
        elif post_body['object_type'] == 'activity':
            activity_id = post_body['object_id']
            # We need to find the user manually because current_user doesn't work with a POST request from
            # Strava because the request is unauthenticated/anonymous
            user = db.session.execute(db.Select(User).filter_by(strava_athlete_id=post_body['owner_id'])).first()
            user = user[0]
            if post_body['aspect_type'] == 'create':
                data = get_individual_strava_activity(user, activity_id)
                in_date_range, tour = check_tour_date_range(data['start_date_local'], user)
                if in_date_range:
                    if check_activity_exists(data['id']) is False:
                        new_activity = TourActivities(strava_activity_id=data['id'],
                                                      activity_name=data['name'],
                                                      activity_date=data['start_date_local'],
                                                      summary_polyline=data['map']['summary_polyline'],
                                                      parent_tour=tour.tour_uuid,
                                                      user_id=user.uuid)
                        db.session.add(new_activity)
                        db.session.commit()

            elif post_body['aspect_type'] == 'update':
                allowed_sport_types = [
                    'Ride',
                    'EBikeRide'
                ]
                need_to_update_db = False
                activity = db.session.execute(db.Select(TourActivities).filter_by(strava_activity_id=activity_id)).first()
                for field in post_body['updates']:
                    if field == 'title':
                        activity[0].activity_name = post_body['updates']['title']
                        need_to_update_db = True
                    if field == 'type':
                        if post_body['updates']['type'] not in allowed_sport_types:
                            db.session.delete(activity[0])
                            need_to_update_db = True
                    if field == 'private':
                        if post_body['updates']['private'] == 'true':
                            db.session.delete(activity[0])
                            need_to_update_db = True
                if need_to_update_db:
                    db.session.commit()

            elif post_body['aspect_type'] == 'delete':
                activity = db.session.execute(db.Select(TourActivities).filter_by(strava_activity_id=activity_id)).first()
                if activity is not None:
                    db.session.delete(activity[0])
                    db.session.commit()
        return make_response({'success': True}, 200, {'ContentType':'application/json'})


def check_tour_date_range(activity_date, user):
    tours = user.tours
    if tours is not None:
        for tour in tours:
            # Replace Z at end of ISO8601 string with +00:00 to allow compatability with Python < 3.11 fromisoformat
            activity_date = activity_date.replace('Z', '+00:00')
            if tour.start_date <= datetime.fromisoformat(activity_date).timestamp() <= tour.end_date:
                return True, tour
            return False, None
    return False, None


def check_activity_exists(activity_id):
    activity = db.session.execute(db.Select(TourActivities).filter_by(strava_activity_id=activity_id)).first()
    if activity is not None:
        return True
    return False


        








def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.isadmin:
            flash("You don't have permission to view this page!")
            return redirect(url_for('main.user_profile'))
        return func(*args, **kwargs)
    return decorated_view


@bp.route('/admin', methods=['GET'])
@login_required
@admin_required
def webhook_admin():
#    if current_user.isadmin:
    return render_template('webhook_admin.html', subscription_info=None)
#    else:
 #       return 'login required'



