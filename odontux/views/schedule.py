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

now = datetime.datetime.now()
today = datetime.date.today()

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


def get_appointment_field_list():
    return [ "patient_id", "dentist_id", "emergency", "reason", "diagnostic", 
             "treatment", "prognostic", "advise", "next_appointment" ]

def get_agenda_field_list():
    return [ "appointment_id", "day", "starttime", "duration", "endtime" ]


@app.route('/agenda/date/', methods=['POST'])
def agenda_date():
    return redirect(url_for('display_day', dateday=request.form["day"]))

@app.route('/agenda/')
def agenda():
    return render_template('summary_agenda.html', today=today)

@app.route('/agenda/day?date=<dateday>')
def display_day(dateday):
    """ 
    For viewing all appointments occured the day "dateday",
    and create links for "previous_day" and "next_day"
    """
    dateday = datetime.datetime.strptime(dateday.encode("utf_8"),
                                         '%Y-%m-%d').date()
    nextday = dateday + datetime.timedelta(days=1)
    prevday = dateday - datetime.timedelta(days=1)

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
    # dateday is return to create links to previous and next day
    return render_template('agenda_day.html', appointments=appointments,
                            dateday=dateday, nextday=nextday, prevday=prevday)


@app.route('/agenda/add', methods=['GET', 'POST'])
def add_appointment():
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))
    
    agenda_form = AgendaForm(request.form)
    appointment_form = AppointmentForm(request.form)
    if (request.method == 'POST' and agenda_form.validate()
        and appointment_form.validate() ):
            pass
