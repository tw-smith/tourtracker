from flask_mail import Message
from tourtracker_app import mail
from threading import Thread
from flask import current_app


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    if current_app.config['TESTING'] is True:
        print(msg.body)
    elif current_app.debug:
        print(msg.body)
    else:
        Thread(target=send_async_email,
               args=(current_app._get_current_object(), msg)).start()