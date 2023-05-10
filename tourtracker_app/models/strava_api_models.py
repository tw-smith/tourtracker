
from tourtracker_app import db
import time
import requests
from tourtracker_app.strava_api_auth.strava_api_utilities import handle_strava_api_response
from flask import current_app


class StravaAccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('user.strava_athlete_id'), index=True, unique=True)
    access_token = db.Column(db.String(50), index=True)
    expires_at = db.Column(db.Integer, index=True)

    def check_token_valid(self):
        if self.expires_at < int(time.time()):
            return False
        else:
            return True

    def refresh_access_token(self, refresh_token):
        client_id = current_app.config['STRAVA_CLIENT_ID']
        client_secret = current_app.config['STRAVA_CLIENT_SECRET']
        post_data = {'client_id': client_id, 'client_secret': client_secret, 'refresh_token': refresh_token.refresh_token, 'grant_type': 'refresh_token'}
        response = handle_strava_api_response(requests.post('https://www.strava.com/api/v3/oauth/token', json=post_data))
        self.access_token = response['access_token']
        self.expires_at = response['expires_at']
        refresh_token.refresh_token = response['refresh_token']

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StravaRefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('user.strava_athlete_id'), index=True, unique=True)
    refresh_token = db.Column(db.String(50), index=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
   

class StravaWebhookSubscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, index=True, unique=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
