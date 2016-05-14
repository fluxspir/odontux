# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

import pdb
from wtforms import (
                    Form, 
                    TextField, TextAreaField,
                    HiddenField, 
                    SelectField, 
                    validators
                    )
import sqlalchemy
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
    new_tooth = TextField(_("New_tooth"))
    appointment_id = SelectField(_("Appointment"), coerce=int)
    location = SelectField(_("Location"), coerce=int)
    color = forms.ColorField(_("color"))
    pic = TextField(_("pic"))
    comments = TextAreaField(_("comments"))

class ToothEventForm(Form):
    toothevent_id = HiddenField(_("ID"))
    event_id = HiddenField(_("event_id"))
    sane = TextField(_("sane"))
    place = TextField(_("place"))
    mobility = TextField(_("mobility"))
    fracture = TextField(_("fracture"))
    absence = TextField(_("absence"))
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
    screwpost = TextField(_("screw post"))

def get_location_choices():
    return [ constants.EVENT_LOCATION_TOOTH, constants.EVENT_LOCATION_CROWN,
             constants.EVENT_LOCATION_ROOT ]

def get_event_field_list():
    return [ "tooth_id", "appointment_id", "location", "pic",
             "color", "comments" ]

def get_tooth_event_field_list():
    return [ "event_id", "sane", "place", "mobility", "fracture",
             "absence", "replaced", "implant" ]

def get_crown_event_field_list():
    return [ "event_id", "side", "tooth_shade", "sealing", "decay",
             "obturation", "crowned", "bridge" ]

def get_root_event_field_list():
    return [ "event_id", "canal", "infected", "abscess", "obturation",
             "inlaycore", "screwpost" ]

def get_tooth_id_choice_list(patient_id):
    patient = checks.get_patient(patient_id)
    try:
        patient_teeth = meta.session.query(teeth.Tooth).filter(
            teeth.Tooth.patient_id == patient.id).all()
    except AttributeError:
        patient_teeth = ""

    if patient_teeth:
        tooth_id_list = [(t.id, t.name) for t in 
                            meta.session.query(teeth.Tooth).filter(
                            teeth.Tooth.patient_id == patient.id).order_by(
                            teeth.Tooth.name).all() ]
    else:
        tooth_id_list = [ ( 0, "") ]
    return tooth_id_list
 
#def add_mouth(patient_id):
#    new_mouth = headneck.Mouth(**{"patient_id": patient_id})
#    meta.session.add(new_mouth)
#    meta.session.commit()
#    return new_mouth.id
#
def add_tooth(patient_id, name, state="s", surveillance=False):
    values = {
        "patient_id": patient_id,
        "name": name.decode("utf_8"),
        "state": state,
        "surveillance": surveillance,
        }
    new_tooth = teeth.Tooth(**values)
    meta.session.add(new_tooth)
    meta.session.commit()
    return new_tooth.id

#def checks_if_mouth_exists(patient_id):
#    patient = checks.get_patient(patient_id)
#    if patient.mouth.id:
#        return True
#    return False
#

def _set_tooth_state(tooth_id, state):
    """ """
    tooth = meta.session.query(teeth.Tooth).filter(
                        teeth.Tooth.id == tooth_id).one()
    tooth_state = {
        "sane": "s",
        "sealing": "x",
        "obturation": "o",
        "crowned": "c",
        "decay": "d",
        "place": "p",
        "mobility": "m",
        "fracture": "f",
        "absence": "a",
        "absent": "a",
        "bridge": "b",
        "resin": "r",
        "implant": "I"
        }
    try:
        tooth.state = tooth_state[state]
        meta.session.commit()
    except KeyError:
        pass


@app.route('/patient/teeth/')
def list_teeth():
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))
    
    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()
    if patient.teeth:
        teeth = [(tooth.id, tooth.name, constants.TOOTH_STATES[tooth.state], 
              tooth.surveillance) for tooth in patient.teeth ]
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
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])
    actual_appointment = checks.get_appointment()
    if not actual_appointment:
        actual_appointment = patient.appointments[-1]
    
    tooth = meta.session.query(teeth.Tooth)\
        .filter(teeth.Tooth.id == tooth_id)\
        .one()

    if not tooth in patient.teeth:
        return redirect(url_for('list_teeth'))
    
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

            try:
                tooth_event = ( meta.session.query(teeth.ToothEvent)
                    .filter(teeth.ToothEvent.event_id == event.id)
                    .one() )
            except sqlalchemy.orm.exc.NoResultFound:
                return redirect(url_for('list_teeth'))
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


@app.route('/add/event_tooth_located?pid=<int:patient_id>&aid=<appointment_id>',
            methods=['GET', 'POST'])
