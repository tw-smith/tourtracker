# import pytest
# from flask import session, g
# from tourtracker_app import db
#
#
# def test_login(client, auth):
#     assert client.get('/auth/login').status_code == 200
#     response = auth.login()
#     assert response.headers["Location"] == "/"
#
#     with client:
#         client.get('/')
#         assert session['user_id'] == 1
#         assert g.user['email'] == 'test@test.com'
#
