# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#


from flask import render_template, request, redirect, url_for 
from wtforms import (Form, HiddenField, BooleanField, TextAreaField, TextField,
                    validators)
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date
import datetime

from odontux.odonweb import app
from odontux.models import meta, schedule, administration
from odontux.views.forms import DateField, TimeField
from odontux.views.log import index


import pdb

class AppointmentForm(Form):
    patient_id = HiddenField('patient_id')
    dentist_id = HiddenField('dentist_id')
    emergency = BooleanField(_('emergency'))
    reason = TextAreaField(_('reason'))
    diagnostic = TextAreaField(_('diagnostic'))
    treatment = TextAreaField(_('treatment'))
    prognostic = TextAreaField(_('prognostic'))
    advise = TextAreaField(_('advise'))
    next_appointment = TextAreaField(_('next_appointment'))

class AgendaForm(Form):
    """ """
    #TODO : validators for time, either duration or endtime must be provided...
    appointment_id = HiddenField('appointment_id')
    day = DateField(_('day'), [validators.Required(_('Please specify '
                                'which day the appointment occurs'))])
    starttime = TimeField(_('starttime'), [validators.Required(_('Please '
                                'tell which time it started'))])
    duration = TimeField(_('duration'))
    endtime = TimeField(_('endtime'))

@app.route('/agenda/date/', methods=['POST'])
def agenda_date():
    return redirect(url_for('display_day', dateday=request.form["day"]))

@app.route('/agenda/')
def agenda():
    return render_template('summary_agenda.html')

@app.route('/agenda/day?date=<dateday>')
def display_day(dateday):
    """ """
    dateday = datetime.datetime.strptime(dateday.encode("utf_8"),
                                         '%Y-%m-%d').date()

    meetings = meta.session.query(schedule.Agenda).filter(or_(
                        cast(schedule.Agenda.starttime, Date) == (dateday),
                        cast(schedule.Agenda.endtime, Date) == (dateday)
                        )).all()
    appointments = []
    for meeting in meetings:
        appointment = meta.session.query(schedule.Appointment).filter(
                    schedule.Appointment.id == meeting.appointment_id
                    ).one()
        patient = meta.session.query(administration.Patient).filter(
                    administration.Patient.id == appointment.patient_id
                    ).one()
        appointments.append((patient, appointment))
    return render_template('agenda_day.html', appointments=appointments,
                            dateday=dateday)