def add_event_tooth_located(patient_id, appointment_id):
    """
    An event is generic and related to more specific : tooth, crown or root,
    which are called in a second time.
    """
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment()
    # Create the forms
    event_form = EventForm(request.form)
    # Populate select fields, get defaults data for the 'GET' method
    event_form.tooth_id.choices = get_tooth_id_choice_list(patient_id)
   
    # Prepare the appointment select_field :
    event_form.appointment_id.choices = [(a.id, 
                            str(a.agenda.starttime.date()) + " " + 
                            str(a.agenda.starttime.time()) ) for a in
                            meta.session.query(schedule.Appointment).filter(
                            schedule.Appointment.patient_id == 
                            patient.id).all() ]
    # Default the select field to current appointment :
    if not appointment:
        appointment = patient.appointments[-1]
        session['appointment_id'] = appointment.id
    event_form.appointment_id.data = appointment.id
    
    event_form.location.choices = get_location_choices()
 
    if request.method == 'POST' and event_form.validate():

        # if the user want to add new tooth
        if event_form.new_tooth.data:
            event_form.tooth_id.data = \
            add_tooth(patient_id, event_form.new_tooth.data)

        event_values = {}
        for f in get_event_field_list():
            event_values[f] = getattr(event_form, f).data
        new_event = teeth.Event(**event_values)
        meta.session.add(new_event)
        meta.session.commit()

        if event_form.location.data == constants.EVENT_LOCATION_TOOTH[0]:
            return redirect(url_for('add_toothevent', patient_id=patient.id, 
                                     appointment_id=appointment.id, 
                                     event_id=new_event.id))

        elif event_form.location.data == constants.EVENT_LOCATION_CROWN[0]:
            return redirect(url_for('add_crownevent', patient_id=patient.id,
                                     appointment_id=appointment.id, 
                                     event_id=new_event.id))

        elif event_form.location.data == constants.EVENT_LOCATION_ROOT[0]:
            return redirect(url_for('add_rootevent', patient_id=patient.id,
                                     appointment_id=appointment.id, 
                                     event_id=new_event.id))
        else:
            raise Exception(_("This event_location doesn't exist"))

    return render_template("add_event.html", patient=patient, 
                                          appointment=appointment,
                                          event_form=event_form)

@app.route('/event_tooth/add?id=<int:patient_id>'
           '&appointment_id=<int:appointment_id>'
           '&event_id=<int:event_id>', methods=['GET', 'POST'])
def add_toothevent(patient_id, appointment_id, event_id):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    tooth_event_form = ToothEventForm(request.form)
    event = meta.session.query(teeth.Event).filter(
                               teeth.Event.id == event_id).one()

    if request.method == 'POST' and tooth_event_form.validate():
        toothevent_values = {}
        tooth_event_form.event_id.data = event_id
        for f in get_tooth_event_field_list():
            toothevent_values[f] = getattr(tooth_event_form, f).data
            if getattr(tooth_event_form, f).data:
                _set_tooth_state(event.tooth_id, f)
        new_toothevent = teeth.ToothEvent(**toothevent_values)
        meta.session.add(new_toothevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", tooth_id=event.tooth_id))

    return render_template("add_toothevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_id=event_id,
                            tooth_event_form=tooth_event_form)

@app.route('/event_crown/add?id=<int:patient_id>'
           '&appointment_id=<int:appointment_id>'
           '&event_id=<int:event_id>', methods=['GET', 'POST'])
def add_crownevent(patient_id, appointment_id, event_id):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    crown_event_form = CrownEventForm(request.form)
    event = meta.session.query(teeth.Event).filter(
                               teeth.Event.id == event_id).one()


    if request.method == 'POST' and crown_event_form.validate():
        crownevent_values = {}
        crown_event_form.event_id.data = event_id
        for f in get_crown_event_field_list():
            crownevent_values[f] = getattr(crown_event_form, f).data
            if getattr(crown_event_form, f).data:
                _set_tooth_state(event.tooth_id, f)
        new_crownevent = teeth.CrownEvent(**crownevent_values)
        meta.session.add(new_crownevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", tooth_id=event.tooth_id))

    return render_template("add_crownevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_id=event_id,
                            crown_event_form=crown_event_form)

@app.route('/event_root/add?id=<int:patient_id>'
           '&appointment_id=<int:appointment_id>'
           '&event_id=<int:event_id>', methods=['GET', 'POST'])
def add_rootevent(patient_id, appointment_id, event_id):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    root_event_form = RootEventForm(request.form)
    event = meta.session.query(teeth.Event).filter(
                               teeth.Event.id == event_id).one()


    if request.method == 'POST' and root_event_form.validate():
        rootevent_values = {} 
        root_event_form.event_id.data = event_id
        for f in get_root_event_field_list():
            rootevent_values[f] = getattr(root_event_form, f).data
        new_rootevent = teeth.RootEvent(**rootevent_values)
        meta.session.add(new_rootevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", tooth_id=event.tooth_id))

    return render_template("add_rootevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_id=event_id,
                            root_event_form=root_event_form)


#    crown_event_form = CrownEventForm(request.form)
#    root_event_form = RootEventForm(request.form)
#
#
#
#                                          crown_event_form=crown_event_form,
#                                          root_event_form=root_event_form)
