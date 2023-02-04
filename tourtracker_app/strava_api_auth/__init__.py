from flask import Blueprint

bp = Blueprint('strava_api_auth', __name__, template_folder='templates')

from tourtracker_app.strava_api_auth import routes # noqa F401