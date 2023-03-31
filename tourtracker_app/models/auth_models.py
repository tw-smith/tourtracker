from tourtracker_app import db, login
from flask import current_app
from argon2 import PasswordHasher, exceptions
import argon2
import jwt
from datetime import datetime, timedelta
import uuid
from tourtracker_app.models.strava_api_models import StravaAccessToken

ph = PasswordHasher()


@login.user_loader
def load_user(email):
    user = db.session.execute(db.Select(User).filter_by(email=email)).first()
    if user:
        return user[0]
    return None


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))
    verified = db.Column(db.Boolean(1))
    strava_athlete_id = db.Column(db.Integer, unique=True, index=True)
    strava_access_token = db.relationship('StravaAccessToken', backref='user', lazy='dynamic')
    strava_refresh_token = db.relationship('StravaRefreshToken', backref='user', lazy='dynamic')
    origin_site = db.relationship('OriginSite', backref='user', lazy='dynamic')
    

    def __init__(self, email, password):
        self.uuid = str(uuid.uuid4())
        self.email = email
        self.password_hash = ph.hash(password)
        self.verified = False
        self.strava_athlete_id = None
        # self.strava_access_token = None
        # self.strava_refresh_token = None

    def set_password(self, password):
        self.password_hash = ph.hash(password)

    def check_password(self, password):
        try:
            check = ph.verify(self.password_hash, password)
        except argon2.exceptions.VerificationError:
            raise argon2.exceptions.VerificationError

        if ph.check_needs_rehash(self.password_hash):
            self.password_hash = ph.hash(password)
            db.session.commit()

        return check

    def create_token(self, expires_in=600):
        token = jwt.encode({
            'iss': current_app.config['JWT_ISSUER'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=15),
            'uuid': self.uuid,
        }, current_app.config['SECRET_KEY'],
            headers={
            'typ': 'JWT',
            'alg': 'HS256'
        }
        )
        print(token)
        return token

    @staticmethod
    def decode_token(token):
        try:
            return jwt.decode(
                token,
                options={'require': ['exp', 'iss']},
                key=current_app.config['SECRET_KEY'],
                algorithms='HS256',
                issuer=current_app.config['JWT_ISSUER'])
        except jwt.exceptions.ExpiredSignatureError:
            raise jwt.exceptions.ExpiredSignatureError
        except jwt.exceptions.InvalidAlgorithmError:
            raise jwt.exceptions.InvalidAlgorithmError
        except jwt.exceptions.InvalidIssuedAtError:
            raise jwt.exceptions.InvalidIssuedAtError
        except jwt.exceptions.InvalidSignatureError:
            raise jwt.exceptions.InvalidSignatureError
        except jwt.exceptions.MissingRequiredClaimError:
            raise jwt.exceptions.MissingRequiredClaimError
        except jwt.exceptions.DecodeError:
            raise jwt.exceptions.DecodeError
        
    @staticmethod
    def verify_user_verification_token(token):
        try:
            uuid = User.decode_token(token)
        except:
            print('jwt decode error')
            raise
        uuid = uuid['uuid']
        print('decoded uuid is ' + uuid)
        return db.session.execute(db.select(User).filter_by(uuid=uuid)).first()

    # For Flask-Login

    @property
    def is_active(self):
        return self.verified
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email


    def __repr__(self):
        return '<User {}>'.format(self.email)

# TODO initialisation values for this
class OriginSite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(50))
    site_url = db.Column(db.String(50), unique=True)
    start_date = db.Column(db.Integer)
    end_date = db.Column(db.Integer)
    refresh_interval = db.Column(db.Integer)
    last_refresh = db.Column(db.Integer)
    user = db.Column(db.String(50), db.ForeignKey('user.uuid'), index=True, unique=True)
    user_activities = db.relationship('UserActivities', backref='originsite', lazy='dynamic')

    def __repr__(self):
        return '<OriginSite {}>'.format(self.site_name)

#TODO also initialise properly
# FIXME db upgrade error ValueError: Constraint must have a name
class UserActivities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    strava_activity_id = db.Column(db.Integer)
    activity_name = db.Column(db.String(100))
    activity_date = db.Column(db.Integer)
    summary_polyline = db.Column(db.String(100))
    origin_site = db.Column(db.String(50), db.ForeignKey('origin_site.site_url'))

    def __repr__(self):
        return '<UserActivities {}>'.format(self.activity_name)

    
