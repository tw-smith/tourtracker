from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    email = StringField('Username',
                        validators=[DataRequired()],
                        render_kw={"placeholder": "Email"})

    password = PasswordField('Password',
                             validators=[DataRequired()],
                             render_kw={"placeholder": "Password"})

    submit = SubmitField('Log In')


class SignupForm(FlaskForm):
    email = EmailField('Email',
                       validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "Email address"})

    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8), EqualTo('repeat_pw')],
                             render_kw={"placeholder": "Password"})

    repeat_pw = PasswordField('Repeat Password',
                              validators=[DataRequired(), Length(min=8)],
                              render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField('Sign Up')


class PasswordResetRequestForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()],
                       render_kw={"placeholder": "Email Address"})

    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8), EqualTo('repeat_pw')],
                             render_kw={"placeholder": "New Password"})

    repeat_pw = PasswordField('Repeat Password',
                              validators=[DataRequired(), Length(min=8)],
                              render_kw={"placeholder": "Confirm New Password"})

    submit = SubmitField('Reset Password')
