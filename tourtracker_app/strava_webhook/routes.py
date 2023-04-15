from tourtracker_app.strava_webhook import bp
import requests
from flask import current_app, request, make_response
from urllib.parse import urlencode


@bp.route('/', methods=['GET', 'POST'])
def webhook_response():
    if request.method == 'GET':
        challenge = request.args.get('hub.challenge')
        verify_token = request.args.get('hub.verify_token')
        if verify_token is not current_app.config['STRAVA_WEBHOOK_VERIFY_TOKEN']:
            return 'error'
        else:
            body = {'hub.challenge': challenge}
            return make_response(body, 200)