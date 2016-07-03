# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

import pdb
from flask import render_template, request, redirect, url_for, session 
from wtforms import (Form, HiddenField, BooleanField, TextAreaField, TextField,
                    IntegerField, SelectField, validators)
from wtforms.fields.html5 import DateField
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date, Time
import datetime
import calendar

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, schedule, administration, users
from odontux.views.forms import TimeField
from odontux.views.log import index

class AppointmentForm(Form):
    patient_id = HiddenField(_('patient_id'))
    dentist_id = SelectField(_('dentist'), coerce=int)
    dental_unit_id = SelectField(_('dental unit'), coerce=int) 
    emergency = BooleanField(_('emergency'))
    reason = TextAreaField(_('reason'), render_kw={'rows': '2', 'cols': '50'})
    diagnostic = TextAreaField(_('diagnostic'),
                                        render_kw={'rows': '2', 'cols': '50'})
    treatment = TextAreaField(_('treatment'),
                                        render_kw={'rows': '2', 'cols': '50'})
    prognostic = TextAreaField(_('prognostic'),
                                        render_kw={'rows': '2', 'cols': '50'})
    advise = TextAreaField(_('advise'), render_kw={'rows': '2', 'cols': '50'})
    next_appointment = TextAreaField(_('next_appointment'),
                                        render_kw={'rows': '2', 'cols': '50'})
    absent = BooleanField(_('absent'))
    excuse = TextField(_('excuse'))

class AgendaForm(Form):
    """ """
    meeting_id = HiddenField('meeting_id')
    appointment_id = HiddenField('appointment_id')
    day = DateField(_('day'), format='%Y-%m-%d', 
                            validators=[validators.Optional()],
                            render_kw={'size': '10px'} )
    starthour = IntegerField(_('h'), [validators.Optional()])
    startmin = IntegerField(_('m'), [validators.Optional()])
    durationhour = IntegerField(_('h'), [validators.Optional()])
    durationmin = IntegerField(_('m'), [validators.Optional()])
    endhour = IntegerField(_('h'), [validators.Optional()])
    endmin = IntegerField(_('m'), [validators.Optional()])

class SummaryAgendaForm(Form):
    day = DateField(_('day'), format='%Y-%m-%d', render_kw={'size': '8px'})
    dentist_id = SelectField(coerce=int,
                                    validators=[validators.Optional()] )
    dental_unit_id = SelectField(coerce=int,
                                    validators=[validators.Optional()] )

class ScheduleNewPatientForm(Form):
    day = DateField(_('Day'))
    dentist_id = HiddenField(_('dentist'))
    dental_unit_id = HiddenField(_('dental unit'))
    date_taker_id = HiddenField(_('date_taker'))
    starttime = TextField(_('Start'), [validators.Required()],
                                        render_kw={'size':'8px'}) 
    duration = TextField(_('Duration'), [validators.Required()],
                                        render_kw={'size':'8px'})
    comment = TextAreaField(_('Name(...)'), [validators.Required()])

class UpdateMeeting(Form):
    meeting_id = HiddenField(_('meeting_id'))
    date_taker_id = HiddenField(_('date_taker'))
    day = DateField(_('Day'))
    dentist_id = SelectField(_('dentist'), coerce=int)
    dental_unit_id = SelectField(_('dental_unit'), coerce=int)
    starttime = TextField(_('Start'), [validators.Required()],
                                        render_kw={'size':'8px'} )
    duration = TextField(_('Duration'), [validators.Required()],
                                        render_kw={'size':'8px'})

class UpdateMeetingNewPatientForm(UpdateMeeting):
    comment = TextAreaField(_('Name(...)'), [validators.Required()])

class UpdateMeetingKnownPatient(UpdateMeeting):
    appointment_id = HiddenField(_('appointment'))
    reason = TextAreaField(_('Reason'))

def get_appointment_field_list():
    return [ "patient_id", "dentist_id", "emergency", "reason", "diagnostic", 
             "treatment", "prognostic", "advise", "next_appointment", "absent",
             "excuse", "dental_unit_id"]

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
    summary_agenda_form = get_summary_agenda_form()
    if request.method == 'POST' :
        return redirect(url_for('display_day', 
                    dateday=summary_agenda_form["day"].data,
                    dentist_id=summary_agenda_form['dentist_id'].data,
                    dental_unit_id=summary_agenda_form['dental_unit_id'].data))

