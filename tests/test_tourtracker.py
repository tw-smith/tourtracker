import os
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

import pytest
import unittest
from flask import current_app
from tourtracker_app import create_app, db
from tourtracker_app.models.auth_models import User


class TestTourTracker(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.appctx = self.app.app_context()
        self.appctx.push()
        db.create_all()
        self.populate_db()
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
            password='testtest',
        )
        user.verified = True
        db.session.add(user)

        non_verified_user = User(
            email='nonverified@test.com',
            password='testtest',
        )
        db.session.add(non_verified_user)

        admin_user = User(
            email='admin@test.com',
            password='admin_password'
        )
        admin_user.isadmin = True
        admin_user.verified = True
        db.session.add(admin_user)

        db.session.commit()

    def login(self):
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'testtest'
        })

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    # Would be nice to use PyTest parametrize here but it is not compatible with this
    # unittest.TestCase approach. https://docs.pytest.org/en/6.2.x/unittest.html
    # TODO: implement @pytest.mark.parametrize if we ever refactor this to full PyTest
    # Or could use this: https://github.com/wolever/parameterized
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

    def login_helper(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password,
        }, follow_redirects=True)

    def login(self):
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'testtest',
        })

    def login_admin(self):
        self.client.post('/auth/login', data={
            'email': 'admin@test.com',
            'password': 'admin_password'
        })

    def test_login(self):
        response = self.login_helper('test@test.com', 'testtest')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'test@test.com' in html

    def test_logout(self):
        self.login()
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
        response = self.login_helper('nonverified@test.com', 'testtest')
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'Please verify your email address' in html
        assert response.request.path == '/auth/login'

    def test_signup_form(self):
        response = self.client.get('/auth/signup')
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Check all signup fields are in HTML
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert 'name="repeat_pw"' in html
        assert 'name="submit"' in html

    def test_jwt_encode_decode(self):
        jwt_user = User(
            email='jwt@test.com',
            password='testpassword'
        )
        token = jwt_user.create_token()
        decoded_token = jwt_user.decode_token(token)
        assert decoded_token['uuid'] == jwt_user.uuid
        assert decoded_token['iss'] == self.app.config['JWT_ISSUER']

    def test_register_email_validation(self):
        jwt_user = User(
            email='jwt@test.com',
            password='testpassword'
        )
        db.session.add(jwt_user)
        db.session.commit()
        token = jwt_user.create_token()
        response = self.client.get('/auth/verify/' + token, follow_redirects=True)
        html = response.data.decode()
        assert response.status_code == 200
        assert 'Signup successful' in html
        assert response.request.path == '/auth/login'
        assert jwt_user.verified is True
        db.session.delete(jwt_user)
        db.session.commit()

    def test_register_email_validation_bad_token(self):
        jwt_user = User(
            email='jwt@test.com',
            password='testpassword'
        )
        db.session.add(jwt_user)
        db.session.commit()
        token = jwt_user.create_token()
        bad_token = 'junktoken'
        response = self.client.get('/auth/verify/' + bad_token, follow_redirects=True)
        html = response.data.decode()
        assert response.status_code == 200
        assert 'Verification error' in html
        assert response.request.path == '/auth/signup'
        assert jwt_user.verified is False
        db.session.delete(jwt_user)
        db.session.commit()

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
            'email': 'test@test.com',
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
        jwt_user = User(
            email='jwt@test.com',
            password='testpassword'
        )
        db.session.add(jwt_user)
        jwt_user.verified = True
        db.session.commit()
        token = jwt_user.create_token()
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
        assert jwt_user.check_password('new_password') is True
        post_html = post_response.data.decode()
        assert 'Password reset. Please log in' in post_html

    def test_admin_user_profile_page(self):
        self.login_admin()
        response = self.client.get('/index', follow_redirects=True)
        html = response.get_data(as_text=True)
        assert 'Webhook Admin' in html



