# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#


from flask import render_template, request, redirect, url_for, session 
from wtforms import (Form, HiddenField, BooleanField, TextAreaField, TextField,
                    IntegerField, validators)
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date
import datetime

from odontux import constants, checks
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
    reason = TextField(_('reason'))
    diagnostic = TextField(_('diagnostic'))
    treatment = TextField(_('treatment'))
    prognostic = TextField(_('prognostic'))
    advise = TextField(_('advise'))
    next_appointment = TextField(_('next_appointment'))

class AgendaForm(Form):
    """ """
    #TODO : validators for time, either duration or endtime must be provided...
    appointment_id = HiddenField('appointment_id')
    day = DateField(_('day'), [validators.Required(_('Please specify '
                                'which day the appointment occurs'))])
    starthour = IntegerField(_('h'), [validators.Required(_('Please '
                                'tell which time it started'))])
    startmin = IntegerField(_('m'), [validators.Required(_("Minutes"))])
    durationhour = IntegerField(_('h'), [validators.Optional()])
    durationmin = IntegerField(_('m'), [validators.Optional()])
    endhour = IntegerField(_('h'), [validators.Optional()])
    endmin = IntegerField(_('m'), [validators.Optional()])


def get_appointment_field_list():
    return [ "patient_id", "dentist_id", "emergency", "reason", "diagnostic", 
             "treatment", "prognostic", "advise", "next_appointment" ]

def get_agenda_field_list():
    return [ "appointment_id", "day", "starthour", "startmin", "durationhour",
             "durationmin", "endhour", "endmin" ]


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


def agenda_handler(day, starthour, startmin, durationhour, durationmin, 
                   endhour, endmin):
    """
    return ( (yyyymmdd hh:mm), (yyyymmdd hh:mm) )  == 
                                                ( startdaytime, enddaytime)
    """
    try:
        starttime = datetime.datetime(day, starthour + " " + startmin)
    except:
        raise

    return starttime

@app.route('/agenda/add?id=<int:body_id>', methods=['GET', 'POST'])
def add_appointment(body_id=""):
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    if not body_id:
        checks.quit_patient_file()
        checks.quit_appointment()

    agenda_form = AgendaForm(request.form)
    appointment_form = AppointmentForm(request.form)

    if (request.method == 'POST' and agenda_form.validate()
        and appointment_form.validate() 
       ):
        # get the appointment agenda schedule first, to raise exception if 
        # agenda problems
        (starttime, endtime) = agenda_handler(agenda_form.day.data, 
                       agenda_form.starthour.data, agenda_form.startmin.data, 
                       agenda_form.durationhour.data, 
                       agenda_form.durationmin.data,
                       agenda_form.endhour.data, agenda_form.endmin.data)

        # add the appointment infos
        args = { f: getattr(appointment_form, f).data 
                 for f in get_appointment_field_list() }
        new_appointment = schedule.Appointment(**args)
        #meta.session.add(new_appointment)
        #meta.session.commit()

        # if every thing went fine until now, we just have to add to database
        # agenda data, and we're done.
        pass

    # the 'GET method'
    return render_template('add_appointment.html',
                            agenda_form=agenda_form,
                            appointment_form=appointment_form)
