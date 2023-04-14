from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# from tourtracker_app.models.auth_models import User
# from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken


# AUTH
from flask_mail import Mail, Message
from flask_login import LoginManager

import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()
migrate = Migrate()

#AUTH
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)



    db.init_app(app)
    migrate.init_app(app, db)

    from tourtracker_app.models.tour_models import Tour, TourActivities
    #from tourtracker_app.strava_api_auth.error_handlers import StravaBadRequestException
    from tourtracker_app.strava_api_auth.strava_api_utilities import handle_strava_api_response
    

    
    from tourtracker_app.models.auth_models import User
    #from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
    

    # AUTH
    login.init_app(app)
    mail.init_app(app)

    from tourtracker_app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from tourtracker_app.strava_api_auth import bp as strava_api_auth_bp
    app.register_blueprint(strava_api_auth_bp, url_prefix='/strava')

    #AUTH
    from tourtracker_app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/arcade.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter
        (logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Arcade startup')

    return app
