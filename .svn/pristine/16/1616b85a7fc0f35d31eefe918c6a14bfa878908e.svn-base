from datetime import datetime
from flask import Blueprint, render_template, redirect, flash, url_for, request, session
from flask_login import login_required, login_user, logout_user
from models.profile import User
from app import db

profile = Blueprint('profile', __name__)


@profile.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('profile/login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username, password=password).first()
    if registered_user is None:
        flash("Invalid credentials", category="error")
        return render_template('profile/login.html')
    login_user(registered_user, remember=True)
    session['user_id'] = registered_user.id
    registered_user.update(commit=False, loginTime=datetime.utcnow())
    db.session.commit()
    flash('Logged in successfully.')
    return redirect(request.args.get('next') or url_for('dashboard.dashboard'))


@profile.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('you have successfully logged out')
    return redirect(url_for('profile.login'))

