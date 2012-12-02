# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

from flask import session, render_template, redirect, url_for, request

from odontux import constants, checks
from odontux.odonweb import app
from odontux.views import forms
from odontux.models import meta, teeth
from odontux.views.log import index


@app.route('/patient/teeth/')
def list_teeth():
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()
    if patient.mouth and patient.mouth.teeth:
        teeth = [(tooth.id, tooth.name, constants.TOOTH_STATES[tooth.state], 
              tooth.surveillance) for tooth in patient.mouth.teeth ]
    else:
        teeth = None
    return render_template('list_teeth.html', patient=patient, 
                            appointment=appointment, teeth=teeth)


@app.route('/patient/tooth?<int:tooth_id>')
def show_tooth(tooth_id):
    """ 
    tooth = ( int:tooth.id , char:tooth.name, char:readable_tooth.state, 
              bool:tooth.surveillance )
    xxx_events = [ ( event , appointment ) ]
    """
    def _get_appointment(appointment_id):
        return meta.session.query(schedule.Appointment).filter(
                    schedule.Appointment.id == appointment_id).one()

    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()
    
    tooth = meta.session.query(teeth.Tooth)\
        .filter(teeth.Tooth.id == tooth_id)\
        .one()

    if not tooth in patient.mouth.teeth:
        return redirect(url_for('index'))
    
    tooth = (tooth.id, tooth.name, constants.TOOTH_STATES[tooth.state], 
             tooth.surveillance)

    tooth_events = meta.session.query(teeth.ToothEvent)\
        .filter(teeth.ToothEvent.tooth_id == tooth_id)\
        .filter(teeth.ToothEvent.appointment_id <= session['appointment_id'])\
        .order_by(teeth.ToothEvent.appointment_id)\
        .all()
    tooth_events = [ (event, _get_appointment(event.appointment_id) )
                      for event in tooth_events ]

    crown_events = meta.sesion.query(teeth.CrownEvent)\
        .filter(teeth.CrownEvent.tooth_id == tooth_id)\
        .filter(teeth.CrownEvent.appointment_id <= session['appointment_id'])\
        .order_by(teeth.CrownEvent.appointment_id)\
        .all()
    crown_events = [ (event, _get_appointment(event.appointment_id) )
                      for event in crown_events ]

    root_events = meta.session.query(teeth.RootEvent)\
        .filter(teeth.RootEvent.tooth_id == tooth_id)\
        .filter(teeth.RootEvent.appointment_id <= session['appointment_id'])\
        .order_by(teeth.RootEvent.appointment_id)\
        .all()
    root_events = [ (event, _get_appointment(event.appointment_id) )
                     for event in root_events ]


    return render_template('show_tooth.html', patient=patient,
                                              appointment=appointment, 
                                              tooth=tooth,
                                              tooth_events=tooth_events,
                                              crown_events=crown_events,
                                              root_events=root_events)
