from tourtracker_app.strava_webhook import bp
from functools import wraps
import requests
from flask import current_app, request, make_response, render_template, flash, redirect, url_for
from urllib.parse import urlencode
from flask_login import login_required, current_user


@bp.route('/subscribe')
async def create_webhook_subscription(app):
    params = dict(client_id=app.config['STRAVA_CLIENT_ID'], 
                  client_secret=app.config['STRAVA_CLIENT_SECRET'],
                  callback_url=app.config['STRAVA_WEBHOOK_CALLBACK_URL'], 
                  verify_token=app.config['STRAVA_WEBHOOK_VERIFY_TOKEN'])
    base_url = app.config['STRAVA_WEBHOOK_BASE_URL']
    post_url = base_url + ("?" + urlencode(params))
    response = await requests.post(post_url)
    print('response')
    return response


@login_required
@bp.route('/view')
def view_webhook_subscription(app):
    params = dict(client_id=app.config['STRAVA_CLIENT_ID'],
                  client_secret=app.config['STRAVA_CLIENT_SECRET'])
    base_url = app.config['STRAVA_WEBHOOK_BASE_URL']
    response = requests.post(base_url + ("?" + urlencode(params)))
    print(response)
    return render_template('webhook_admin.html', subscription_info=response)


@login_required
@bp.route('/delete')
def delete_webhook_subscription(app):
    return render_template('webhook_admin.html', subscription_info='delete sub placeholder')



@bp.route('/', methods=['GET', 'POST'])
def webhook_response():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')
        if verify_token is not current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN']:
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


#TODO sort out the admin required functionality
# https://stackoverflow.com/questions/61939800/role-based-authorization-in-flask-login
@login_required
@admin_required
@bp.route('/admin', methods=['GET'])
def webhook_admin():
#    if current_user.isadmin:
    return render_template('webhook_admin.html', subscription_info=None)
#    else:
 #       return 'login required'



