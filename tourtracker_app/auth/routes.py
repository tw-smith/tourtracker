from flask import render_template, request, redirect, url_for, flash, current_app
from tourtracker_app import db
from tourtracker_app.auth import bp
from tourtracker_app.auth.forms  import LoginForm, SignupForm, PasswordResetRequestForm, PasswordResetForm
from tourtracker_app.models.auth_models import User
from werkzeug.urls import url_parse
#from flask_login import login_user, logout_user, current_user # TODO: remove
import argon2
import requests
import urllib.parse
from flask_jwt_extended import jwt_required, get_jwt_identity, current_user





@bp.route('/login', methods=['GET','POST'])#TODO: do we check if user is verified anywhere?
@jwt_required(optional=True, locations=['json'])
def login():
    if current_user:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            params = {
                "service": "tourtracker",
            }
            url = f"{current_app.config['AUTH_SERVER_URL']}/auth?{urllib.parse.urlencode(params)}"
            response = requests.post(url,
                                     data={'username': form.username.data,
                                           'password': form.password.data})
            if response.status_code == 401:
                flash('Incorrect username or password!')
                return redirect(url_for('auth.login'))
           # TODO behaviour on account not verified
            if response.status_code == 200:
                redirect_to = request.args.get('next')
                if not redirect_to or url_parse(redirect_to).netloc != '':
                    redirect_to = url_for('main.index')
                redirect_to = f"{redirect_to}?jwt={response.json()['access_token']}"
                return redirect(redirect_to)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout', methods=['GET']) # TODO: revoke JWT?
def logout():
    #logout_user()
    return redirect(url_for('main.index'))


@bp.route('signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            params = {
                "service": "tourtracker",
            }
            url = f"{current_app.config['AUTH_SERVER_URL']}'/signup?'{urllib.parse.urlencode(params)}"
            response = requests.post(url,
                                     data={'email': form.email.data,
                                           'password': form.password.data})
            if response.status_code == 400:
                message = response.json()['msg']
                flash(message)
                return render_template('signup.html', title='Sign Up', form=form)
            if response.status_code == 201:
                user = User(email=form.data.email,
                            username=form.data.username,
                            public_id=response.json()['public_id'])
                db.session.add(user)
                db.session.commit()
                return render_template('verify_email.html')
    return render_template('signup.html', title='Sign Up', form=form)


# @bp.route('/verify/<token>', methods=['GET']) #
# def validate_user(token):
#     try:
#         user = User.verify_user_verification_token(token)
#     except:
#         flash('Verification error. Please try again')
#         return redirect(url_for('auth.signup'))
#     user[0].verified = True
#     db.session.commit()
#     flash('Signup successful! Please log in.')
#     return redirect(url_for('auth.login'))


@bp.route('/requestresetpassword', methods=['GET', 'POST'])
def request_password_reset():
    form = PasswordResetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            params = {
                "service": "tourtracker",
            }
            url = f"{current_app.config['AUTH_SERVER_URL']}'/resetpasswordrequest?'{urllib.parse.urlencode(params)}"
            response = requests.post(url,
                                     data={'email': form.email.data})
            if response.status_code == 200:
                flash(response.json()['msg'])
                return redirect(url_for('auth.login'))
    return render_template('requestresetpassword.html', title='Reset Password', form=form)


@bp.route('/resetpassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = PasswordResetForm()
    if request.method == 'GET':
        # try:
        #     user = User.verify_user_verification_token(token)
        return render_template('resetpassword.html', form=form)
        # except:
        #     flash('Password reset error. Please try again')
        #     return redirect(url_for('auth.request_password_reset'))

    # TODO: do we want to put the api call to the auth server here or in frontend JS buttonCLick?
    # if request.method == 'POST':
    #     try:
    #         user = User.verify_user_verification_token(token)
    #
    #         if form.validate_on_submit():
    #             user[0].set_password(form.password.data)
    #             db.session.commit()
    #             flash('Password reset. Please log in')
    #             return redirect(url_for('auth.login'))
    #     except:
    #         flash('Password reset error. Please try again')
    #         return redirect(url_for('auth.request_password_reset'))




