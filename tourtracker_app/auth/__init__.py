from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

from tourtracker_app.auth import routes # noqa F401