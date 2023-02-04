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

@bp.route('/refresh_tokens')
def refresh_tokens():
    response = strava_token_request('refresh_token', refresh_token=current_user.strava_refresh_token[0].refresh_token)
    strava_access_token = db.session.execute(db.Select(StravaAccessToken).filter_by(athlete_id=current_user.strava_athlete_id)).first()
    strava_refresh_token = db.session.execute(db.Select(StravaRefreshToken).filter_by(athlete_id=current_user.strava_athlete_id)).first()
    strava_access_token[0].access_token = response['access_token']
    strava_access_token[0].expires_at = response['expires_at']
    strava_refresh_token[0].refresh_token = response['refresh_token']
    print(strava_refresh_token[0].refresh_token)
    db.session.commit()
    return redirect(url_for('main.user_profile'))



@bp.route('/strava')
def strava_auth():
    strava_base_url = 'https://www.strava.com/oauth/authorize'
    params = dict(client_id=current_app.config['STRAVA_CLIENT_ID'], response_type='code', redirect_uri=current_app.config['STRAVA_REDIRECT_URL'], scope=current_app.config['STRAVA_SCOPE'])
    redirect_url = strava_base_url + ("?" + urlencode(params) if params else "")
    return redirect(redirect_url)


@bp.route('/token_exchange')
def token_exchange():
    code = request.args['code']
    response = strava_token_request('authorization_code', code=code)
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
    
