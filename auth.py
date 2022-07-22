from cProfile import label
from hashlib import new
from click import password_option
from flask import Blueprint, flash, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash, check_password_hash
from .models import Labeller
from flask_login import login_user, login_required, logout_user

from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    labeller = Labeller.query.filter_by(username=username).first()
    # print("Email hash : ", generate_password_hash(email, method='sha256'))

    # check if the user exists
    # take the user supplied password, hash it and compare it against the hashed password stored in the database
    if not labeller or not check_password_hash(labeller.password, password):
        flash('Please check your login details and try again')
        return redirect(url_for('auth.login'))
    
    login_user(labeller, remember=remember)
    return redirect(url_for('main.survey_instructions'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database
    # email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')

    labeller = Labeller.query.filter_by(username=username).first()  ## if this returns a user,  the user already exists in the database

    if labeller:
        flash('Labeller already exists in the database')
        return redirect(url_for('auth.signup'))

    # new_labeller = Labeller(email=email, username=username, password=generate_password_hash(password, method='sha256'))
    new_labeller = Labeller(username=username, password=generate_password_hash(password, method='sha256'))

    

    db.session.add(new_labeller)
    db.session.commit()

    new_labeller = Labeller.query.filter_by(username=username).first()
    message = 'Your labeller id is ' + str(new_labeller.id) + '. Please remember it so that you can use it if you forget your password'
    flash(message)
    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    # return render_template('logout.html')