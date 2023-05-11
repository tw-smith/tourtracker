import os
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'

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
            password='testtest'
        )
        db.session.add(user)
        db.session.commit()

    def login(self):
        self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'testtest'
        })

    def test_app(self):
        assert self.app is not None
        assert current_app == self.app

    def test_auth_redirects(self):
        response = self.client.get('/profile', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'
        response = self.client.get('/createtour', follow_redirects=True)
        assert response.status_code == 200
        assert response.request.path == '/auth/login'

    def test_login(self):
        response = self.client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'testtest'
        }, follow_redirects=True)
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'test@test.com' in html

    def test_signup_form(self):
        response = self.client.get('/auth/signup')
        assert response.status_code == 200
        html = response.get_data(as_text=True)

        # Check all signup fields are in HTML
        assert 'name="email"' in html
        assert 'name="password"' in html
        assert 'name="repeat_pw"' in html
        assert 'name="submit"' in html



