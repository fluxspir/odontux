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


class SelectSTEventForm(Form):
    soft_tissue = SelectField(_('soft tissue'), coerce=int)

class EndoBuccalEventForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Name of the event'), [validators.Required()])
    comments = TextAreaField(_('Comments about the event'))

class HardPalateEventForm(EndoBuccalEventForm):
    pass

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
def add_endo_buccal_event():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    select_soft_form = SelectSTEventForm(request.form)
    select_soft_form.soft_tissue.choices = []
    for loc in constants.ANATOMIC_LOCATION.items():
        if loc[1][2] != "endobuccal":
            continue
        select_soft_form.soft_tissue.choices.append(
            (loc[0], loc[1][0]) 
        )
    endo_buccal_event_form = EndoBuccalEventForm(request.form)

    if ( request.method == 'POST' and select_soft_form.validate()
                                    and endo_buccal_event_form.validate() ):
        pass

@app.route('/add/headneck_event')
def add_headneck_event():
    pass

