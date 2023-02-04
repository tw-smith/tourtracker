from tourtracker_app import db
import time


class StravaAccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('user.strava_athlete_id'), index=True, unique=True)
    access_token = db.Column(db.String(50), index=True)
    expires_at = db.Column(db.Integer, index=True)

    def check_token_valid(self):
        if self.expires_at > int(time.time()):
            return False
        else:
            return True



    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class StravaRefreshToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('user.strava_athlete_id'), index=True, unique=True)
    refresh_token = db.Column(db.String(50), index=True)


    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
