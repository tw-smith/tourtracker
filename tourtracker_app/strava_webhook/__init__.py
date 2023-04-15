from flask import Blueprint

bp = Blueprint('strava_webhook', __name__, template_folder='templates')

from tourtracker_app.strava_webhook import routes # noqa F401