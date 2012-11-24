# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/26
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, users
from odontux.secret import SECRET_KEY
from odontux.odonweb import app

from odontux import constants

from gettext import gettext as _

def _quit_patient_file():
    try:
        if session['patient']:
            session.pop('patient', None)
    except KeyError:
        pass

@app.route('/')
def index():
    _quit_patient_file()
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    _quit_patient_file()
    if request.method == 'POST':
        try:
            user = meta.session.query(users.OdontuxUser).filter\
                   (users.OdontuxUser.username == request.form['username'])\
                   .one()
            if request.form['password'] == user.password:
                session['username'] = user.username
                session['user_id'] = user.id
                session['role'] = int(user.role)
                session['ROLES'] = constants.ROLES_LIST 
                session['email'] = user.mails[0]
                session['avatar_id'] = user.avatar_id
                return redirect(url_for('index'))
            return redirect(url_for('logout'))
        except sqlalchemy.orm.exc.NoResultFound:
            return redirect(url_for('logout'))
    return render_template('login.html')

@app.route('/logout/')
def logout():
    _quit_patient_file()
    session.pop('username', None)
    return redirect(url_for('index'))

app.secret_key = SECRET_KEY
