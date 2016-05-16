# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

import pdb
from wtforms import ( Form, 
                    TextField, TextAreaField, HiddenField, SelectMultipleField,
                    BooleanField, RadioField, IntegerField, SelectField, 
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
    teeth = TextField(_("Teeth"))
    anatomic_location = SelectField(_("Location"),
                        description='ChangementToothAnatomicLocation()')

    appointment_id = SelectField(_("Appointment"), coerce=int)
    
    description = TextField(_("Description"))
    comments = TextAreaField(_("General comments of this event"))
    pic = TextField(_("pic"))
    color = forms.ColorField(_("color"))

class ToothEventForm(Form):
    choose_state = SelectField(_("Choose state of tooth/teeth"), coerce=int)

class CrownEventForm(Form):
    choose_state = SelectField(_("Choose state of crown(s)"), coerce=int)
    side = SelectMultipleField(_("Sides"), coerce=int)
    tooth_shade = TextField(_("tooth_shade"))

class RootEventForm(Form):
    choose_state = SelectField(_("Choose state of root(s)"), coerce=int)
    root = SelectMultipleField(_("Root"), coerce=int)

class PeriodonteEventForm(Form):
    choose_state = SelectField(_("Choose state of periodonte"), coerce=int)
    bleeding = BooleanField(_('Bleeding'))
    furcation = IntegerField(_('Furcation') ) ## validators <=3 ?
    recession = IntegerField(_('Recession') )
    pocket_depth = IntegerField(_('Pocket depth') )

def get_event_field_list():
    return [ "teeth", "appointment_id", "anatomic_location", "pic",
             "color", "comments", "description" ]

def get_tooth_event_field_list():
    return [ "choose_state" ]

def get_crown_event_field_list():
    return [ "side", "tooth_shade", "choose_state"]

def get_root_event_field_list():
    return [ "choose_state", "root" ]

def get_periodonte_event_field_list():
    return [ "chosse_state", "bleeding", "furcation", "recession", 
            "pocket_depth" ]

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

def _set_tooth_state(tooth_id, state):
    """ """
    tooth = meta.session.query(teeth.Tooth).filter(
                        teeth.Tooth.id == tooth_id).one()
    try:
        tooth.state = state
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
        session['appointment_id'] = actual_appointment.id
    
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


@app.route('/add/event_tooth_located?pid=<int:patient_id>'
                '&aid=<int:appointment_id>', methods=['GET','POST'])
def add_event_tooth_located(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment()

    event_form = EventForm(request.form)
    tooth_event_form = ToothEventForm(request.form)
    crown_event_form = CrownEventForm(request.form)
    root_event_form = RootEventForm(request.form)
    periodonte_event_form = PeriodonteEventForm(request.form)

    event_form.anatomic_location.choices =\
                                    constants.TOOTH_EVENT_LOCATIONS.items()
    event_form.appointment_id.choices = [
            (a.id, str(a.agenda.starttime.date()) 
            + " " + str(a.agenda.starttime.time()) 
            ) for a in meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.patient_id == patient.id)
                        .all() 
            ]

    tooth_event_form.choose_state.choices = [ (id, state[0]) for id, state in
                                            constants.TOOTH_STATES.items() ]
    crown_event_form.choose_state.choices = [ (id, state[0]) for id, state in
                                            constants.CROWN_STATES.items() ]
    crown_event_form.side.choices = [ (id, side[0]) for id, side in 
                                        constants.CROWN_SIDES.items() ]
    root_event_form.choose_state.choices = [ (id, state[0]) for id, state in 
                                        constants.ROOT_STATES.items() ]
    root_event_form.root.choices = [ (id, root[0] ) for id, root in
                                        constants.ROOT_CANALS.items() ]
    periodonte_event_form.choose_state.choices = [ (id, state[0]) 
                        for id, state in constants.PERIODONTE_STATES.items() ]

    if request.method == 'POST' and event_form.validate():
        if event_form.location.data == "tooth":
            if tooth_event_form.validate():
                add_tooth_event()
        elif event_form.location.data == "crown": 
            if crown_event_form.validate():
                add_crown_event()
        elif event_form.location.data == "root":
            if root_event_form.validate():
                add_root_event()
        elif event_form.location.data == "periodonte":
            if periodonte_event_form.validate():
                add_periodonte_event()
        else:
            return redirect(url_for('index'))
    
#    session['location_tooth'] = constants.TOOTH_EVENT_LOCATION_TOOTH
#    session['location_crown'] = constants.TOOTH_EVENT_LOCATION_CROWN
#    session['location_root'] = constants.TOOTH_EVENT_LOCATION_ROOT
#    session['location_periodonte'] = constants.TOOTH_EVENT_LOCATION_PERIODONTE

    if request.method == 'POST':
        clear_form = False
    else:
        clear_form = True

    return render_template('add_event_tooth_located.html',
                    patient=patient, appointment=appointment,
                    event_form=event_form,
                    tooth_event_form=tooth_event_form,
                    crown_event_form=crown_event_form,
                    root_event_form=root_event_form,
                    periodonte_event_form=periodonte_event_form,
                    clear_form=clear_form)

@app.route('/add/event_tooth_loc?pid=<int:patient_id>&aid=<appointment_id>',
            methods=['GET', 'POST'])
def add_event_tooth_loc(patient_id, appointment_id):
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
    
    event_form.anatomic_location.choices =\
                                    constants.TOOTH_EVENT_LOCATIONS.items()
 
    if request.method == 'POST' and event_form.validate():

        # Separation of teeth on which appeared this event;
        # unique teeth separated by ";" or ","
        # sequence of maxilar or mandibular teeth : separated by "-".
        
        teeth_affected_by_event = []
        event_form.teeth.data

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

    return render_template("add_event_tooth_located.html", patient=patient, 
                                          appointment=appointment,
                                          event_form=event_form)

@app.route('/event_tooth/add?pid=<int:patient_id>'
                        '&aid=<int:appointment_id>'
                        '&event_id=<int:event_id>', 
                        methods=['GET', 'POST'])
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
