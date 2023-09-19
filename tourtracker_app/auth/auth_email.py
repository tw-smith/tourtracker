from flask import render_template, current_app
from tourtracker_app.email import send_email


def send_user_validation_email(user):
    token = user.create_token()
    send_email(current_app.config['APP_TITLE'] + ': Verify your email',
               sender=current_app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.username],
               text_body=render_template('email/user_validation.txt', user=user, token=token),
               html_body=render_template('email/user_validation.html', user=user, token=token))


def send_password_reset_email(user):
    token = user.create_token()
    send_email(current_app.config['APP_TITLE'] + ': Password reset',
               sender=current_app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.username],
               text_body=render_template('email/password_reset.txt', user=user, token=token),
               html_body=render_template('email/password_reset.html', user=user, token=token))