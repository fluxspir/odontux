# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/26
# v0.5
# Licence BSD
#

import pdb
from base64 import b64decode
import scrypt

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, users
from odontux.secret import SECRET_KEY
from odontux.odonweb import app

from odontux import constants, checks

from gettext import gettext as _

@app.route('/')
def index():
    checks.quit_patient_file()
    checks.quit_appointment()
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    checks.quit_patient_file()
    checks.quit_appointment()
    if request.method == 'POST':
        try:
            user = meta.session.query(users.OdontuxUser).filter\
                   (users.OdontuxUser.username == request.form['username'])\
                   .one()
            try:
                if scrypt.decrypt(b64decode(user.password), 
                                    request.form['password'].encode("utf_8")):
                    session['username'] = user.username
                    session['user_id'] = user.id
                    session['role'] = int(user.role)
                    session['ROLES'] = constants.ROLES_LIST
                    session['TOOTH_STATES'] = constants.TOOTH_STATES
                    session['ROLE_DENTIST'] = constants.ROLE_DENTIST
                    session['ROLE_NURSE'] = constants.ROLE_NURSE
                    session['ROLE_ASSISTANT'] = constants.ROLE_ASSISTANT
                    session['ROLE_SECRETARY'] = constants.ROLE_SECRETARY
                    session['ROLE_ADMIN'] = constants.ROLE_ADMIN
                    session['ROLE_PATIENT'] = constants.ROLE_PATIENT
                    session['avatar_id'] = user.avatar_id
                    session['isoweekdays'] = constants.ISOWEEKDAYS 
                    session['months'] = constants.MONTHS
                    session['UNITIES'] = [ ( id, UNIT[0] ) for id, UNIT in
                                            constants.UNITIES.items() ]
                    for unit in constants.UNITIES.items():
                        session[unit[1][1]] = unit[0]
                    
                    session['END_USE_REASONS'] = [ ( id, EUR[0] ) for id, EUR 
                                        in constants.END_USE_REASONS.items() ]

                    session['MEDICAL_HISTORIES'] = constants.MEDICAL_HISTORIES
                    
                    for EUR in constants.END_USE_REASONS.items():
                        session[EUR[1][1]] = EUR[0]

                    for anamnesis in constants.ANAMNESIS.items():
                        session[anamnesis[1][1]] = anamnesis[0]
                        #anamnesis_type = 'anamnesis_type_' + str(anamnesis[0])
                        #session[anamnesis_type]= anamnesis[1][0]

                    for AR in constants.ALLERGIC_REACTIONS.items():
                        session[AR[1][1]] = AR[0]

                    if request.form['password'] == "please_change_password":
                        return redirect(url_for('update_user',
                                                body_id = user.id,
                                                form_to_display = "gen_info"))

                    else:
                        return redirect(url_for('index'))
            except scrypt.error:
                return redirect(url_for('logout'))
        except sqlalchemy.orm.exc.NoResultFound:
            return redirect(url_for('logout'))
    return render_template('login.html')

@app.route('/logout/')
def logout():
    checks.quit_patient_file()
    checks.quit_appointment()
    #session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))

app.secret_key = SECRET_KEY
