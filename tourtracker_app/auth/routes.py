from flask import render_template, request, redirect, url_for, flash
from tourtracker_app import db
from tourtracker_app.auth import bp
from tourtracker_app.auth.forms  import LoginForm, SignupForm, PasswordResetRequestForm, PasswordResetForm
from tourtracker_app.models.auth_models import User
from tourtracker_app.auth.auth_email import send_user_validation_email, send_password_reset_email
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
import argon2


@bp.route('/login', methods=['GET','POST']) #TODO do we check if user is verified anywhere?
def login(message=None):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.execute(db.select(User).filter_by(email=form.email.data)).first()
            if not user:
                flash('Invalid username or password!')
                return redirect(url_for('auth.login'))
            try:
                user[0].check_password(form.password.data)
            except argon2.exceptions.VerificationError:
                flash('Invalid username or password!')
                return redirect(url_for('auth.login'))

            user = user[0]
            if not user.verified:
                flash('Please verify your email address')
                return redirect(url_for('auth.login'))
            login_user(user)
            redirect_to = request.args.get('next')
            if not redirect_to or url_parse(redirect_to).netloc != '':
                redirect_to = url_for('main.index')
            return redirect(redirect_to)
    return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('signup', methods=['GET','POST'])
def signup():
    form = SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            email_exists = db.session.execute(db.select(User).filter_by(email=email)).first()
            if email_exists:
                flash('Account already exists!')
                return redirect(url_for('auth.login'))
            else:
                user = User(
                    email=email,
                    password=password
                )
                db.session.add(user)
                db.session.commit()
                send_user_validation_email(user)
                return render_template('verify_email.html')
    print(form.errors)
    return render_template('signup.html', title='Sign Up', form=form)


@bp.route('/verify/<token>', methods=['GET'])
def validate_user(token):
    try:
        user = User.verify_user_verification_token(token)
    except:
        flash('Verification error. Please try again')
        return redirect(url_for('auth.signup'))
    user[0].verified = True
    db.session.commit()
    flash('Signup successful! Please log in.')
    return redirect(url_for('auth.login'))


@bp.route('/requestresetpassword', methods=['GET', 'POST'])
def request_password_reset():
    form = PasswordResetRequestForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = db.session.execute(db.select(User).filter_by(email=form.email.data)).first()
            if user:
                user = user[0]
                send_password_reset_email(user)
            flash('Password reset link sent if this account exists.')
            return redirect(url_for('auth.login'))
    return render_template('requestresetpassword.html', title='Reset Password', form=form)


@bp.route('/resetpassword/<token>', methods=['GET', 'POST'])
def reset_password(token):
    form = PasswordResetForm()
    if request.method == 'GET':
        try:
            user = User.verify_user_verification_token(token)
            return render_template('resetpassword.html', form=form)
        except:
            flash('Password reset error. Please try again')
            return redirect(url_for('auth.request_password_reset'))
    if request.method == 'POST':
        try:
            user = User.verify_user_verification_token(token)

            if form.validate_on_submit():
                user[0].set_password(form.password.data)
                db.session.commit()
                flash('Password reset. Please log in')
                return redirect(url_for('auth.login'))
        except:
            flash('Password reset error. Please try again')
            return redirect(url_for('auth.request_password_reset'))