@app.route('/agenda/')
@app.route('/agenda?year=<int:year>&month=<int:month>&day=<int:day>')
def agenda(year=None, month=None, day=None):
    summary_agenda_form = get_summary_agenda_form()
    if year is None and month is None and day is None:
        day_to_emph = datetime.date.today()
    else:
        try:
            if month == 13:
                year = year + 1
                month = 1
            elif month == 0:
                year = year - 1
                month = 12
            else: day_to_emph = datetime.date.today()
            day_to_emph = datetime.date(year, month, day)
        except ValueError:
            day_to_emph = (datetime.date(year, month + 1, 1) - datetime.timedelta(1))
    
    summary_agenda_form.day.data = day_to_emph
    cal = calendar.monthcalendar(day_to_emph.year, day_to_emph.month)
    return render_template('monthly_agenda.html', 
                            summary_agenda_form=summary_agenda_form,
                            day_to_emph=day_to_emph,
                            datetime=datetime,
                            calendar=calendar,
                            cal=cal)
@app.route('/agenda/day?date=<dateday>&dentist=<int:dentist_id>'
            '&dental_unit_id=<int:dental_unit_id>&meeting_id=<int:meeting_id>')
@app.route('/agenda/day?date=<dateday>&dentist=<int:dentist_id>'
            '&dental_unit_id=<int:dental_unit_id>')
