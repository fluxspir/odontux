# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for
import sqlalchemy
#from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks
from odontux.models import meta, administration, schedule
from odontux.views.log import index

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, validators)

#class EventForm(Form):
    

@app.route('/choose/event_location?pid=<int:patient_id>&aid=<int:appointment_id>')
def choose_event_location(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if not session['role'] in authorized_roles:
        return redirect(url_for('index'))
    patient = (
        meta.session.query(administration.Patient)
            .filter(administration.Patient.id == patient_id)
            .one()
        )
    appointment = (
        meta.session.query(schedule.Appointment)
            .filter(schedule.Appointment.id == appointment_id)
            .one()
        )
    return render_template('choose_event_location.html',
                                            patient=patient,
                                            appointment=appointment)

@app.route('/add/tooth_event')
def add_tooth_event():
    pass

@app.route('/add/periodonte_event')
def add_periodonte_event():
    pass

@app.route('/add/softtissues_event')
def add_softtissues_event():
    pass

@app.route('/add/headneck_event')
def add_headneck_event():
    pass

