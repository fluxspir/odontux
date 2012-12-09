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
    if not actual_appointment:
        actual_appointment = patient.appointments[-1]
    
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


@app.route('/event/add?id=<int:patient_id>&rv_id=<int:appointment_id>',
            methods=['GET', 'POST'])
def add_event(patient_id, appointment_id):
    """
    An event is generic and related to more specific : tooth, crown or root,
    which are called in a second time.
    """
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment()
#    if tooth_id:
#        tooth = meta.session.query(teeth.Tooth).filter(
#                teeth.Tooth.id == tooth_id).one()
#    else:
#        tooth = ""

    # Create the forms
    event_form = EventForm(request.form)
    
    if request.method == 'POST' and event_form.validate():
        if event_form.location.data == constants.EVENT_LOCATION_TOOTH[0]:
            return redirect(url_for('add_toothevent', patient.id, 
                                     appointment.id, event_form))

        elif event_form.location.data == constants.EVENT_LOCATION_CROWN[0]:
            return redirect(url_for('add_crownevent', patient.id,
                                     appointment.id, event_form))

        elif event_form.location.data == constants.EVENT_LOCATION_ROOT[0]:
            return redirect(url_for('add_rootevent', patient.id,
                                     apointment.id, event_form))
        else:
            raise Exception(_("This event_location doesn't exist"))

    # Populate select fields, get defaults data for the 'GET' method
    try:
        patient_teeth = meta.session.query(teeth.Tooth).filter(
            teeth.Tooth.mouth_id == patient.mouth.id).all()
    except AttributeError:
        patient_teeth = ""

    if patient_teeth:
        event_form.tooth_id.choices = [(t.id, t.name) for t in 
                            meta.session.query(teeth.Tooth).filter(
                            teeth.Tooth.mouth_id == patient.mouth.id).order_by(
                            teeth.Tooth.name).all() ]
    else:
        event_form.tooth_id.choices = [ ( 0, "") ]
    
    # Prepare the appointment select_field :
    event_form.appointment_id.choices = [(a.id, 
                            str(a.agenda.starttime.date()) + " " + 
                            str(a.agenda.starttime.time()) ) for a in
                            meta.session.query(schedule.Appointment).filter(
                            schedule.Appointment.patient_id == 
                            patient.id).all() ]
    # Default the select field to current appointment :
    if appointment:
        event_form.appointment_id.data = appointment.id

    event_form.location.choices = get_location_choices()
   
    return render_template("add_event.html", patient=patient, 
                                          appointment=appointment,
                                          event_form=event_form)

def checks_if_mouth_exists(patient_id):
    patient = checks.get_patient(patient_id)
    if patient.mouth.id:
        return True
    return False

@app.route('/event_tooth/add?id=<int:patient_id>&rv_id=<int:appointment_id>'
           '&event_form=<event_form>', methods=['GET', 'POST'])
def add_toothevent(patient_id, appointment_id, event_form):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    tooth_event_form = ToothEventForm(request.form)

    if request.method == 'POST' and tooth_event_form.validate():
        # Verify first if we're dealing with a new mouth, and then new tooth
        try:
            mouth_id = patient.mouth.id
        except:
            mouth_id = add_mouth(patient_id)
        # if the user want to add new tooth
        if event_form.new_tooth.data:
            event_form.tooth_id.data = \
            add_tooth(mouth_id, event_form.new_tooth.data)

        event_values = {}
        toothevent_values = {}
        for f in get_event_field_list():
            event_values[f] = getattr(event_form, f).data
        new_event = teeth.Event(**event_values)
        meta.session.add(new_event)
        meta.session.commit()

        tooth_event_form.event_id.data = new_event.id
        for f in get_tooth_event_field_list():
            toothevent_values[f] = getattr(tooth_event_form, f).data
        new_toothevent = teeth.ToothEvent(**toothevent_values)
        meta.session.add(new_toothevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", event_form.tooth_id.data))

    return render_template("add_toothevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_form=event_form,
                            tooth_event_form=tooth_event_form)

@app.route('/event_crown/add?id=<int:patient_id>&rv_id=<int:appointment_id>'
           '&event_form=<event_form>', methods=['GET', 'POST'])
def add_crownevent(patient_id, appointment_id, event_form):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    crown_event_form = CrownEventForm(request.form)

    if request.method == 'POST' and crown_event_form.validate():
        try:
            mouth_id = patient.mouth.id
        except:
            mouth_id = add_mouth(patient_id)
        if event_form.new_tooth.data:
            event_form.tooth_id.data = \
            add_tooth(mouth_id, event_form.new_tooth.data)

        event_values = {}
        crowevent_values = {}
        for f in get_event_field_list():
            event_values[f] = getattr(event_form, f).data
        new_event = teeth.Event(**event_values)
        meta.session.add(new_event)
        meta.session.commit()
        
        crown_event_form.event_id.data = new_event.id
        for f in get_crown_event_field_list():
            crownevent_values[f] = getattr(crown_event_form, f).data
        new_crownevent = teeth.CrownEvent(**crownevent_value)
        meta.session.add(new_crownevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", event_form.tooth_id.data))

    return render_template("add_crownevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_form=event_form,
                            crown_event_form=crown_event_form)

@app.route('/event_root/add?id=<int:patient_id>&rv_id=<int:appointment_id>'
           '&event_form=<event_form>', methods=['GET', 'POST'])
def add_rootevent(patient_id, appointment_id, event_form):
    """ """
    patient = checks.get_patient(patient_id)
    session['appointment_id'] = appointment_id
    appointment = checks.get_appointment()
    root_event_form = RootEventForm(request.form)

    if request.method == 'POST' and root_event_form.validate():
        try:
            mouth_id = patient.mouth.id
        except:
            mouth_id = add_mouth(patient_id)
        if event_form.new_tooth.data:
            event_form.tooth_id.data = \
            add_tooth(mouth_id, event_form.new_tooth.data)

        event_values = {}
        rootevent_values = {}
        for f in get_event_field_list():
            event_values[f] = getattr(event_form, f).data
        new_event = teeth.Event(**event_values)
        meta.session.add(new_event)
        meta.session.commit()
        
        root_event_form.event_id.data = new_event.id
        for f in get_root_event_field_list():
            rootevent_values[f] = getattr(root_event_form, f).data
        new_rootevent = teeth.RootEvent(**rootevent_value)
        meta.session.add(new_rootevent)
        meta.session.commit()

        return redirect(url_for("show_tooth", event_form.tooth_id.data))

    return render_template("add_rootevent.html",
                            patient=patient,
                            appointment=appointment,
                            event_form=event_form,
                            root_event_form=root_event_form)


#    crown_event_form = CrownEventForm(request.form)
#    root_event_form = RootEventForm(request.form)
#
#
#
#                                          crown_event_form=crown_event_form,
#                                          root_event_form=root_event_form)
