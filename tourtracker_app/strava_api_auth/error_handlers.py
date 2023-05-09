from tourtracker_app.strava_api_auth import bp
from tourtracker_app import db
from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
from flask_login import current_user
from flask import flash, redirect, url_for


class StravaBadRequestException(Exception):
    def __init__(self, strava_message, *args):
        super().__init__(args)
        self.strava_message = strava_message

    def __str__(self):
        return f'Strava error message:{self.strava_message}'


@bp.errorhandler(StravaBadRequestException)
def handle_strava_bad_request(e):
    print(e)
    access_token = db.session.execute(db.select(StravaAccessToken).filter_by(athlete_id=current_user.strava_athlete_id)).first()
    refresh_token = db.session.execute(db.select(StravaRefreshToken).filter_by(athlete_id=current_user.strava_athlete_ud)).first()
    db.session.delete(access_token[0])
    db.session.delete(refresh_token[0])
    current_user.strava_athlete_id = None
    db.session.commit()
    flash(e.strava_message)
    flash('Strava reauth required')
    return redirect(url_for('main.user_profile'))
