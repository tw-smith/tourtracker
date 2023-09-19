from tourtracker_app import db
import uuid
from dataclasses import dataclass


class Tour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tour_uuid = db.Column(db.String(50), unique=True)
    tour_name = db.Column(db.String(50))
    start_date = db.Column(db.Integer)
    end_date = db.Column(db.Integer)
    # auto_refresh = db.Column(db.Boolean(1))
    #refresh_interval = db.Column(db.Integer)
    #last_refresh = db.Column(db.Integer)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), index=True)
    tour_activities = db.relationship('TourActivities', backref='tour', lazy='dynamic', cascade='all, delete')

    def __init__(self, tour_name, start_date, end_date, user_id):
        self.tour_uuid = str(uuid.uuid4())
        self.tour_name = tour_name
        self.start_date = start_date
        self.end_date = end_date
        # self.auto_refresh = auto_refresh,
        self.user_id = user_id

    def __repr__(self):
        return '<Tour {}>'.format(self.tour_name)

#TODO also initialise properly

@dataclass
class TourActivities(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    # https://stackoverflow.com/questions/12297156/fastest-way-to-insert-object-if-it-doesnt-exist-with-sqlalchemy
    strava_activity_id = db.Column(db.Integer, primary_key=True)
    activity_name = db.Column(db.String(100))
    activity_date = db.Column(db.Integer)
    summary_polyline = db.Column(db.String(100))
    parent_tour = db.Column(db.String(50), db.ForeignKey('tour.tour_uuid'), primary_key=True)
    user_id = db.Column(db.String(50), db.ForeignKey('user.public_id'), index=True)

    def __init__(self, strava_activity_id, activity_name, activity_date, summary_polyline, parent_tour, user_id):
        self.strava_activity_id = strava_activity_id
        self.activity_name = activity_name
        self.activity_date = activity_date
        self.summary_polyline = summary_polyline
        self.parent_tour = parent_tour
        self.user_id = user_id

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return '<TourActivities {}>'.format(self.activity_name)