from datetime import datetime
from flask import Blueprint, render_template, redirect, flash, url_for, request, session
from flask_login import login_required, login_user, logout_user, current_user
from models.profile import User, check_password, generate_password
from app import db, app
from custom_email import send_email

profile = Blueprint('profile', __name__)


@profile.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('profile/login.html')
    username = request.form['username']
    password = request.form['password']
    registered_user = User.query.filter_by(username=username).first()
    if registered_user is None:
        hashedPasswd = generate_password(password)
        registered_user = User(username, hashedPasswd, 0, True)
        registered_user.save()
    elif not check_password(registered_user.password, password):
        flash("Invalid credentials", category="error")
        return render_template('profile/login.html')
    if login_user(registered_user, remember=True):
        session['user_id'] = registered_user.id
        registered_user.update(commit=False, loginTime=datetime.utcnow())
        db.session.commit()
        flash('Logged in successfully.')
    else:
        flash("Invalid credentials", category="error")
        return render_template('profile/login.html')
    return redirect(request.args.get('next') or url_for('dashboard.dashboard'))


@profile.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash('you have successfully logged out')
    return redirect(url_for('profile.login'))


@profile.route('/forget_password', methods=["GET", "POST"])
def forget_password():
    if request.method == 'GET':
        return render_template('profile/forget_password.html')
    else:
        username = request.form['username']
        registered_user = User.query.filter_by(username=username).first()
        if registered_user is None:
            flash("Invalid User", category="error")
        else:
            reset_link = app.config['BASE_URL'] + url_for('profile.reset_password', user_id=registered_user.id)
            text = ""
            html = render_template("emails/reset_password.html", user=registered_user, reset_link=reset_link)
            subject = "OCTAD: Reset Password Request"
            if send_email(registered_user.username, subject, text, html):
                flash('Please check your email for reset password link')
            else:
                flash('Please check your administrator for reset password link', category="error")
        return render_template('profile/forget_password.html')


@profile.route('/change_password', methods=["GET", "POST"])
@login_required
def change_password():
    """
    On GET: display change password page
    On POST: accepting old and new password and display the flash message.
    :return:
    """
    if request.method == 'GET':
        return render_template('profile/change_password.html')
    else:
        old_passwd = request.form['old_pwd']
        new_passwd = request.form['new_pwd']
        retype_passwd = request.form['retype_pwd']
        if old_passwd == new_passwd:
            flash('Old and New password can not same', category="error")
        elif new_passwd != retype_passwd:
            flash('New and Retype password must be same', category="error")
        elif old_passwd != new_passwd and new_passwd == retype_passwd:
            if check_password(current_user.password, old_passwd):
                hash_new_pwd = generate_password(new_passwd)
                current_user.update(commit=True, password=hash_new_pwd)
                flash('your password change successfully')
                return redirect(request.args.get('next') or url_for('dashboard.dashboard'))
            else:
                flash('Old password is not correct', category="error")
        else:
            flash('Please contact administrator', category="error")
        return render_template('profile/change_password.html')


@profile.route('/reset_password/<user_id>', methods=["GET", "POST"])
def reset_password(user_id):
    """
    On GET: display reset password page
    On POST: accepting new password and reseting to parameterized user_id
    :param user_id: user_id
    :return:
    """
    if request.method == 'GET':
        return render_template('profile/reset_password.html', user_id=user_id)
    else:
        # TODO: Check existing password and new password is same or not. this filter is needed or not?
        raw_password = request.form['new_pwd']
        re_type_password = request.form['retype_pwd']
        registered_user = User.query.filter_by(id=user_id).first()
        if registered_user is None:
            flash("Invalid User", category="error")
            return render_template('profile/reset_password.html', user_id=user_id)
        else:
            if raw_password != re_type_password:
                flash("Both Password should be same", category="error")
                return render_template('profile/reset_password.html', user_id=user_id)
            elif check_password(registered_user.password, raw_password):
                flash("Previous and New Password can not be same", category="error")
                return render_template('profile/reset_password.html', user_id=user_id)
            password = generate_password(raw_password)
            registered_user.update(commit=True, password=password)
            flash('Password chagned successfully')
            return redirect(url_for('profile.login'))
