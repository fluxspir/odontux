# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

from flask import session, redirect, url_for, render_template, request

from odontux import constants
from odontux.views import controls
from odontux.models import meta, administration, schedule, act, teeth
from odontux.odonweb import app
from odontux.views.administration import enter_patient_file
from odontux.views.log import index

import pdb

@app.route('/patient/appointment/', methods=['GET', 'POST'])
def enter_patient_appointment():
    """ 
    We are entering in this function in a specific appointment
    that was made for a reason,
    where was established a diagnostic,
    were done a treatment,
    were imagined a prognostic,
    were given advise,
    maybe an drug prescription was made,
    the appointment may have been taken in emergency.
    
    The treatment part may have been a unique or a 
    series of "acts"
    These acts have an alias to described in comprehensive words
    what was made, 
    they have a code, usually depending on the social security of the country,
    they are made either on a tooth or no (more global, like a descaling),
    they have a price (which "will" change over the time, that's why it is
    recorded right now),
    is related to the invoice_id in gnucash,
    and may be paid or not.
    """

    def _get_appointment_acts():
        """ To have more human_readable data, when "id" won't speak a lot..."""
        acts = meta.session.query(act.AppointmentActReference)\
            .filter(act.AppointmentActReference.appointment_id ==
                    session['appointment_id']).all()
        appointment_acts = []
        for a in acts:
            if a.tooth_id:
                tooth_name = meta.session.query(teeth.Tooth)\
                    .filter(teeth.Tooth.id == a.tooth_id)\
                    .one().name
            else:
                tooth_name = ""
            act_alias = meta.session.query(act.ActType)\
                .filter(act.ActType.id == a.act_id)\
                .one().alias
            appointment_acts.append((a, act_alias, tooth_name))
        return appointment_acts
        
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # First at all, we need to quit old patient, and old appointment.
        # controls.quit_patient_file()
        # controls.quit_appointment()

        # We looking to find a couple patient_appointment by an 
        # appointment_id ( coming from a next_appointment or a
        # previous_appointment function )
        if request.form['appointment_id']:
            # feel in the new session variables with current appointment.
            appointment = meta.session.query(schedule.Appointment)\
                .filter(schedule.Appointment.id == 
                        request.form['appointment_id']).one()
            patient = meta.session.query(administration.Patient)\
                .filter(administration.Patient.id == appointment.patient_id)\
                .one()
        # Case probably rare, but if we want to go in last appointment of 
        # patient known.
        elif request.form['patient_id']:
            patient = meta.session.query(administration.Patient)\
                .filter(administration.Patient.id ==
                        request.form['patient_id']).one()
            appointment = meta.session.query(schedule.Appointment)\
                .filter(schedule.Appointment.patient_id ==
                        session['patient_id']).all()[-1]

        # Here, we shouldn't even see that kind of case, that could be dug up 
        # a little (entering the last appointment if a session['patient'] exist
        # or other cases scenarii... maybe.
        else:
            return redirect(url_for('enter_patient_file', 
                                    session['patient_id']))

        # Stock information about patient and appointment in session
        session['patient_id'] = patient.id
        session['appointment_id'] = appointment.id

        # Verify if this patient is really the one who have this appointment
        # because if it isn't, things could get very nasty after...
        # This function should be frequently used.
        if not controls.is_patient_self_appointment():
            session.pop('appointment_id', None)
            return redirect(url_for('enter_patient_file',
                            body_id=session['patient_id']))
        
        appointment_acts = _get_appointment_acts()
        return render_template("patient_appointment.html",
                                patient=patient,
                                appointment=appointment,
                                acts=appointment_acts)

    # During the 'GET' method :
    if not controls.is_patient_self_appointment():
        session.pop('appointment', None)
        return redirect(url_for('enter_patient_file', 
                        body_id=session['patient_id']))
    
    appointment_acts = _get_appointment_acts()
    patient = meta.session.query(administration.Patient)\
            .filter(administration.Patient.id == session['patient_id'])\
            .one()
    appointment = meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.id == session['appointment_id'])\
            .one()
    return render_template("patient_appointment.html",
                            patient=patient,
                            appointment=appointment,
                            acts=appointment_acts)

@app.route('/patient/appointments/')
def list_appointments():
    # Go to index if the admin tries to look at appointments
    # or if we aren't in a patient file.
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))
    # In the improbable (impossible) case that session['patient_id'] doesn't
    # exists when list_appointments is triggered, just flip back to index :
    try:
        if not session['patient_id']:
            pass
    except KeyError:
        return redirect(url_for('index'))
    
    # Get the patient in database, and the list of his appointments.
    patient = meta.session.query(administration.Patient)\
        .filter(administration.Patient.id ==
                session['patient_id']).one()

    appointments = meta.session.query(schedule.Appointment)\
        .filter(schedule.Appointment.patient_id ==
                session['patient_id']).all()
    return render_template("list_patient_appointments.html",
                            patient=patient,
                            appointments=appointments)
