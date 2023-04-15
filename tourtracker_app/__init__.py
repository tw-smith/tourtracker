from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
from urllib.parse import urlencode
# from tourtracker_app.models.auth_models import User
# from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken


# AUTH
from flask_mail import Mail, Message
from flask_login import LoginManager

import logging
from logging.handlers import RotatingFileHandler
import os
import sys

db = SQLAlchemy()
migrate = Migrate()

#AUTH
login = LoginManager()
login.login_view = 'auth.login'
mail = Mail()

def init_webhooks(base_url):
    # Update inbound traffic via APIs to use the public-facing ngrok URL
    pass


async def create_webhook_subscription(app):
    params = dict(client_id=app.config['STRAVA_CLIENT_ID'], 
                  client_secret=app.config['STRAVA_CLIENT_SECRET'],
                  callback_url=app.config['STRAVA_WEBHOOK_CALLBACK_URL'], 
                  verify_token=app.config['STRAVA_WEBHOOK_VERIFY_TOKEN'])
    base_url = 'https://www.strava.com/api/v3/push_subscriptions'
    post_url = base_url + ("?" + urlencode(params))
    response = await requests.post(post_url)
    print('response')
    return response



def create_app(config_class=Config):
    app = Flask(__name__)
    if app.debug:
        app.config.from_object(DevelopmentConfig)
        from pyngrok import ngrok

        # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        app.config["BASE_URL"] = public_url
        app.config["STRAVA_WEBHOOK_CALLBACK_URL"] = public_url + '/strava/webhook'
        init_webhooks(public_url)

    else:
        app.config.from_object(ProductionConfig)
    db.init_app(app)
    migrate.init_app(app, db)

    from tourtracker_app.models.tour_models import Tour, TourActivities
    from tourtracker_app.strava_api_auth.strava_api_utilities import handle_strava_api_response
    from tourtracker_app.models.auth_models import User

    

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

    from tourtracker_app.strava_webhook import bp as strava_webhook_bp
    app.register_blueprint(strava_webhook_bp, url_prefix='/strava_webhook')

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

    response = create_webhook_subscription(app)
    print(response)
    return app
