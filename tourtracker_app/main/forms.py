from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, StringField, URLField, BooleanField
from wtforms.validators import DataRequired, URL


class StravaActivitiesForm(FlaskForm):
    start_date = DateField('From', validators=[DataRequired()])
    end_date = DateField('To', validators=[DataRequired()])
    submit = SubmitField('Submit')

class TourForm(FlaskForm):
    tour_name = StringField('Site Name', validators=[DataRequired()])
    site_url = URLField('Site Url', validators=[DataRequired(), URL(require_tld=False)])
    start_date = DateField('Start Date', validators=[DataRequired()])
    auto_refresh = BooleanField('On Tour')
    end_date = DateField('End Date')
    submit = SubmitField('Link Site')