def display_day(dateday, dentist_id, dental_unit_id, meeting_id=0):
    """ 
    For viewing all appointments occured the day "dateday",
    and create links for "previous_day" and "next_day"
    
    agenda_day is a dictionnary that contains all details for 
    the day.
     agenda_day = { 
        constants.PERIODS[x]: (
                                (start_time, period_starttime),
                                [ meetings ],
                                (end_time, period_endtime),
                        ),
                                ..., 
        }
    """
    agenda_day = {}
    
    def _time_to_datetime(time, day=datetime.date.today()):
        return datetime.datetime.combine(day, time)

    def _get_first_meeting_time(meeting):
        return datetime.time(meeting.starttime.hour, meeting.starttime.minute)

    def _get_last_meeting_time(meeting):
        return datetime.time(meeting.endtime.hour, meeting.endtime.minute)

    def _get_first_scheduled_time(period, first_patient_schedule_time):
        """ return the first time, and boolean that inform if the time is the 
            theorical real time or not."""
        if period.begin <= first_patient_schedule_time:
            return (period.begin, period.begin)
        return (first_patient_schedule_time, period.begin)

    def _get_last_scheduled_time(period, last_patient_scheduled_time):
        """ see _get_fist_schedule_time()"""
        if period.end >= last_patient_scheduled_time:
            return (period.end, period.end)
        return (last_patient_scheduled_time, period.end)


    def _get_limit_min(period, period_break):
        period_begin = _time_to_datetime(period.begin)
        interval_break_start =\
                        _time_to_datetime(period_break[period.period - 1][1])
        interval_break_end =\
                        _time_to_datetime(period_break[period.period][0])
        interval_break_duration = interval_break_end - interval_break_start
        return (period_begin - (interval_break_duration / 2 )).time()

    def _get_limit_max(period, period_break):
        period_end = _time_to_datetime(period.end)
        interval_break_start =\
                        _time_to_datetime(period_break[period.period][1])
        interval_break_end =\
                        _time_to_datetime(period_break[period.period + 1][0])
        interval_break_duration = interval_break_end - interval_break_start
        return (period_end + (interval_break_duration /2)).time()

    def get_period_schedule(meetings, period, limit_min=None, limit_max=None):
        if period:
            if limit_max:
                meetings = meetings.filter(
                        cast(schedule.Agenda.endtime, Time) < limit_max)
            else:
                meetings = meetings.filter(
                        cast(schedule.Agenda.endtime, Time) < period.end)
            if limit_min:
                meetings = meetings.filter(
                        cast(schedule.Agenda.starttime, Time) > limit_min)
            else:
                meetings = meetings.filter(
                        cast(schedule.Agenda.starttime, Time) > period.begin)
        meetings = meetings.order_by(schedule.Agenda.starttime).all()

        try:
            first_patient_schedule_time = _get_first_meeting_time(meetings[0])
            last_patient_schedule_time = _get_last_meeting_time(meetings[-1])
        except IndexError:
            if not period:
                return ( (None, None), None, (None, None) )
            else:
                return ( (None, period.begin), None, (None, period.end) )
        if not period:  
            return ( (first_patient_schedule_time, None), meetings, 
                        (last_patient_schedule_time, None) 
                    )
        return ( _get_first_scheduled_time( period,
                                            first_patient_schedule_time),
                    meetings, 
                    _get_last_scheduled_time(period, 
                                            last_patient_schedule_time)
                )
 
       
    dateday = datetime.datetime.strptime(dateday,'%Y-%m-%d').date()
    nextday = dateday + datetime.timedelta(days=1)
    prevday = dateday - datetime.timedelta(days=1)
    
    summary_agenda_form = get_summary_agenda_form(dateday)

    dentist = ( meta.session.query(users.OdontuxUser)
                    .filter(users.OdontuxUser.id == dentist_id)
                    .one()
    )
    dental_unit = ( meta.session.query(users.DentalUnit)
                    .filter(users.DentalUnit.id == dental_unit_id)
                    .one()
    )
    day_timesheet = ( meta.session.query(users.TimeSheet)
                        .filter(
                            users.TimeSheet.user_id == dentist.id,
                            users.TimeSheet.weekday == dateday.isoweekday(),
                        )
                        .order_by(users.TimeSheet.begin)
                        .all()
    )
    meetings = ( meta.session.query(schedule.Agenda)
                    .filter(or_(
                        cast(schedule.Agenda.starttime, Date) == (dateday),
                        cast(schedule.Agenda.endtime, Date) == (dateday) 
                        ),
                        schedule.Appointment.dentist_id == dentist_id,
                        schedule.Appointment.dental_unit_id == dental_unit_id
                    )
    )
    
    if not day_timesheet:
        agenda_day[0] = get_period_schedule(meetings, None)
    else:
        period_break = { period.period: (period.begin , period.end) 
                                                for period in day_timesheet }
        for period in day_timesheet:
            limit_min = limit_max = None
            if len(period_break) > period.period * 2:
                limit_max = _get_limit_max(period, period_break)
            if period.period > 1:
                limit_min = _get_limit_min(period, period_break)
            
            agenda_day[period.period] = get_period_schedule(meetings, period,
                                                        limit_min, limit_max )

    
    ## For scheduling new patients
    schedule_new_patient_form = ScheduleNewPatientForm(request.form)
    schedule_new_patient_form.day.data = dateday
    schedule_new_patient_form.dentist_id.data = dentist.id
    schedule_new_patient_form.dental_unit_id.data = dental_unit.id
    schedule_new_patient_form.date_taker_id.data = session['user_id']

    if meeting_id:
        meeting = ( meta.session.query(schedule.Agenda)
                        .filter(schedule.Agenda.id == meeting_id)
                        .one()
        )
        if meeting.appointment_id:
            meeting_form = UpdateMeetingKnownPatientForm(request.form)
            meeting_form.appointment_id.data = meeting.appointment_id
            meeting_form.appointment.reason.data = meeting.appointment.reason
        else:
            meeting_form = UpdateMeetingNewPatientForm(request.form)
            meeting_form.comment.data = meeting.comment
        
        meeting_form.meeting_id.data = meeting.id
        
        dentists = ( meta.session.query(users.OdontuxUser)
                    .filter(users.OdontuxUser.role == constants.ROLE_DENTIST)
                    .all()
        )
        dental_units = meta.session.query(users.DentalUnit).all()
        meeting_form.dentist_id.choices = [ 
                ( dentist.id, dentist.firstname + " " + dentist.lastname )
                                                    for dentist in dentists ]
        meeting_form.dental_unit_id.choices = [ (DU.id, DU.name) 
                                                    for DU in dental_units ]

        meeting_form.dentist_id.data = meeting.dentist_id
        meeting_form.dental_unit_id.data = meeting.dental_unit_id
        meeting_form.date_taker_id.data = session['user_id']
        meeting_form.day.data = meeting.starttime.date()
        meeting_form.starttime.data = meeting.starttime.time()
        duration = ( meeting.endtime - meeting.starttime ).total_seconds()
        meeting_form.duration.data = ( str( int(duration / 3600) ) + ":" +
                                        str( int( (duration % 3600) / 60) )
                                    )

    else:
        meeting = meeting_form = None

    # dateday is return to create links to previous and next day
    return render_template('agenda_day.html',
                            dateday=dateday, nextday=nextday, prevday=prevday,
                            datetime=datetime,
                            calendar=calendar,
                            constants=constants,
                            agenda_day=agenda_day,
                            summary_agenda_form=summary_agenda_form,
                            sched_new_pat_form=schedule_new_patient_form,
                            dentist=dentist, 
                            dental_unit=dental_unit,
                            meeting=meeting,
                            meeting_form=meeting_form
                            )

