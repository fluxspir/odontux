# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

from flask import session, redirect, url_for, render_template, request

from odontux import constants, checks
from odontux.models import meta, administration, schedule, act, teeth
from odontux.odonweb import app
from odontux.views.administration import enter_patient_file
from odontux.views.log import index

import pdb

@app.route('/patient_appointment/?aid=<int:appointment_id>')
def patient_appointment(appointment_id):
    """
    This method must be rewritten with the one below 
     "enter_patient_appointment" to make one "big" method who will
     work "always".
     # TODO bug 10001
    """
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    appointment = (
            meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id == appointment_id)
                .one()
            )
    patient = checks.get_patient(appointment.patient_id)
    # Stock information about patient and appointment in session
    session['patient_id'] = patient.id
    session['appointment_id'] = appointment.id

    # Verify if this patient is really the one who have this appointment
    # because if it isn't, things could get very nasty after...
    # This function should be frequently used.
    if not checks.is_patient_self_appointment():
        session.pop('appointment_id', None)
        return redirect(url_for('enter_patient_file',
                        body_id=session['patient_id']))
    
    acts = checks.get_patient_acts(patient.id, appointment.id,
                [ act.AppointmentGestureReference.anatomic_location ]
                )
    return render_template("patient_appointment.html",
                            patient=patient,
                            appointment=appointment,
                            acts=acts)

@app.route('/patient/appointment/', methods=['GET', 'POST'])
def enter_patient_appointment():
    """ 
    # TODO bug 10001   ;  voir "patient_appointment()"
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
    try:
        if session['role'] != constants.ROLE_DENTIST:
            return redirect(url_for('index'))
    except KeyError:
        return redirect(url_for('logout'))

    if request.method == 'POST':
        # First at all, we need to quit old patient, and old appointment.
        # checks.quit_patient_file()
        # checks.quit_appointment()

        # We looking to find a couple patient_appointment by an 
        # appointment_id ( coming from a next_appointment or a
        # previous_appointment function )
        if request.form['appointment_id']:
            # feel in the new session variables with current appointment.
            appointment = (
                    meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.id == 
                                request.form['appointment_id'])
                        .one()
                    )
            patient = checks.get_patient(appointment.patient_id)

        # Case probably rare, but if we want to go in last appointment of 
        # patient known.
        elif request.form['patient_id']:
            patient = checks.get_patient(request.form['patient_id'])
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
        if not checks.is_patient_self_appointment():
            session.pop('appointment_id', None)
            return redirect(url_for('enter_patient_file',
                            body_id=session['patient_id']))
        
        acts = checks.get_patient_acts(patient.id, appointment.id,
                    [ act.AppointmentGestureReference.anatomic_location ]
                    )
        return render_template("patient_appointment.html",
                                patient=patient,
                                appointment=appointment,
                                acts=acts)

    # During the 'GET' method :
    if not checks.is_patient_self_appointment():
        session.pop('appointment', None)
        return redirect(url_for('enter_patient_file', 
                        body_id=session['patient_id']))
    
    patient = checks.get_patient(session['patient_id'])
    appointment = meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.id == session['appointment_id'])\
            .one()
    acts = checks.get_patient_acts(patient.id, appointment.id,
                    [ act.AppointmentGestureReference.tooth_id ]
                    )
    return render_template("patient_appointment.html",
                            patient=patient,
                            appointment=appointment,
                            acts=acts)

@app.route('/list/patient_appointments/')
def list_appointments():
    # Go to index if the admin tries to look at appointments
    # or if we aren't in a patient file.
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))
    # In the improbable (impossible) case that session['patient_id'] doesn't
    # exists when list_appointments is triggered, just flip back to index :
    if not checks.in_patient_file():
        return redirect(url_for('index'))
    
    # Get the patient in database, and the list of his appointments.
    patient = checks.get_patient(session['patient_id'])
    checks.quit_appointment()

    appointments = ( meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.patient_id == patient.id)
                        .join(schedule.Agenda)
                        .order_by(schedule.Agenda.starttime.desc())
                        .all()
    )

    return render_template("list_patient_appointments.html",
                            patient=patient,
                            appointments=appointments)

@app.route('/patient/acts/')
def list_acts():
    """
    Sends to template a list of tuples :
    ( gesture, tooth, act_info, act_specialty )
    """
    # Everybody but admin should enter this function ; however,
    # what is displayed should depends on whom is looking.
    # This will be taken care of in the html_template, by jinja.
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    if not checks.in_patient_file():
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])

    acts = checks.get_patient_acts(patient.id, None,
            [ act.AppointmentGestureReference.appointment_id, ]
            )
    return render_template("list_patient_acts.html",
                            patient=patient,
                            acts=acts)

@app.route("/patient/update_act?id=<int:patient_id>&act=<int:act_id>")
def update_patient_act(patient_id, act_id):
    pass
