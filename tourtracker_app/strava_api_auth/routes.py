from flask import render_template, current_app, redirect, request, url_for, flash
from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
from tourtracker_app.models.auth_models import User
from tourtracker_app import db
from tourtracker_app.strava_api_auth import bp
from urllib.parse import urlencode
import requests
from flask_login import current_user


def strava_token_request(grant_type, code=None, refresh_token=None):
    client_id = current_app.config['STRAVA_CLIENT_ID']
    client_secret = current_app.config['STRAVA_CLIENT_SECRET']
    post_data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'refresh_token': refresh_token, 'grant_type': grant_type}
    response = requests.post('https://www.strava.com/api/v3/oauth/token', json=post_data)
    response_json = response.json()
    return response_json

@bp.route('/strava') # TODO check scope and behaviour on access denied
def strava_auth():
    strava_base_url = 'https://www.strava.com/oauth/authorize'
    params = dict(client_id=current_app.config['STRAVA_CLIENT_ID'], response_type='code', redirect_uri=current_app.config['STRAVA_REDIRECT_URL'], scope=current_app.config['STRAVA_SCOPE'])
    redirect_url = strava_base_url + ("?" + urlencode(params) if params else "")
    return redirect(redirect_url)

@bp.route('strava_deauth')
def strava_deauth():
    if current_user.strava_access_token[0].check_token_valid() is False:
        current_user.strava_access_token[0].refresh_access_token(current_user.strava_refresh_token[0])
    strava_base_url = 'https://www.strava.com/oauth/deauthorize'
    params = dict(access_token=current_user.strava_access_token[0].access_token)
    deauth_url = strava_base_url + ("?" + urlencode(params) if params else "")
    response = requests.post(deauth_url)
    if response.status_code == 200:
        db.session.delete(current_user.strava_access_token[0])
        db.session.delete(current_user.strava_refresh_token[0])
        current_user.strava_athlete_id = None
        db.session.commit()

        flash('Strava deauthorisation successful!')
    if response.status_code == 401:
        flash('Strava deauthorisation not authorised')
    return redirect(url_for('main.user_profile'))


@bp.route('/token_exchange')
def token_exchange():
    code = request.args['code']
    client_id = current_app.config['STRAVA_CLIENT_ID']
    client_secret = current_app.config['STRAVA_CLIENT_SECRET']
    post_data = {'client_id': client_id, 'client_secret': client_secret, 'code': code, 'grant_type': 'authorization_code'}
    response = requests.post('https://www.strava.com/api/v3/oauth/token', json=post_data)
    response = response.json()
    expires_at = response['expires_at']
    refresh_token = response['refresh_token']
    access_token = response['access_token']
    athlete_id = response['athlete']['id']

    if db.session.execute(db.Select(User).filter_by(strava_athlete_id=athlete_id)).first():
        flash('This Strava athlete is already in our database!')
        return redirect(url_for('main.user_profile'))

    if current_user.strava_athlete_id is not None:
        flash('This Strava athlete is already in our database!')
        return redirect(url_for('main.user_profile'))
    
    current_user.strava_athlete_id = athlete_id

    strava_access_token = StravaAccessToken(
        athlete_id=athlete_id,
        access_token=access_token,
        expires_at=expires_at
    )

    db.session.add(strava_access_token)

    strava_refresh_token = StravaRefreshToken(
        athlete_id=athlete_id,
        refresh_token=refresh_token
    )    
    db.session.add(strava_refresh_token)

    db.session.commit()
    flash('Strava account linked!')
    return redirect(url_for('main.user_profile'))
    
