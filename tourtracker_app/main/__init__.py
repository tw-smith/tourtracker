from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

from tourtracker_app.main import routes # noqa F401