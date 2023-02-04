from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField
from wtforms.validators import DataRequired


class StravaActivitiesForm(FlaskForm):
    start_date = DateField('From', validators=[DataRequired()])
    end_date = DateField('To', validators=[DataRequired()])
    submit = SubmitField('Submit')
