# import datetime
from datetime import datetime, timedelta, MINYEAR, MAXYEAR
import os

os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

import unittest
from unittest.mock import Mock, patch
from flask import current_app
from flask_login import current_user
from requests.models import Response
from tourtracker_app import create_app, db
from tourtracker_app.models.auth_models import User
from tourtracker_app.models.tour_models import Tour, TourActivities
from tourtracker_app.email import send_email
from tourtracker_app.strava_api_auth.strava_api_utilities import get_strava_activities, get_individual_strava_activity, \
    handle_strava_api_response, strava_request_header_prep
from tourtracker_app.strava_api_auth.error_handlers import StravaBadRequestException
from test_utilities import login_helper, logout_helper


class TestTourTracker(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app.config['TESTING'] = True
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.drop_all()
        db.create_all()
        self.populate_db()
        self.base_user = db.session.execute(db.select(User).filter_by(id=1)).first()
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.appctx = None
        self.client = None

    def populate_db(self):
        user = User(
            email='test@test.com',
            password='test_password',
        )
        user.verified = True
        db.session.add(user)
        db.session.commit()

    def login_helper(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password,
        }, follow_redirects=True)

    def logout_helper(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    def create_mock_response(self, response_body, status_code):
        r = Mock(spec=Response)
        r.json.return_value = response_body
        r.status_code = status_code
        if status_code < 400:
            r.ok = True
        else:
            r.ok = False
        return r

    def return_example_strava_activities(self, one_or_multiple):
        if one_or_multiple == 'one':
            return [
            {
                "resource_state": 2,
                "athlete": {
                    "id": 134815,
                    "resource_state": 1
                },
                "name": "Happy Friday",
                "distance": 24931.4,
                "moving_time": 4500,
                "elapsed_time": 4500,
                "total_elevation_gain": 0,
                "type": "Ride",
                "sport_type": "MountainBikeRide",
                "workout_type": None,
                "id": 154504250376823,
                "start_date": "2018-05-02T12:15:09Z",
                "start_date_local": "2018-05-02T05:15:09Z",
                "timezone": "(GMT-08:00) America/Los_Angeles",
                "utc_offset": -25200,
                "map": {
                    "id": "a12345678987654321",
                    "summary_polyline": 'iiv_Gbk|wOrnh@o{p@bb_Ahg`@_hZr{ZwcbA~}[',
                    "resource_state": 2
                },
                "trainer": False,
                "commute": False,
                "manual": False,
                "private": False,
                "flagged": False,
                "max_speed": 11,
            },
        ]

        if one_or_multiple == 'multiple':
            return [
            {
                "resource_state": 2,
                "athlete": {
                    "id": 134815,
                    "resource_state": 1
                },
                "name": "Happy Friday",
                "distance": 24931.4,
                "moving_time": 4500,
                "elapsed_time": 4500,
                "total_elevation_gain": 0,
                "type": "Ride",
                "sport_type": "MountainBikeRide",
                "workout_type": None,
                "id": 154504250376823,
                "start_date": "2018-05-02T12:15:09Z",
                "start_date_local": "2018-05-02T05:15:09Z",
                "timezone": "(GMT-08:00) America/Los_Angeles",
                "utc_offset": -25200,
                "map": {
                    "id": "a12345678987654321",
                    "summary_polyline": 'iiv_Gbk|wOrnh@o{p@bb_Ahg`@_hZr{ZwcbA~}[',
                    "resource_state": 2
                },
                "trainer": False,
                "commute": False,
                "manual": False,
                "private": False,
                "flagged": False,
                "max_speed": 11,
            },
            {
                "resource_state": 2,
                "athlete": {
                    "id": 167560,
                    "resource_state": 1
                },
                "name": "Bondcliff",
                "distance": 23676.5,
                "moving_time": 5400,
                "elapsed_time": 5400,
                "total_elevation_gain": 0,
                "type": "Ride",
                "sport_type": "MountainBikeRide",
                "workout_type": None,
                "id": 1234567809,
                "start_date": "2018-04-30T12:35:51Z",
                "start_date_local": "2018-04-30T05:35:51Z",
                "timezone": "(GMT-08:00) America/Los_Angeles",
                "utc_offset": -25200,
                "map": {
                    "id": "a12345689",
                    "summary_polyline": 'iiv_Gbk|wOrnh@o{p@bb_Ahg`@_hZr{ZwcbA~}[',
                    "resource_state": 2
                },
                "trainer": False,
                "commute": False,
                "manual": False,
                "private": False,
                "flagged": False,
                "max_speed": 8.8,
            },
            {
                "resource_state": 2,
                "athlete": {
                    "id": 167560,
                    "resource_state": 1
                },
                "name": "NotAllowed",
                "distance": 23676.5,
                "moving_time": 5400,
                "elapsed_time": 5400,
                "total_elevation_gain": 0,
                "type": "Handcycle",
                "sport_type": "MountainBikeRide",
                "workout_type": None,
                "id": 1234567810,
                "start_date": "2018-04-30T12:35:51Z",
                "start_date_local": "2018-04-30T05:35:51Z",
                "timezone": "(GMT-08:00) America/Los_Angeles",
                "utc_offset": -25200,
                "map": {
                    "id": "a12345689",
                    "summary_polyline": 'iiv_Gbk|wOrnh@o{p@bb_Ahg`@_hZr{ZwcbA~}[',
                    "resource_state": 2
                },
                "trainer": False,
                "commute": False,
                "manual": False,
                "private": False,
                "flagged": False,
                "max_speed": 8.8,
            }
        ]

    def strava_authenticate_user(self):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        self.base_user[0].strava_athlete_id = 1002
        expires_at = int(round((datetime.now() + timedelta(days=3)).timestamp()))
        strava_access_token = StravaAccessToken(
            athlete_id=1002,
            access_token='dummy_access_token',
            expires_at=expires_at
        )
        db.session.add(strava_access_token)
        db.session.commit()

    def create_dummy_tour(self, one_or_multiple):
        start_date = int(round((datetime.now() - timedelta(days=3)).timestamp()))
        end_date = int(round((datetime.now() + timedelta(days=3)).timestamp()))
        test_tour = Tour('test_tour', start_date, end_date, self.base_user[0].uuid)
        db.session.add(test_tour)
        activities = self.return_example_strava_activities(one_or_multiple)
        for activity in activities:
            new_activity = TourActivities(
                activity['id'],
                activity['name'],
                activity['start_date_local'],
                activity['map']['summary_polyline'],
                test_tour.tour_uuid,
                self.base_user[0].uuid
            )
            db.session.add(new_activity)
        db.session.commit()
        return db.session.execute(db.select(Tour).filter_by(id=1)).first()


    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    # Would be nice to use PyTest parametrize here but it is not compatible with this
    # unittest.TestCase approach. https://docs.pytest.org/en/6.2.x/unittest.html
    # TODO: implement @pytest.mark.parametrize if we ever refactor this to full PyTest
    # Or could use this: https://github.com/wolever/parameterized

    #################################
    ########## AUTH TESTS ###########
    #################################
    def test_auth_redirects(self):
        status_code = 200
        auth_redirect_url = '/auth/login'
        response = self.client.get('/profile', follow_redirects=True)
        assert response.status_code == status_code
        assert response.request.path == auth_redirect_url
        response = self.client.get('/createtour', follow_redirects=True)
        assert response.status_code == status_code
        assert response.request.path == auth_redirect_url
        response = self.client.get('/tour/dummyuuid', follow_redirects=True)
        assert response.status_code == status_code
        assert response.request.path == auth_redirect_url
        response = self.client.get('/tour/refresh/dummyuuid', follow_redirects=True)
        assert response.status_code == status_code
        assert response.request.path == auth_redirect_url
        response = self.client.get('/deletetour/dummyuuid', follow_redirects=True)
        assert response.status_code == status_code
        assert response.request.path == auth_redirect_url

    def test_login(self):
        response = self.login_helper('test@test.com', 'test_password')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'test@test.com' in html
        self.logout_helper()

    def test_logout(self):
        self.login_helper('test@test.com', 'test_password')
        response = self.client.get('auth/logout', follow_redirects=True)
        assert response.request.path == '/index'
        # TODO is there a way to check we are ACTUALLY logged out?

    def test_login_incorrect_password(self):
        response = self.login_helper('test@test.com', 'wrong_password')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Invalid username or password' in html
        assert response.request.path == '/auth/login'

    def test_login_no_such_user(self):
        response = self.login_helper('nouser@test.com', 'test_password')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Invalid username or password' in html
        assert response.request.path == '/auth/login'

    def test_login_non_verified_user(self):
        self.base_user[0].verified = False
        db.session.commit()
        response = self.login_helper('test@test.com', 'test_password')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Please verify your email address' in html
        assert response.request.path == '/auth/login'

    def test_signup_form(self):
        response = self.client.get('/auth/signup')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert 'name="repeat_pw"' in html
        assert 'name="submit"' in html

    def test_jwt_encode_decode(self):
        token = self.base_user[0].create_token()
        decoded_token = self.base_user[0].decode_token(token)
        assert decoded_token['uuid'] == self.base_user[0].uuid
        assert decoded_token['iss'] == self.app.config['JWT_ISSUER']

    def test_register_email_validation(self):
        self.base_user[0].verified = False
        db.session.commit()
        self.assertFalse(self.base_user[0].verified)
        token = self.base_user[0].create_token()
        response = self.client.get('/auth/verify/' + token, follow_redirects=True)
        html = response.data.decode()
        assert response.status_code == 200
        assert 'Signup successful' in html
        assert response.request.path == '/auth/login'
        assert self.base_user[0].verified is True

    def test_register_email_validation_bad_token(self):
        self.base_user[0].verified = False
        db.session.commit()
        self.assertFalse(self.base_user[0].verified)
        bad_token = 'bad_token'
        response = self.client.get('/auth/verify/' + bad_token, follow_redirects=True)
        html = response.data.decode()
        assert response.status_code == 200
        assert 'Verification error' in html
        assert response.request.path == '/auth/signup'
        assert self.base_user[0].verified is False

    def test_register_user(self):
        data = {
            'email': 'testreg@test.com',
            'password': 'test_password',
            'repeat_pw': 'test_password',
        }
        response = self.client.post('/auth/signup', data=data, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Please check your email for a verification link' in html

    def test_register_user_already_exists(self):
        data = {
            'email': self.base_user[0].email,
            'password': 'test_password',
            'repeat_pw': 'test_password',
        }
        response = self.client.post('/auth/signup', data=data, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert response.request.path == '/auth/login'
        assert 'Account already exists' in html

    def test_register_user_mismatched_passwords(self):
        data = {
            'email': 'testreg@test.com',
            'password': 'test_password1',
            'repeat_pw': 'test_password2',
        }
        response = self.client.post('/auth/signup', data=data, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Field must be equal to repeat_pw' in html
        # TODO this is an awful error message to show the user

    def test_register_user_password_length(self):
        data = {
            'email': 'testreg@test.com',
            'password': '123',
            'repeat_pw': '123',
        }
        response = self.client.post('/auth/signup', data=data, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Field must be at least 8 characters long' in html

    def test_request_password_reset(self):
        response = self.client.get('/auth/requestresetpassword', follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'name="email"' in html
        assert 'name="submit"' in html

        response = self.client.post('/auth/requestresetpassword', data={
            'email': 'blah@blah.com'
        }, follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'Password reset link sent' in html
        assert response.request.path == '/auth/login'

    def test_reset_password(self):
        token = self.base_user[0].create_token()
        response = self.client.get('/auth/resetpassword/' + token, follow_redirects=True)
        assert response.status_code == 200
        html = response.data.decode()
        assert 'name="submit"' in html
        assert 'name="password"' in html
        assert 'name="repeat_pw' in html

        post_response = self.client.post('/auth/resetpassword/' + token, data={
            'password': 'new_password',
            'repeat_pw': 'new_password'
        }, follow_redirects=True)
        assert post_response.status_code == 200
        assert post_response.request.path == '/auth/login'
        assert self.base_user[0].check_password('new_password') is True
        post_html = post_response.data.decode()
        assert 'Password reset. Please log in' in post_html

    def test_admin_user_profile_page(self):
        self.base_user[0].isadmin = True
        db.session.commit()
        self.login_helper(self.base_user[0].email, 'test_password')
        response = self.client.get('/index', follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'Webhook Admin' in html
        self.logout_helper()

    def test_tour_detail_page(self):
        self.login_helper('test@test.com', 'test_password')
        tour_db_object = self.create_dummy_tour('multiple')
        tour_uuid = tour_db_object[0].tour_uuid
        tour_name_from_db = tour_db_object[0].tour_name
        response = self.client.get('/tour/' + tour_uuid)
        self.assertIn(tour_name_from_db, response.data.decode())
        self.assertIn('Refresh', response.data.decode())
        self.assertIn('User Profile', response.data.decode())
        self.assertIn('Delete Tour', response.data.decode())
        self.assertIn('<div id="map">', response.data.decode())
        self.assertIn('Tour Detail', response.data.decode())
        self.assertIn('src="https://maps.googleapis.com/maps/api', response.data.decode())
        self.logout_helper()

    def test_tour_embed_page(self):
        self.login_helper('test@test.com', 'test_password')
        tour_db_object = self.create_dummy_tour('multiple')
        tour_uuid = tour_db_object[0].tour_uuid
        response = self.client.get('/tour/embed/' + tour_uuid)
        self.assertIn('<div id="map">', response.data.decode())
        self.assertIn('src="https://maps.googleapis.com/maps/api', response.data.decode())
        self.logout_helper()

    def test_get_tour_data(self):
        tour_db_object = self.create_dummy_tour('multiple')
        tour_uuid = tour_db_object[0].tour_uuid
        response = self.client.get('/tour/data/' + tour_uuid)
        self.assertIn('points', response.data.decode())
        self.assertIn('Bondcliff', response.data.decode())
        self.assertIn('NotAllowed', response.data.decode())

    def test_delete_tour(self):
        self.login_helper('test@test.com', 'test_password')
        tour_db_object = self.create_dummy_tour('multiple')
        tour_uuid = tour_db_object[0].tour_uuid
        response = self.client.get('/deletetour/' + tour_uuid, follow_redirects=True)
        tour = db.session.execute(db.Select(Tour).filter_by(tour_uuid=tour_uuid)).first()
        tour_activities = db.session.execute(db.Select(TourActivities).filter_by(parent_tour=tour_uuid)).first()
        self.assertEqual(tour, None)
        self.assertEqual(tour_activities, None)
        self.assertEqual(response.request.path, '/profile')
        self.logout_helper()

    def test_delete_tour_wrong_user(self):
        tour_db_object = self.create_dummy_tour('multiple')
        tour_uuid = tour_db_object[0].tour_uuid
        wrong_user = User(
            email='new@test.com',
            password='test_password'
        )
        wrong_user.verified = True
        db.session.add(wrong_user)
        db.session.commit()
        self.login_helper('new@test.com', 'test_password')
        response = self.client.get('/deletetour/' + tour_uuid, follow_redirects=True)
        tour = db.session.execute(db.Select(Tour).filter_by(tour_uuid=tour_uuid)).first()
        tour_activities = db.session.execute(db.Select(TourActivities).filter_by(parent_tour=tour_uuid)).first()
        self.assertIsNotNone(tour)
        self.assertIsNotNone(tour_activities)
        self.assertEqual(response.request.path, '/profile')
        self.logout_helper()



    #################################
    ########## TEST STRAVA API UTILITIES ###########
    #################################
    def test_strava_auth(self):
        expected_url = 'https://www.strava.com/oauth/authorize?client_id=101417&response_type=code&redirect_uri=https%3A%2F%2Ftourtracker.tw-smith.me%2Fstrava%2Ftoken_exchange&scope=activity%3Aread'
        response = self.client.get('/strava/strava')
        assert response.location == expected_url

    @patch('tourtracker_app.strava_api_auth.routes.requests.post')
    def test_strava_token_exchange(self, mock_response):
        response_body = {
            'athlete': {
                'id': '1002'
            },
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'expires_at': '123456789'
        }
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.login_helper(self.base_user[0].email, 'test_password')
        response = self.client.get('/strava/token_exchange?code=dummycode', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.base_user[0].strava_athlete_id, 1002)
        self.assertEqual(self.base_user[0].strava_access_token[0].access_token, 'mock_access_token')
        self.assertEqual(self.base_user[0].strava_access_token[0].expires_at, 123456789)
        self.assertEqual(self.base_user[0].strava_refresh_token[0].refresh_token, 'mock_refresh_token')
        self.assertEqual(response.request.path, '/profile')
        self.logout_helper()

    @patch('tourtracker_app.strava_api_auth.routes.requests.post')
    def test_strava_token_exchange_existing_athlete(self, mock_response):
        response_body = {
            'athlete': {
                'id': '1003'
            },
            'access_token': 'mock_access_token',
            'refresh_token': 'mock_refresh_token',
            'expires_at': '123456789'
        }
        # https://stackoverflow.com/questions/40361308/create-a-functioning-response-object
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.base_user[0].strava_athlete_id = 1003
        db.session.commit()
        self.login_helper(self.base_user[0].email, 'test_password')
        response = self.client.get('/strava/token_exchange?code=dummycode', follow_redirects=True)
        self.assertIn('already in our database', response.data.decode())
        self.assertEqual(response.request.path, '/profile')
        self.logout_helper()

    @patch('tourtracker_app.strava_api_auth.routes.requests.post')
    def test_strava_deauth(self, mock_response):
        from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
        mock_response.return_value = self.create_mock_response('', 200)
        self.base_user[0].strava_athlete_id = 1002
        expires_at = int(round((datetime.now() + timedelta(days=3)).timestamp()))
        strava_access_token = StravaAccessToken(
            athlete_id=1002,
            access_token='dummy_access_token',
            expires_at=expires_at
        )
        db.session.add(strava_access_token)
        strava_refresh_token = StravaRefreshToken(
            athlete_id=1002,
            refresh_token='dummy_refresh_token'
        )
        db.session.add(strava_refresh_token)
        db.session.commit()
        self.assertEqual(self.base_user[0].strava_access_token[0].access_token, 'dummy_access_token')
        self.assertEqual(self.base_user[0].strava_refresh_token[0].refresh_token, 'dummy_refresh_token')
        self.login_helper(self.base_user[0].email, 'test_password')
        response = self.client.get('/strava/strava_deauth', follow_redirects=True)
        strava_access_token = db.session.execute(db.select(StravaAccessToken).filter_by(athlete_id=1002)).first()
        strava_refresh_token = db.session.execute(db.Select(StravaRefreshToken).filter_by(athlete_id=1002)).first()
        self.assertEqual(strava_access_token, None)
        self.assertEqual(strava_refresh_token, None)
        self.assertEqual(self.base_user[0].strava_athlete_id, None)
        self.assertEqual(response.request.path, '/profile')
        self.assertIn('Strava deauthorisation successful', response.data.decode())
        self.logout_helper()

    # Test tour CRUD functions
    def test_create_tour_get(self):
        self.base_user[0].strava_athlete_id = 1003
        db.session.commit()
        self.login_helper(self.base_user[0].email, 'test_password')
        response = self.client.get('/createtour', follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'name="tour_name"' in html
        assert 'name="start_date"' in html
        assert 'name="end_date"' in html
        assert 'name="submit"' in html
        self.logout_helper()

    @patch('tourtracker_app.strava_api_auth.strava_api_utilities.requests.get')
    def test_create_tour_post(self, mock_response):
        response_body = self.return_example_strava_activities('multiple')
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.strava_authenticate_user()
        self.login_helper(self.base_user[0].email, 'test_password')
        year = datetime.now().year
        month = datetime.now().month
        start_day = (datetime.now() - timedelta(days=3)).day
        end_day = (datetime.now() + timedelta(days=3)).day
        data = {
            'tour_name': 'test tour name',
            'start_date': str(year) + '-' + str(month) + '-' + str(start_day),
            'end_date': str(year) + '-' + str(month) + '-' + str(end_day),
        }
        response = self.client.post('/createtour', data=data, follow_redirects=True)
        tour = db.session.execute(db.Select(Tour).filter_by(user_id=self.base_user[0].uuid)).first()
        self.assertEqual(tour[0].tour_name, 'test tour name')
        self.assertEqual(response.request.path, '/tour/' + tour[0].tour_uuid)

    def test_create_tour_post_bad_form_entry(self):
        self.login_helper(self.base_user[0].email, 'test_password')
        data = {
            'tour_name': 'test tour name',
        }
        response = self.client.post('/createtour', data=data, follow_redirects=True)
        self.assertEqual(response.request.path, '/profile')
        self.assertIn('Site linking error!', response.data.decode())

    @patch('tourtracker_app.strava_api_auth.strava_api_utilities.requests.get')
    def test_refresh_tour(self, mock_response):
        self.strava_authenticate_user()
        self.login_helper(self.base_user[0].email, 'test_password')
        response_body = self.return_example_strava_activities('multiple')
        mock_response.return_value = self.create_mock_response(response_body, 200)
        tour_db_object = self.create_dummy_tour('one')
        self.client.get('/tour/refresh/' + tour_db_object[0].tour_uuid)
        tour_activities = db.session.execute(db.Select(TourActivities).filter_by(parent_tour=tour_db_object[0].tour_uuid)).all()
        self.assertEqual(len(tour_activities), 2)

    def test_handle_strava_api_response_ok(self):
        response_body = {
            'message': 'test response body'
        }
        mock_response = self.create_mock_response(response_body, 200)
        result = handle_strava_api_response(mock_response)
        self.assertEqual(result['message'], 'test response body')

    def test_handle_strava_api_response_bad_request(self):
        response_body = {
            'message': 'bad request'
        }
        mock_response = self.create_mock_response(response_body, 400)
        self.assertRaises(StravaBadRequestException, handle_strava_api_response, mock_response)
        mock_response = self.create_mock_response(response_body, 401)
        self.assertRaises(StravaBadRequestException, handle_strava_api_response, mock_response)
        mock_response = self.create_mock_response(response_body, 429)
        self.assertRaises(StravaBadRequestException, handle_strava_api_response, mock_response)

    def test_strava_request_header_prep(self):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        self.base_user[0].strava_athlete_id = 1002
        expires_at = int(round((datetime.now() + timedelta(days=3)).timestamp()))
        strava_access_token = StravaAccessToken(
            athlete_id=1002,
            access_token='dummy_access_token',
            expires_at=expires_at
        )
        db.session.add(strava_access_token)
        db.session.commit()
        headers = strava_request_header_prep(self.base_user[0])
        self.assertIn('Bearer ', headers['Authorization'])
        self.assertIn(strava_access_token.access_token, headers['Authorization'])

    @patch('tourtracker_app.strava_api_auth.strava_api_utilities.requests.get')
    def test_get_strava_activities(self, mock_response):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        response_body = self.return_example_strava_activities('multiple')
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.strava_authenticate_user()
        start_timestamp = int(round(datetime(year=1990, day=1, month=1).timestamp()))
        end_timestamp = int(round(datetime(year=2050, day=1, month=1).timestamp()))
        result = get_strava_activities(self.base_user[0], start_timestamp, end_timestamp)
        self.assertEqual(result[0]['activity_name'], 'Happy Friday')
        self.assertEqual(result[1]['activity_name'], 'Bondcliff')
        self.assertEqual(len(result), 2)  # Check handcycle activity skipped

    @patch('tourtracker_app.strava_api_auth.strava_api_utilities.requests.get')
    def test_get_individual_strava_activity(self, mock_response):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        response_body = self.return_example_strava_activities('one')
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.strava_authenticate_user()
        result = get_individual_strava_activity(self.base_user[0], 154504250376823)
        self.assertEqual(result[0]['name'], 'Happy Friday')

    # def test_create_tour(self):
    #     self.login_helper('strava@test.com', 'testtest')
    #     data = {
    #         'tour_name': 'Test Tour Name',
    #         'start_date': '1/5/23',
    #         'end_date': '5/5/23',
    #     }
    #     response = self.client.post('/createtour', data=data, follow_redirects=True)
    # TODO this is now going to call get_strava_activities and strava API so we need to mock response

    # Test Strava API models

    def test_check_strava_access_token_valid(self):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        valid_access_token = StravaAccessToken(
            athlete_id=1234,
            access_token='dummy_access_token',
            expires_at=int(round((datetime.now() + timedelta(days=3)).timestamp()))
        )
        expired_access_token = StravaAccessToken(
            athlete_id=1235,
            access_token='expired_dummy_access_token',
            expires_at=int(round((datetime.now() - timedelta(days=3)).timestamp()))
        )
        self.assertTrue(valid_access_token.check_token_valid())
        self.assertFalse(expired_access_token.check_token_valid())

    @patch('tourtracker_app.models.strava_api_models.requests.post')
    def test_refresh_strava_access_token(self, mock_response):
        from tourtracker_app.models.strava_api_models import StravaAccessToken, StravaRefreshToken
        response_body = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_at': str(int(round((datetime.now() + timedelta(days=3)).timestamp())))
        }
        mock_response.return_value = self.create_mock_response(response_body, 200)
        self.base_user[0].strava_athlete_id = 1002
        access_token = StravaAccessToken(
            athlete_id=1002,
            access_token='expired_dummy_access_token',
            expires_at=int(round((datetime.now() - timedelta(days=3)).timestamp()))
        )
        refresh_token = StravaRefreshToken(
            athlete_id=1002,
            refresh_token='refresh_token'
        )
        db.session.add(access_token)
        db.session.add(refresh_token)
        db.session.commit()

        self.base_user[0].strava_access_token[0].refresh_access_token(self.base_user[0].strava_refresh_token[0])
        db.session.commit()
        self.assertEqual(self.base_user[0].strava_access_token[0].access_token, 'new_access_token')
        self.assertEqual(self.base_user[0].strava_refresh_token[0].refresh_token, 'new_refresh_token')

    def test_model_as_dict(self):
        from tourtracker_app.models.strava_api_models import StravaAccessToken
        expires_at = int(round((datetime.now() + timedelta(days=3)).timestamp()))
        valid_access_token = StravaAccessToken(
            athlete_id=1234,
            access_token='dummy_access_token',
            expires_at=expires_at
        )
        expected = {
            'id': None,
            'athlete_id': 1234,
            'access_token': 'dummy_access_token',
            'expires_at': expires_at
        }

        result = valid_access_token.as_dict()
        self.assertEqual(expected, result)

    def test_tour_model_inits(self):
        tour = Tour('test_tour_name', 'test_start_date', 'test_end_date', 'test_user_id')
        self.assertEqual(tour.tour_name, 'test_tour_name')
        self.assertEqual(tour.start_date, 'test_start_date')
        self.assertEqual(tour.end_date, 'test_end_date')
        self.assertEqual(tour.user_id, 'test_user_id')
        self.assertIsInstance(tour.tour_uuid, str)

        tour_activities = TourActivities(
            1234,
            'test_activity_name',
            'test_activity_date',
            'polyline',
            'parent_tour',
            'user_id')

        self.assertEqual(tour_activities.strava_activity_id, 1234)
        self.assertEqual(tour_activities.activity_name, 'test_activity_name')
        self.assertEqual(tour_activities.activity_date, 'test_activity_date')
        self.assertEqual(tour_activities.summary_polyline, 'polyline')
