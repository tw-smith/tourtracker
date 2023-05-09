from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, StringField, BooleanField
from wtforms.validators import DataRequired


class TourForm(FlaskForm):
    tour_name = StringField('Site Name', validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    # auto_refresh = BooleanField('On Tour')
    submit = SubmitField('Create Tour')