@app.route('/delete/meeting?meeting_id:<int:meeting_id>'
            '&dentist_id=<int:dentist_id>&dental_unit_id=<int:dental_unit_id>')
def delete_meeting(meeting_id, dentist_id, dental_unit_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    meeting = ( meta.session.query(schedule.Agenda)
                .filter(schedule.Agenda.id == meeting_id)
                .one()
    )
    dateday = meeting.starttime.date().isoformat()
    meta.session.delete(meeting)
    meta.session.commit()
    return redirect(url_for('display_day', dateday=dateday, 
                                            dentist_id=dentist_id, 
                                            dental_unit_id=dental_unit_id))

@app.route('/update/meeting?meeting_id=<int:meeting_id>', methods=['POST'])
def update_meeting(meeting_id):
    def _get_start_and_end_time(meeting_form):
        day = meeting_form.day.data
        time_begin = datetime.time(
                        int(meeting_form.starttime.data.split(":")[0]),
                        int(meeting_form.starttime.data.split(":")[1])
        )
        starttime = datetime.datetime.combine(day, time_begin)
        hour_duration = int(meeting_form.duration.data.split(":")[0])
        minute_duration = int(meeting_form.duration.data.split(":")[1])
        duration = datetime.timedelta(minutes=(
                                    hour_duration * 60 + minute_duration))
        endtime = starttime + duration
        return (starttime, endtime)

    meeting = ( meta.session.query(schedule.Agenda)
                .filter(schedule.Agenda.id == meeting_id).one() )
    if meeting.appointment_id:
        meeting_form = UpdateMeetingKnownPatientForm(request.form)
    else:
        meeting_form = UpdateMeetingNewPatientForm(request.form)

    meeting_form.meeting_id.data = meeting_id
    dentists = ( meta.session.query(users.OdontuxUser)
                .filter(users.OdontuxUser.role == constants.ROLE_DENTIST)
                .all()
    )
    dental_units = meta.session.query(users.DentalUnit).all()
    meeting_form.dentist_id.choices = [ 
            ( dentist.id, dentist.firstname + " " + dentist.lastname )
                                                for dentist in dentists ]
    meeting_form.dental_unit_id.choices = [ (DU.id, DU.name) 
                                                    for DU in dental_units ]
    
    if meeting.appointment_id:
        meeting.reason = meeting_form.reason.data
    else:
        meeting.comment = meeting_form.comment.data

    meeting.date_taker_id = meeting_form.date_taker_id.data
    meeting.dentist_id = meeting_form.dentist_id.data
    meeting.dental_unit_id = meeting_form.dental_unit_id.data
    (starttime, endtime) = _get_start_and_end_time(meeting_form)
    meeting.starttime = starttime
    meeting.endtime = endtime

    meta.session.commit()

    return redirect(url_for('display_day', dateday=meeting_form.day.data,
                            dentist_id=meeting_form.dentist_id.data,
                            dental_unit_id=meeting_form.dental_unit_id.data) )

@app.route('/schedule/new_patient', methods=['POST'])
def schedule_new_patient():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    sched_new_pat_form = ScheduleNewPatientForm(request.form)
    if sched_new_pat_form.validate():
        try:
            hour = int(sched_new_pat_form.starttime.data.split(":")[0])
            minute = int(sched_new_pat_form.starttime.data.split(":")[1])
            h_duration = int(sched_new_pat_form.duration.data.split(":")[0])
            m_duration = int(sched_new_pat_form.duration.data.split(":")[1])
        except (ValueError, IndexError, TypeError):
            return redirect(url_for('display_day', 
                        dateday=sched_new_pat_form.day.data,
                        dentist_id=sched_new_pat_form.dentist_id.data,
                        dental_unit_id=sched_new_pat_form.dental_unit_id.data))

        (year, month, day) = ( sched_new_pat_form.day.data.year,
                                    sched_new_pat_form.day.data.month,
                                    sched_new_pat_form.day.data.day )

        
        values = {
            'dentist_id': sched_new_pat_form.dentist_id.data,
            'dental_unit_id': sched_new_pat_form.dental_unit_id.data,
            'date_taker_id': sched_new_pat_form.date_taker_id.data,
            'starttime': datetime.datetime( year, month, day, hour, minute),
            'endtime': ( datetime.datetime(year, month, day, hour, minute) +
                        datetime.timedelta(hours=h_duration) + 
                        datetime.timedelta(minutes=m_duration)
                        ),
            'comment': sched_new_pat_form.comment.data,

        }
        new_schedule_patient = schedule.Agenda(**values)
        meta.session.add(new_schedule_patient)
        meta.session.commit()

    return redirect(url_for('display_day', 
                        dateday=sched_new_pat_form.day.data,
                        dentist_id=sched_new_pat_form.dentist_id.data,
                        dental_unit_id=sched_new_pat_form.dental_unit_id.data))

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

    patient, appointment = checks.get_patient_appointment(body_id, 
                                                                appointment_id)
    agenda_form = AgendaForm(request.form)
    appointment_form = AppointmentForm(request.form)
    appointment_form.dentist_id.choices = [ (user.id, user.firstname + " " 
                                           + user.lastname ) for user in
                            meta.session.query(users.OdontuxUser).filter(
                            users.OdontuxUser.role == constants.ROLE_DENTIST)\
                            .all()
    ]
    appointment_form.dental_unit_id.choices = [ 
                        (dental_unit.id, dental_unit.name) for dental_unit in
                            meta.session.query(users.DentalUnit).all() 
    ]

    if (request.method == 'POST' and agenda_form.validate()
        and appointment_form.validate() ):
        # get the agenda entry:
        agenda = ( meta.session.query(schedule.Agenda)
            .filter(schedule.Agenda.appointment_id == appointment_id)
            .one()
        )
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
        return redirect(url_for('patient_appointment', 
                                                appointment_id=appointment_id))
    
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

@app.route('/add/appointment')
def add_appointment():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))


