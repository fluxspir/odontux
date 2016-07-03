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
from odontux.models import meta, administration, schedule, endobuccal, headneck
from odontux.views.log import index

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, validators)

#class EventForm(Form):


class SelectEBLocationEventForm(Form):
    location = SelectField(_('soft tissue'), coerce=int)

class EndoBuccalEventForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Name of the event'), [validators.Required()])
    comments = TextAreaField(_('Comments about the event'))

class HardPalateEventForm(EndoBuccalEventForm):
    pass

@app.route('/choose/event_location?pid=<int:patient_id>'
            '&aid=<int:appointment_id>')
def choose_event_location(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if not session['role'] in authorized_roles:
        return redirect(url_for('index'))
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    return render_template('choose_event_location.html',
                                            patient=patient,
                                            appointment=appointment)

@app.route('/add/endo_buccal_event?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
def add_endo_buccal_event(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
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
    select_location_form = SelectEBLocationEventForm(request.form)
    select_location_form.location.choices = []
    for loc in constants.ANATOMIC_LOCATION_SOFT_TISSUES.items():
        if loc[1][2] != "endobuccal":
            continue
        select_location_form.location.choices.append(
            (loc[0], loc[1][0]) 
        )
    endo_buccal_event_form = EndoBuccalEventForm(request.form)

    if ( request.method == 'POST' and select_location_form.validate()
                                    and endo_buccal_event_form.validate() ):
        
        loc = select_location_form.location.data
        if constants.ANATOMIC_LOCATION_SOFT_TISSUES[loc][2] == "endobuccal":
            LocationEvent = getattr(endobuccal, 
                            constants.ANATOMIC_LOCATION_SOFT_TISSUES[loc][3] )
        elif constants.ANATOMIC_LOCATION_SOFT_TISSUES[loc][3] == "headneck":
            LocationEvent = getattr(headneck,
                            constants.ANATOMIC_LOCATION_SOFT_TISSUES[loc][3] )
        else:
            return redirect(url_for('index'))

        values = {
            'patient_id': patient_id,
            'appointment_id': appointment_id,
            'name': endo_buccal_event_form.name.data,
            'comments': endo_buccal_event_form.comments.data,
#            'docs': endo_buccal_event_form.docs.data,
            }
        if LocationEvent == endobuccal.VestibuleEvent:
            values['location'] = loc

        new_event = LocationEvent(**values)
        meta.session.add(new_event)
        meta.session.commit()

        return redirect(url_for('choose_event_location',
                                patient_id=patient_id,
                                appointment_id=appointment_id))

    return render_template('add_endobuccal_event.html',
                            select_location_form=select_location_form,
                            endo_buccal_event_form=endo_buccal_event_form,
                            patient=patient,
                            appointment=appointment)

@app.route('/add/headneck_event')
def add_headneck_event():
    pass

