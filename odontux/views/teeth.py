# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

from wtforms import (
                    Form, 
                    TextField, TextAreaField,
                    HiddenField, 
                    SelectField, 
                    validators
                    )

from flask import session, render_template, redirect, url_for, request

from gettext import gettext as _

from odontux import constants, checks
from odontux.odonweb import app
from odontux.views import forms
from odontux.models import meta, teeth, schedule, headneck
from odontux.views.log import index


class EventForm(Form):
    event_id = HiddenField(_("ID"))
    tooth_id = SelectField(_("Tooth"), coerce=int)
    appointment_id = SelectField(_("Appointment"), coerce=int)
    location = SelectField(_("Location"), coerce=int)
    color = TextField(_("color"))
    pic = TextField(_("pic"))
    comments = TextAreaField(_("comments"))

class ToothEventForm(Form):
    toothevent_id = HiddenField(_("ID"))
    event_id = HiddenField(_("event_id"))
    sane = TextField(_("sane"))
    place = TextField(_("place"))
    mobility = TextField(_("mobility"))
    fracture = TextField(_("fracture"))
    abscence = TextField(_("abscence"))
    replaced = TextField(_("replaced"))
    implant = TextField(_("implant"))

class CrownEventForm(Form):
    crownevent_id = HiddenField(_("ID"))
    event_id = HiddenField(_("event_id"))
    side = TextField(_("side"))
    tooth_shade = TextField(_("tooth_shade"))
    sealing = TextField(_("sealing"))
    decay = TextField(_("decay"))
    obturation = TextField(_("obturation"))
    crowned = TextField(_("crowned"))
    bridge = TextField(_("bridge"))

class RootEventForm(Form):
    rootevent_id = HiddenField(_("ID"))
    event_id = HiddenField(_("event_id"))
    canal = TextField(_("canal"))
    infected = TextField(_("infected"))
    abscess = TextField(_("abscess"))
    obturation = TextField(_("obturation"))
    inlaycore = TextField(_("inlay core"))

def get_location_choices():
    return [ constants.EVENT_LOCATION_TOOTH, constants.EVENT_LOCATION_CROWN,
             constants.EVENT_LOCATION_ROOT ]

def get_event_field_list():
    return [ "tooth_id", "appointment_id", "location", "pic",
             "color", "comments" ]

def get_tooth_event_field_list():
    return [ "event_id", "sane", "place", "mobility", "fracture",
             "abscence", "replaced", "implant" ]

def get_crown_event_field_list():
    return [ "event_id", "side", "tooth_shade", "sealing", "decay",
             "obturation", "crowned", "bridge" ]

def get_root_event_field_list():
    return [ "event_id", "canal", "infected", "abscess", "obturation",
             "inlaycore" ]


def add_mouth(patient_id):
    new_mouth = headneck.Mouth(**{"patient_id": patient_id})
    meta.session.add(new_mouth)
    meta.session.commit()
    return new_mouth.id

def add_tooth(mouth_id, name, state="s", surveillance=False):
    values = {
        "mouth_id": mouth_id,
        "name": name.decode("utf_8"),
        "state": state,
        "surveillance": surveillance,
        }
    new_tooth = teeth.Tooth(**values)
    meta.session.add(new_tooth)
    meta.session.commit()
    return new_tooth.id


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
    actual_appointment = checks.get_appointment()
    
    tooth = meta.session.query(teeth.Tooth)\
        .filter(teeth.Tooth.id == tooth_id)\
        .one()

    if not tooth in patient.mouth.teeth:
        return redirect(url_for('index'))
    
    events = ( meta.session.query(teeth.Event)
                    .filter(
                        teeth.Event.tooth_id == tooth_id
                        )
                    .filter(
                        teeth.Event.appointment_id ==
                        schedule.Appointment.id
                        )
                    .filter(
                        schedule.Appointment.id == 
                        schedule.Agenda.appointment_id
                        )
                    .filter(
                        schedule.Agenda.starttime <= 
                        actual_appointment.agenda.starttime
                        )
                    .order_by(
                        schedule.Agenda.starttime
                        )
                    .order_by(
                        teeth.Event.id
                        )
             ).all()

    events_list = []
    for event in events:
        if event.location == constants.EVENT_LOCATION_TOOTH[0]:

            tooth_event = ( meta.session.query(teeth.ToothEvent)
                .filter(teeth.ToothEvent.event_id == event.id)
                .one() )
            appointment = (meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id == event.appointment_id)
                .one() )

            event_description = []
            for f in constants.TOOTH_EVENT_ATTRIBUTES:
                if getattr(tooth_event, f):
                    event_name = f
                    event_data = getattr(tooth_event, f)
                    event_description.append( (event_name, event_data) )

            events_list.append( (event, "tooth", tooth_event, 
                                 event_description, appointment) )

        elif event.location == constants.EVENT_LOCATION_CROWN[0]:

            crown_event = ( meta.session.query(teeth.CrownEvent)
                .filter(teeth.CrownEvent.event_id == event.id)
                .one() )
            appointment = (meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id == event.appointment_id)
                .one() )

            event_description = []
            for f in constants.CROWN_EVENT_ATTRIBUTES:
                if getattr(crown_event, f):
                    event_name = f
                    event_data = getattr(crown_event, f)
                    event_description.append( (event_name, event_data) )
            
            events_list.append( (event, "crown", crown_event,
                                 event_description, appointment) )

        elif event.location == constants.EVENT_LOCATION_ROOT[0]:

            root_event = ( meta.session.query(teeth.RootEvent)
                .filter(teeth.RootEvent.event_id == event.id)
                .one() )
            appointment = (meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id == event.appointment_id)
                .one() )
            
            event_description = []
            for f in constants.ROOT_EVENT_ATTRIBUTES:
                if getattr(root_event, f):
                    event_name = f
                    event_data = getattr(root_event, f)
                    event_description.append( (event_name, event_data) )

            events_list.append( (event, "root", root_event, 
                                 event_description, appointment) )

        else:
            raise Exception(_("Unknown event location"))
 
    return render_template('show_tooth.html', patient=patient,
                                              appointment=actual_appointment,
                                              tooth=tooth,
                                              events_list=events_list)


@app.route('/tooth_event/add?id=<int:patient_id>&rv_id=<int:appointment_id'
           '&tooth_id=<tooth_id>')
def add_event(patient_id, appointment_id, tooth_id):
    """ """
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment()
    if not tooth_id == " ":
        tooth = meta.session.query(teeth.Tooth).filter(
                teeth.Tooth.id == tooth_id).one()

    event_form = EventForm(request.form)
    tooth_event_form = ToothEventForm(request.form)
    crown_event_form = CrownEventForm(request.form)
    root_event_form = RootEventForm(request.form)

    event_form.appointment_id.choices = [(a.id, a.agenda.starttime.date()
                            + " " + a.agenda.startime.time() ) for a in
                            meta.session.query(schedule.Appointment).filter(
                            schedule.Appointment.id == appointment.id).all() 
                                            ]
    event.form.location.choices = get_location_choices()
    
