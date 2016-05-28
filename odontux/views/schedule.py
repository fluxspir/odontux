# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

import pdb
from flask import render_template, request, redirect, url_for, session 
from wtforms import (Form, HiddenField, BooleanField, TextAreaField, TextField,
                    IntegerField, SelectField, DateField, validators)
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date
import datetime

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, schedule, administration, users
from odontux.views.forms import TimeField
from odontux.views.log import index

class AppointmentForm(Form):
    patient_id = HiddenField('patient_id')
    dentist_id = SelectField(coerce=int)
    emergency = BooleanField(_('emergency'))
    reason = TextAreaField(_('reason'))
    diagnostic = TextAreaField(_('diagnostic'))
    treatment = TextAreaField(_('treatment'))
    prognostic = TextAreaField(_('prognostic'))
    advise = TextAreaField(_('advise'))
    next_appointment = TextAreaField(_('next_appointment'))
    absent = BooleanField(_('absent'))
    excuse = TextField(_('excuse'))

class AgendaForm(Form):
    """ """
    #TODO : validators for time, either duration or endtime must be provided...
    appointment_id = HiddenField('appointment_id')
    day = DateField(_('day'), format='%Y-%m-%d', 
                            validators=[validators.Optional()])
    starthour = IntegerField(_('h'), [validators.Optional()])
    startmin = IntegerField(_('m'), [validators.Optional()])
    durationhour = IntegerField(_('h'), [validators.Optional()])
    durationmin = IntegerField(_('m'), [validators.Optional()])
    endhour = IntegerField(_('h'), [validators.Optional()])
    endmin = IntegerField(_('m'), [validators.Optional()])

class SummaryAgendaForm(Form):
    day = DateField(_('day'), format='%Y-%m-%d')
    dentist_id = SelectField(_('Dentist'), coerce=int,
                                    validators=[validators.Optional()] )
    dental_unit_id = SelectField(_('Dental_unit'), coerce=int,
                                    validators=[validators.Optional()] )


def get_appointment_field_list():
    return [ "patient_id", "dentist_id", "emergency", "reason", "diagnostic", 
             "treatment", "prognostic", "advise", "next_appointment", "absent",
             "excuse"]

def get_agenda_field_list():
    return [ "appointment_id", "day", "starthour", "startmin", "durationhour",
             "durationmin", "endhour", "endmin" ]

def get_time_field_list():
    """ Used for making the width of these fields """
    return [ "starthour", "startmin", "durationhour","durationmin", "endhour",
             "endmin" ]

def get_summary_agenda_form(day=datetime.date.today()):
    """ 
    return summary_agenda_form, to send to summary_agenda in the 
    header_mainsummary
    """
    summary_agenda_form = SummaryAgendaForm(request.form)
    summary_agenda_form.day.data = day
    summary_agenda_form.dentist_id.choices = [ (dentist.id, dentist.firstname +
                                    " " + dentist.lastname) for dentist in
                                    meta.session.query(users.OdontuxUser)\
                                    .filter(users.OdontuxUser.role ==
                                            constants.ROLE_DENTIST)\
                                    .all()
                                    ]
    summary_agenda_form.dental_unit_id.choices  = [ 
                (dental_unit.id, dental_unit.name) for dental_unit in
                    meta.session.query(users.DentalUnit).all()
                ]

    if session['role'] == constants.ROLE_DENTIST :
        summary_agenda_form.dentist_id.data = session['user_id']
    return summary_agenda_form

@app.route('/agenda/date/', methods=['POST'])
def agenda_date():
    summary_agenda_form = SummaryAgendaForm(request.form)
    if request.method == 'POST' :
        return redirect(url_for('display_day', 
                    dateday=summary_agenda_form["day"].data,
                    dentist_id=summary_agenda_form['dentist_id'].data,
                    dental_unit_id=summary_agenda_form['dental_unit_id'].data))

@app.route('/agenda/')
def agenda():
    summary_agenda_form = get_summary_agenda_form()
    return render_template('summary_agenda.html', 
                            summary_agenda_form=summary_agenda_form)

@app.route('/agenda/day?date=<dateday>&dentist=<int:dentist_id>'
            '&dental_unit_id=<int:dental_unit_id>')
def display_day(dateday, dentist_id, dental_unit_id):
    """ 
    For viewing all appointments occured the day "dateday",
    and create links for "previous_day" and "next_day"
    """
    dateday = datetime.datetime.strptime(dateday,'%Y-%m-%d').date()
    summary_agenda_form = get_summary_agenda_form(dateday)
    if not dentist_id:
        return redirect(url_for('index'))
    nextday = dateday + datetime.timedelta(days=1)
    prevday = dateday - datetime.timedelta(days=1)
    meetings = (
        meta.session.query(schedule.Agenda)
            .filter(or_(
                cast(schedule.Agenda.starttime, Date) == (dateday),
                cast(schedule.Agenda.endtime, Date) == (dateday) 
                )
            )
            .filter(
                schedule.Appointment.dentist_id == dentist_id,
                schedule.Appointment.dental_unit_id == dental_unit_id
            )
            .all()
    )

    # dateday is return to create links to previous and next day
    return render_template('agenda_day.html', meetings=meetings,
                            dateday=dateday, nextday=nextday, prevday=prevday,
                            summary_agenda_form=summary_agenda_form,
                            dentist_id=dentist_id, dental_unit_id=dental_unit_id)


