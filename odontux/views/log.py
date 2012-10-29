# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/09/25
# v0.4
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, users
from odontux.secret import SECRET_KEY
from odontux.odonweb import app

from gettext import gettext as _


@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html',
               msg=_("Logged in as {}".format(session['username'])))
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = meta.session.query(users.OdontuxUser).filter\
                   (users.OdontuxUser.username == request.form['username'])\
                   .one()
            if request.form['password'] == user.password:
                session['username'] = request.form['username']
                session['role'] = user.role
                return redirect(url_for('index'))
            return redirect(url_for('logout'))
        except sqlalchemy.orm.exc.NoResultFound:
            return redirect(url_for('logout'))
    
    return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

app.secret_key = SECRET_KEY
