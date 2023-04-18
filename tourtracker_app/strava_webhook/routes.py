from tourtracker_app.strava_webhook import bp
from functools import wraps
import requests
from flask import current_app, request, make_response, render_template, flash, redirect, url_for
from urllib.parse import urlencode
from flask_login import login_required, current_user
from tourtracker_app.models.strava_api_models import StravaWebhookSubscription
from tourtracker_app import db


@bp.route('/subscribe')
async def create_webhook_subscription():
    payload = dict(client_id=current_app.config['STRAVA_CLIENT_ID'], 
                   client_secret=current_app.config['STRAVA_CLIENT_SECRET'],
                   callback_url=current_app.config['STRAVA_WEBHOOK_CALLBACK_URL'], 
                   verify_token=current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN'])
    base_url = current_app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.post(base_url, data=payload).json()
    print(response)
    strava_webhook_subscription = StravaWebhookSubscription(
        subscription_id=response['id']
    )
    db.session.add(strava_webhook_subscription)
    db.session.commit()
    return redirect(url_for('strava_webhook.webhook_admin'))


@bp.route('/view')
@login_required
def view_webhook_subscription():
    params = dict(client_id=current_app.config['STRAVA_CLIENT_ID'],
                  client_secret=current_app.config['STRAVA_CLIENT_SECRET'])
    base_url = current_app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.get(base_url + ("?" + urlencode(params)))
    print(response.json())
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
        print(response.json())
        flash('Some error while deleting!')
        flash(response.json())
    return redirect(url_for('strava_webhook.webhook_admin'))

@bp.route('/callback', methods=['GET', 'POST']) #TODO behaviour on POST when strava sends an update
def webhook_response():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')

        if verify_token != current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN']:
            return 'error'
        else:
            body = {'hub.challenge': challenge}
            return make_response(body, 200)



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



