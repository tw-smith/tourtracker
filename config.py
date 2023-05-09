import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    APP_TITLE = 'Tour Tracker'
    JWT_ISSUER = 'http://tourtracker.tw-smith.me'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    STRAVA_SCOPE = os.environ.get('STRAVA_SCOPE')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/tour_tracker_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER='smtp.sendgrid.net'
    MAIL_PORT=587
    MAIL_USE_TLS=True
    MAIL_USERNAME='apikey'
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    STRAVA_WEBHOOK_VERIFY_TOKEN = os.environ.get('STRAVA_WEBHOOK_VERIFY_TOKEN')
    STRAVA_WEBHOOK_BASE_URL = 'https://www.strava.com/api/v3/push_subscriptions'


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('PROD_SECRET_KEY')
    STRAVA_REDIRECT_URL = 'https://tourtracker.tw-smith.me/strava/token_exchange'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/tour_tracker_prod.db')
    STRAVA_CLIENT_ID = os.environ.get('PROD_STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.environ.get('PROD_STRAVA_CLIENT_SECRET')
    STRAVA_WEBHOOK_CALLBACK_URL = 'http://'


class DevelopmentConfig(Config):
    SECRET_KEY = os.environ.get('DEV_SECRET_KEY')
    STRAVA_REDIRECT_URL = 'http://127.0.0.1:5000/strava/token_exchange'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db/tour_tracker_dev.db')
    STRAVA_CLIENT_ID = os.environ.get('DEV_STRAVA_CLIENT_ID')
    STRAVA_CLIENT_SECRET = os.environ.get('DEV_STRAVA_CLIENT_SECRET')