def agenda_handler(day, starthour=0, startmin=0, durationhour=0, durationmin=0,
                   endhour=0, endmin=0):
    """
    return 2 datetime object : ( starttime, endtime)
    """
    if not starthour: starthour = 0
    if not startmin: startmin = 0
    if not durationhour: durationhour = 0
    if not durationmin: durationmin = 0
    if not endhour: endhour = 0
    if not endmin: endmin = 0
    starttime = datetime.datetime(day.year, day.month, day.day, 
                                                        starthour, startmin)

    if durationhour or durationmin:
        endtime = starttime + datetime.timedelta(hours=durationhour, 
                                                 minutes=durationmin)
    elif endhour or endmin:
        endtime = datetime.datetime(year, month, day, endhour, endmin)
    else:
        raise Exception(_("duration / start endtime problem !"))
    return (starttime, endtime)

def reverse_agenda_handler(starttime, endtime):
    """ return day .... view agenda_handler(), it's the contrary. 
    """
    day  = starttime.date() 
    (starthour, startmin) = (starttime.hour, starttime.minute)
    (endhour, endmin) = (endtime.hour , endtime.minute)
    duration = endtime - starttime
    durationhour = duration.seconds / 3600
    durationmin = duration.seconds % 3600 / 60
    return (day, starthour, startmin, durationhour, durationmin, endhour, 
                                                                  endmin)

@app.route('/agenda/update?id=<int:body_id>'
           '&appointment=<int:appointment_id>', methods=['GET', 'POST'])
def update_appointment(body_id, appointment_id):
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    session['patient_id'] = body_id
    session['appointment_id'] = appointment_id
    patient = checks.get_patient(session['patient_id'])
    appointment = meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.id == session['appointment_id'])\
            .one()

    agenda_form = AgendaForm(request.form)
    appointment_form = AppointmentForm(request.form)
    appointment_form.dentist_id.choices = [ (user.id, user.firstname + " " 
                                           + user.lastname ) for user in
                            meta.session.query(users.OdontuxUser).filter(
                            users.OdontuxUser.role == constants.ROLE_DENTIST)\
                            .all()
                                           ]

    if (request.method == 'POST' and agenda_form.validate()
        and appointment_form.validate() ):
        # get the agenda entry:
        agenda = meta.session.query(schedule.Agenda)\
            .filter(schedule.Agenda.appointment_id == 
                                session['appointment_id']).one()
        # verify the day_time infos
        (starttime, endtime) = agenda_handler(agenda_form.day.data,
                       agenda_form.starthour.data, agenda_form.startmin.data, 
                       agenda_form.durationhour.data, 
                       agenda_form.durationmin.data,
                       agenda_form.endhour.data, agenda_form.endmin.data)
        # update appointment infos:
        for f in get_appointment_field_list():
            setattr(appointment, f,  getattr(appointment_form, f).data)
        for f,g in (("starttime", starttime), ("endtime", endtime)):
            setattr(agenda, f, g)
        meta.session.commit()
        return redirect(url_for('enter_patient_appointment'))
    
    (day, starthour, startmin, durationhour, durationmin, endhour, endmin) = \
            reverse_agenda_handler(appointment.agenda.starttime, 
                                   appointment.agenda.endtime)

    # prepopulate agenda fields :
    for f,g in ( ("day", day), ("starthour", starthour), 
                 ("startmin", startmin), ("durationhour", durationhour),
                 ("durationmin", durationmin), ("endhour", endhour),
                 ("endmin", endmin) ):
        getattr(agenda_form, f).data = g
    # prepoputate appointments fields:
    for f in get_appointment_field_list():
        getattr(appointment_form, f).data = getattr(appointment, f)
    return render_template('update_appointment.html', 
                            patient=patient,
                            appointment_form=appointment_form,
                            agenda_form=agenda_form,
                            appointment=appointment)


@app.route('/agenda/add?id=<int:body_id>', methods=['GET', 'POST'])
def add_appointment(body_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    if not body_id:
        checks.quit_patient_file()
        checks.quit_appointment()

    agenda_form = AgendaForm(request.form)
    appointment_form = AppointmentForm(request.form)
    appointment_form.dentist_id.choices = [ (user.id, user.firstname + " " 
                                           + user.lastname ) for user in
                            meta.session.query(users.OdontuxUser).filter(
                            users.OdontuxUser.role == constants.ROLE_DENTIST)\
                            .all()
                                          ]

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
        meta.session.add(new_appointment)
        meta.session.commit()

        # if every thing went fine until now, we just have to add to database
        # agenda data, and we're done.
        args = {}
        args['appointment_id'] = new_appointment.id
        args['starttime'] = starttime
        args['endtime'] = endtime
        new_schedule = schedule.Agenda(**args)
        meta.session.add(new_schedule)
        meta.session.commit()

        session['appointment_id'] = new_schedule.id
        return redirect(url_for('enter_patient_appointment'))

    # the 'GET method' ; 
    # making  "smalls" fields ; not working right now ; why ?
    #for f in get_time_field_list():
    #    getattr(agenda_form, f)(style="width:30px;")
    
    agenda_form.day.data = datetime.date.today()
    
    if session['role'] == constants.ROLE_DENTIST:
        appointment_form.dentist_id.data = session['user_id']
    if session['patient_id']:
        patient = checks.get_patient(session['patient_id'])
        return render_template('add_patient_appointment.html',
                            patient=patient,
                            agenda_form=agenda_form,
                            appointment_form=appointment_form)
    else:
        return render_template('add_appointment.html',
                            agenda_form=agenda_form,
                            appointment_form=appointment_form)

