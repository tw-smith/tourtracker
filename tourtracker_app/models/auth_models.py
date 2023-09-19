from tourtracker_app import db, jwt as jwt_extended
from flask import current_app
from argon2 import PasswordHasher, exceptions
import argon2
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
import uuid

ph = PasswordHasher()

@jwt_extended.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"] # TODO this means we will need to have the auth server uuid here
    user = db.session.execute(db.Select(User).filter_by(public_id=identity)).one_or_none()
    user = user[0]
    return user


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(50), unique=True)
    isadmin = db.Column(db.Boolean(1))
    strava_athlete_id = db.Column(db.Integer, unique=True, index=True)
    strava_access_token = db.relationship('StravaAccessToken', backref='user', lazy='dynamic')
    strava_refresh_token = db.relationship('StravaRefreshToken', backref='user', lazy='dynamic')
    tours = db.relationship('Tour', backref='user', lazy='dynamic')
    activities = db.relationship('TourActivities', backref='user', lazy='dynamic')
    

    def __init__(self, email, username, public_id):
        self.public_id = public_id
        self.isadmin = False
        self.email = email
        self.username = username
        self.strava_athlete_id = None

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

    # def create_token(self, expires_in=600):
    #     token = jwt.encode({
    #         'iss': current_app.config['JWT_ISSUER'],
    #         'iat': datetime.utcnow(),
    #         'exp': datetime.utcnow() + timedelta(minutes=15),
    #         'uuid': self.uuid,
    #     }, current_app.config['SECRET_KEY'],
    #         headers={
    #         'typ': 'JWT',
    #         'alg': 'HS256'
    #     }
    #     )
    #     print(token)
    #     return token

    @staticmethod
    def decode_token(token):
        try:
            token_payload = jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms='HS256')
        except ExpiredSignatureError:
            raise ExpiredSignatureError
        except JWTError:
            raise JWTError

    # @staticmethod
    # def decode_token(token):
    #     try:
    #         return jwt.decode(
    #             token,
    #             options={'require': ['exp', 'iss']},
    #             key=current_app.config['SECRET_KEY'],
    #             algorithms='HS256',
    #             issuer=current_app.config['JWT_ISSUER'])
    #     except jwt.exceptions.ExpiredSignatureError:
    #         raise jwt.exceptions.ExpiredSignatureError
    #     except jwt.exceptions.InvalidAlgorithmError:
    #         raise jwt.exceptions.InvalidAlgorithmError
    #     except jwt.exceptions.InvalidIssuedAtError:
    #         raise jwt.exceptions.InvalidIssuedAtError
    #     except jwt.exceptions.InvalidSignatureError:
    #         raise jwt.exceptions.InvalidSignatureError
    #     except jwt.exceptions.MissingRequiredClaimError:
    #         raise jwt.exceptions.MissingRequiredClaimError
    #     except jwt.exceptions.DecodeError:
    #         raise jwt.exceptions.DecodeError
        
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

    def __repr__(self):
        return '<User {}>'.format(self.email)

    