@app.route('/add/agenda?pid=<int:body_id>', methods=['GET', 'POST'])
@app.route('/add/agenda?pid=<int:body_id>&meeting_id=<int:meeting_id>',
                                            methods=['GET', 'POST'])
def add_patient_appointment(body_id, meeting_id=0):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    agenda_form = AgendaForm(request.form)
    meeting = ( meta.session.query(schedule.Agenda)
                        .filter(schedule.Agenda.id == meeting_id)
                        .one_or_none()
    )
    if meeting:
        day, starthour, startmin, durationhour, durationmin, endhour, endmin =\
            reverse_agenda_handler(meeting.starttime, meeting.endtime)
        agenda_form.meeting_id.data = meeting.id
        agenda_form.day.data = day
        agenda_form.starthour.data = starthour
        agenda_form.startmin.data = startmin
        agenda_form.durationhour.data = durationhour
        agenda_form.durationmin.data = durationmin
        agenda_form.endhour.data = endhour
        agenda_form.endmin.data = endmin
    
    appointment_form = AppointmentForm(request.form)
    appointment_form.dentist_id.choices = [ (user.id, user.firstname + " " 
                                           + user.lastname ) for user in
                            meta.session.query(users.OdontuxUser).filter(
                            users.OdontuxUser.role == constants.ROLE_DENTIST)\
                            .all()
                                          ]
    appointment_form.dental_unit_id.choices = [ 
                    ( dental_unit.id, dental_unit.name ) for dental_unit in
                                meta.session.query(users.DentalUnit).all() ]
    
    if (request.method == 'POST' and agenda_form.validate()
        and appointment_form.validate() ):
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
        if agenda_form.meeting_id.data:
            appointment_in_agenda = (
                meta.session.query(schedule.Agenda)
                    .filter(schedule.Agenda.id == agenda_form.meeting_id.data)
                    .one_or_none()
            )
            if appointment_in_agenda:
                appointment_in_agenda.appointment_id = new_appointment.id
                meta.session.commit()
                return redirect(url_for('patient_appointment', 
                                            appointment_id=new_appointment.id))

        args = {}
        args['dentist_id'] = new_appointment.dentist_id
        args['date_taker_id'] = new_appointment.dentist_id
        args['dental_unit_id'] = new_appointment.dental_unit_id
        args['appointment_id'] = new_appointment.id
        args['starttime'] = starttime
        args['endtime'] = endtime
        new_schedule = schedule.Agenda(**args)
        meta.session.add(new_schedule)
        meta.session.commit()

        return redirect(url_for('patient_appointment',
                                appointment_id=new_appointment.id))

    if not agenda_form.day.data:
        agenda_form.day.data = datetime.date.today()
    
    if session['role'] == constants.ROLE_DENTIST:
        appointment_form.dentist_id.data = session['user_id']
    patient, appointment = checks.get_patient_appointment(patient_id=body_id)
    return render_template('add_patient_appointment.html',
                            patient=patient,
                            agenda_form=agenda_form,
                            appointment_form=appointment_form)

