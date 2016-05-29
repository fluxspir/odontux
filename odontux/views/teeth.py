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

def get_teeth_list(teeth=""):
    """
        entry teeth is a string of tooth or teeth.
        teeth may be separated by ";"
        sequence of teeth is separated by "-" and must be on the same arcade

        return a list o teeth.
        examples : 
         "13" → [ 13 ]
         "13;15" → [ 13, 15 ]
         "13 ; 37" → [ 13, 37" ]
         "26-36" → [ ]
         "stupid_entry; 48" → [ 48 ]
    """
    def _get_tooth(tooth):
        for t in constants.ANATOMIC_LOCATION_TEETH.items():
            if tooth == t[1][0] or tooth == t[1][1]:
                return t[0]
        return None
    
    def _get_teeth_sequence(first_tooth, last_tooth):
        teeth_sequences = (
            constants.PERMANENT_SUPERIOR_TEETH_SEQUENCE,
            constants.PERMANENT_INFERIOR_TEETH_SEQUENCE,
            constants.DECIDUOUS_SUPERIOR_TEETH_SEQUENCE,
            constants.DECIDUOUS_INFERIOR_TEETH_SEQUENCE,
        )
        for sequence in teeth_sequences:
            if first_tooth in sequence and last_tooth in sequence:
                FT_index = sequence.index(first_tooth)
                LT_index = sequence.index(last_tooth)
                teeth_sequence = sequence[FT_index:(LT_index+1)]
                if not teeth_sequence:
                    teeth_sequence = sequence[LT_index:(FT_index+1)]

                return teeth_sequence

        return None

    # remove all whitespace, turns "," into ";" separators
    teeth_group = ''.join(teeth.replace(",", ";").split())
    teeth_group = teeth_group.split(";")
    teeth = []
    for tooth_group in teeth_group:
        if len(tooth_group.split('-')) > 2:
            continue

        elif len(tooth_group.split('-')) == 2:
            first_tooth = _get_tooth(tooth_group.split('-')[0])
            last_tooth = _get_tooth(tooth_group.split('-')[1])
            if not first_tooth or not last_tooth:
                continue
            
            if first_tooth == last_tooth:
                tooth = _get_tooth(first_tooth)
                if tooth:
                    teeth.append(tooth)
                continue

            teeth_sequence = _get_teeth_sequence(first_tooth, last_tooth)
            if not teeth_sequence:
                continue
            for tooth in teeth_sequence:
                teeth.append(tooth)
            continue

        elif len(tooth_group.split('-')) == 1:
            tooth = _get_tooth(tooth_group)
            if tooth:
                teeth.append(tooth)
            continue
        else:
            continue

    return teeth

def get_patient_tooth(patient_id, tooth_codename):
    tooth = (
        meta.session.query(teeth.Tooth)
            .filter(
                teeth.Tooth.patient_id == patient_id,
                teeth.Tooth.codename == tooth_codename
            )
            .one_or_none()
    )
    if not tooth:
        values = {
            'patient_id': patient_id,
            'codename': tooth_codename,
            }
        new_tooth = teeth.Tooth(**values)
        meta.session.add(new_tooth)
        meta.session.commit()

        periodonte_values = {
            'id': new_tooth.id
            }
        new_periodonte = teeth.Periodonte(**periodonte_values)
        meta.session.add(new_periodonte)
        meta.session.commit()

        return new_tooth

    return tooth

def get_patient_periodonte(patient_id, tooth_codename):
    periodonte = (
        meta.session.query(teeth.Periodonte)
            .filter(teeth.Periodonte.id.in_(
                meta.session.query(teeth.Tooth.id)
                    .filter(
                        teeth.Tooth.patient_id == patient_id,
                        teeth.Tooth.codename == tooth_codename
                        )
                    )
                )
            .one_or_none()
    )
    return periodonte

class ToothForm(Form):
    tooth_id = HiddenField(_("id"))
    choose_tooth_state = SelectField(_("Choose state of tooth/teeth"), 
                                                                coerce=int)
    surveillance = BooleanField(_('Surveillance'))

