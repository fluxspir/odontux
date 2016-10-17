# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

from flask import session, redirect, url_for, render_template, request, abort

from odontux import constants, checks
from odontux.models import ( meta, administration, schedule, act, teeth, 
                            compta, documents )
from odontux.odonweb import app
from odontux.views.administration import enter_patient_file
from odontux.views.log import index

import pdb

@app.route('/patient_appointment/?aid=<int:appointment_id>')
def patient_appointment(appointment_id):
    """
    """
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)

    acts = checks.get_patient_acts(patient.id, appointment.id,
                [ act.AppointmentCotationReference.anatomic_location ]
                )
    return render_template("patient_appointment.html",
                            patient=patient,
                            appointment=appointment,
                            acts=acts)

@app.route('/list/patient_appointments&pid=<int:patient_id>')
def list_appointments(patient_id):
    # Go to index if the admin tries to look at appointments
    # or if we aren't in a patient file.
    if session['role'] == constants.ROLE_ADMIN:
        return abort(403)
    
    # Get the patient in database, and the list of his appointments.
    patient, appointment = checks.get_patient_appointment(
                                                        patient_id=patient_id)
    appointments = ( meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.patient_id == patient_id)
                        .join(schedule.Agenda)
                        .order_by(schedule.Agenda.starttime.desc())
                        .all()
    )
    return render_template("list_patient_appointments.html",
                            patient=patient,
                            appointment=appointment,
                            appointments=appointments)

@app.route('/patient/acts?pid=<int:patient_id>')
@app.route('/patient/acts?pid=<int:patient_id>&aid=<int:appointment_id>')
def list_acts(patient_id, appointment_id=0):
    """
    Sends to template a list of tuples :
    ( gesture, tooth, act_info, act_specialty )
    """
    # Everybody but admin should enter this function ; however,
    # what is displayed should depends on whom is looking.
    # This will be taken care of in the html_template, by jinja.
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    acts = checks.get_patient_acts(patient.id, None,
            [ act.AppointmentCotationReference.appointment_id, ]
            )
    payments = ( meta.session.query(compta.Payment)
        .filter(compta.Payment.patient_id == patient_id)
        .all()
    )
    return render_template("list_patient_acts.html",
                            patient=patient,
                            appointment=appointment,
                            acts=acts,
                            payments=payments)

@app.route("/patient/update_act?id=<int:patient_id>&act=<int:act_id>")
def update_patient_act(patient_id, act_id):
    pass