class EventForm(Form):
    event_id = HiddenField(_("ID"))
    teeth = TextField(_("Teeth"))
    appointment_id = SelectField(_("Appointment"), coerce=int)
    description = TextField(_("Description"))
    comment = TextAreaField(_("General comments of this event"))
    color = forms.ColorField(_("color"))
    x_ray = BooleanField(_("x_ray"))
    pic = BooleanField(_("pic"))
    document = BooleanField(_("document"))
    anatomic_location = SelectField(_("Location"), coerce=int,
                        description='ChangementToothAnatomicLocation()')

class CrownEventForm(Form):
    choose_crown_state = SelectField(_("Choose state of crown(s)"), coerce=int)
    side = SelectMultipleField(_("Sides"), coerce=int)
    tooth_shade = TextField(_("tooth_shade"))

class RootEventForm(Form):
    choose_root_state = SelectField(_("Choose state of root(s)"), coerce=int)
    root = SelectMultipleField(_("Root"), coerce=int)

class PeriodonteEventForm(Form):
    choose_periodonte_state = SelectField(_("Choose state of periodonte"), 
                                                                    coerce=int)
    bleeding = BooleanField(_('Bleeding'))
    furcation = IntegerField(_('Furcation') ) ## validators <=3 ?
    recession = IntegerField(_('Recession') )
    pocket_depth = IntegerField(_('Pocket depth') )


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
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in constants.ROLE_DENTIST :
        return redirect(url_for('index'))
    
    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()
    if patient.teeth:
        teeth = [(tooth.id, 
                constants.ANATOMIC_LOCATION_TEETH[tooth.codename], 
                constants.TOOTH_STATES[tooth.state], 
                tooth.surveillance) 
                for tooth in patient.teeth ]
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
    authorized_roles = [ constants.ROLE_DENTIST ] 
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])
    actual_appointment = checks.get_appointment(session['appointment_id'])
    if not actual_appointment:
        actual_appointment = patient.appointments[-1]
        session['appointment_id'] = actual_appointment.id
    
    tooth = ( meta.session.query(teeth.Tooth)
                .filter(teeth.Tooth.id == tooth_id).one() )

    if not tooth in patient.teeth:
        return redirect(url_for('list_teeth'))
    
    events = ( 
        meta.session.query(teeth.Event)
            .filter(
                teeth.Event.tooth_id == tooth_id,
                teeth.Event.appointment_id == schedule.Appointment.id,
                schedule.Appointment.id == schedule.Agenda.appointment_id,
                schedule.Agenda.starttime <= actual_appointment.agenda.starttime
            ).order_by(
                schedule.Agenda.starttime,
                teeth.Event.id
            ).all()
    )

    events_list = []
    for event in events:
        if event.location == constants.TOOTH_EVENT_LOCATION_TOOTH:

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
            for f in constants.TOOTH_STATES:
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

    tooth_form = ToothForm(request.form)
    event_form = EventForm(request.form)
    crown_event_form = CrownEventForm(request.form)
    root_event_form = RootEventForm(request.form)
    periodonte_event_form = PeriodonteEventForm(request.form)

    tooth_form.choose_tooth_state.choices = [ (id, state[0]) 
                            for id, state in constants.TOOTH_STATES.items() ]
    event_form.anatomic_location.choices =\
                                    constants.TOOTH_EVENT_LOCATIONS.items()
    event_form.appointment_id.choices = [
            (a.id, str(a.agenda.starttime.date()) 
            + " " + str(a.agenda.starttime.time()) 
            ) for a in meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.patient_id == patient.id)
                        .join(schedule.Agenda)
                        .order_by(schedule.Agenda.starttime.desc())
                        .all() 
            ]

    crown_event_form.choose_crown_state.choices = [ (id, state[0]) 
                            for id, state in constants.CROWN_STATES.items() ]
    crown_event_form.side.choices = [ (id, side[0]) for id, side in 
                                        constants.CROWN_SIDES.items() ]
    root_event_form.choose_root_state.choices = [ (id, state[0]) 
                            for id, state in constants.ROOT_STATES.items() ]
    root_event_form.root.choices = [ (id, root[0] ) for id, root in
                                        constants.ROOT_CANALS.items() ]
    periodonte_event_form.choose_periodonte_state.choices = [ (id, state[0]) 
                        for id, state in constants.PERIODONTE_STATES.items() ]

    if ( request.method == 'POST' and event_form.validate() 
                                                and tooth_form.validate() ):

        def _update_tooth_datas(tooth, tooth_values):
            tooth.state = tooth_values['state']
            tooth.surveillance = tooth_values['surveillance']
            meta.session.commit()
            
        teeth_to_add = get_teeth_list(event_form.teeth.data)               
        
        tooth_values = {
            'state': tooth_form.choose_tooth_state.data,
            'surveillance': tooth_form.surveillance.data,
        }
        event_values = {
            'appointment_id': appointment_id,
            'description': event_form.description.data,
            'comment': event_form.comment.data,
            'color': event_form.color.data,
            'x_ray': event_form.x_ray.data,
            'pic': event_form.pic.data,
            'document': event_form.document.data,
            'location': event_form.anatomic_location.data,
            'state': tooth_form.choose_tooth_state.data,
        }

        if ( event_form.anatomic_location.data == 
                                        constants.TOOTH_EVENT_LOCATION_TOOTH ):
            
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                _update_tooth_datas(tooth, tooth_values)
                values = event_values
                values['tooth_id'] = tooth.id
                new_tooth_event = teeth.ToothEvent(**values)
                meta.session.add(new_tooth_event)
                meta.session.commit()

        elif ( event_form.anatomic_location.data == 
                                        constants.TOOTH_EVENT_LOCATION_CROWN
        and crown_event_form.validate() ):
            values = {
                'state': crown_event_form.choose_crown_state.data,
                'tooth_shade': crown_event_form.tooth_shade.data,
                }
            values.update(event_values)
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                values.update(event_values)
                values['tooth_id'] = tooth.id
                for side in crown_event_form.side.data:
                    values['side'] = side
                    new_crown_event = teeth.CrownEvent(**values)
                    meta.session.add(new_crown_event)
                    meta.session.commit()

        elif ( event_form.anatomic_location.data == 
                                            constants.TOOTH_EVENT_LOCATION_ROOT
        and root_event_form.validate() ):
            values = {
                'state': root_event_form.choose_root_state.data,
                }
            values.update(event_values)
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                values['tooth_id'] = tooth.id
                for root in root_event_form.root.data:
                    values['root'] = root
                    new_root_event = teeth.RootEvent(**values)
                    meta.session.add(new_root_event)
                    meta.session.commit()

        elif ( event_form.anatomic_location.data == 
                                    constants.TOOTH_EVENT_LOCATION_PERIODONTE
        and periodonte_event_form.validate() ):
            periodonte_values = {
                'state': 
                            periodonte_event_form.choose_periodonte_state.data,
                'bleeding': periodonte_event_form.bleeding.data,
                }
            values = {
                'furcation': periodonte_event_form.furcation.data,
                'recession': periodonte_event_form.recession.data,
                'pocket_depth': periodonte_event_form.pocket_depth.data,
                }
            for tooth in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                add_periodonte_event(tooth, values)

        return redirect(url_for('add_event_tooth_located',
                                patient_id=patient_id,
                                appointment_id=appointment_id))

    if request.method == 'POST':
        clear_form = False
    else:
        clear_form = True

    return render_template('add_event_tooth_located.html',
                    patient=patient, appointment=appointment,
                    tooth_form=tooth_form,
                    event_form=event_form,
                    crown_event_form=crown_event_form,
                    root_event_form=root_event_form,
                    periodonte_event_form=periodonte_event_form,
                    clear_form=clear_form)


