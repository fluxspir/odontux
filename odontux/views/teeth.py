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
                    FieldList, FileField, FormField, SubmitField, validators
                    )
import sqlalchemy
from sqlalchemy.orm import with_polymorphic
from flask import session, render_template, redirect, url_for, request, abort

from gettext import gettext as _

from odontux import constants, checks
from odontux.odonweb import app
from odontux.views import forms
from odontux.models import meta, teeth, schedule, headneck, documents, act
from odontux.views.log import index
from documents import insert_document_in_db


def get_teeth_list(teeth=""):
    """
        entry teeth is a string of tooth or teeth.
        teeth may be separated by ";"
        sequence of teeth is separated by "-" and must be on the same arcade

        return a list o int(teeth).
        examples : 
         "13" → [ 13 ]
         "13;15" → [ 13, 15 ]
         "13 ; 37" → [ 13, 37 ]
         "13-21" → [ 13, 12, 11, 21 ]
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

        gum_values = {
            'id': new_tooth.id
            }
        new_gum = teeth.Gum(**gum_values)
        meta.session.add(new_gum)
        meta.session.commit()

        return new_tooth

    return tooth

def get_patient_gum(patient_id, tooth_codename):
    gum = (
        meta.session.query(teeth.Gum)
            .filter(teeth.Gum.id.in_(
                meta.session.query(teeth.Tooth.id)
                    .filter(
                        teeth.Tooth.patient_id == patient_id,
                        teeth.Tooth.codename == tooth_codename
                        )
                    )
                )
            .one_or_none()
    )
    return gum

class ToothForm(Form):
    tooth_id = HiddenField(_("id"))
    choose_tooth_state = SelectField(_("Choose state of tooth/teeth"), 
                                                                coerce=int)
    surveillance = BooleanField(_('Surveillance'))

class ToothModelForm(Form):
    choose_tooth_model_state = SelectField(_("Choose state of tooth/teeth"), 
                                                                coerce=int)
    surveillance = BooleanField(_('Surveillance'))

class DocumentForm(Form):
    document = FileField(_('Document'))
    document_type = SelectField(_('Type'), coerce=int, 
            choices=[ (doc[0], doc[1][0]) for doc in constants.FILES.items()
                                            if doc[1][1] 
                                            and 'tooth' in doc[1][1] ] )
    add_file = SubmitField(_('Add document'))

class EventForm(Form):
    event_id = HiddenField(_("ID"))
    teeth = TextField(_("Teeth"))
    appointment_id = SelectField(_("Appointment"), coerce=int)
    description = TextField(_("Description"))
    comment = TextAreaField(_("General comments of this event"))
    color = forms.ColorField(_("color"))
    location = SelectField(_("Location"), coerce=int,
                        description='ChangementToothAnatomicLocation()')

class CrownEventForm(Form):
    choose_crown_state = SelectField(_("Choose state of crown(s)"), coerce=int)
    tooth_shade = TextField(_("tooth_shade"))
    is_occlusal = BooleanField(_('occlusal'))
    is_buccal = BooleanField(_('buccal'))
    is_lingual = BooleanField(_('lingual'))
    is_mesial = BooleanField(_('mesial'))
    is_distal = BooleanField(_('distal'))

class RootCanalEventForm(Form):
    choose_root_state = SelectField(_("Choose state of root(s)"), coerce=int)
    is_central = BooleanField(_('Canal central'))
    is_buccal = BooleanField(_('Canal buccal'))
    is_lingual = BooleanField(_('Canal lingual'))
    is_mesial = BooleanField(_('Canal mesial'))
    is_distal = BooleanField(_('Canal distal'))
    is_mesio_buccal = BooleanField(_('Canal mesio buccal'))
    is_mesio_lingual = BooleanField(_('Canal mesio lingual'))
    is_disto_buccal = BooleanField(_('Canal disto buccal'))
    is_disto_lingual = BooleanField(_('Canal disto lingual'))
    is_mesio_buccal_2 = BooleanField(_('Canal mesio buccal 2'))

class PeriodontalEventForm(Form):
    choose_periodontal_state = SelectField(_("Choose state of periodonte"), 
                                                                    coerce=int)
    bleeding = BooleanField(_('Bleeding'))
    furcation = IntegerField(_('Furcation'), [validators.Optional()]) ## validators <=3 ?
    recession = IntegerField(_('Recession'), [validators.Optional()])
    pocket_depth = IntegerField(_('Pocket depth'), [validators.Optional()])
    is_mesio_buccal = BooleanField(_('mesio buccal'))
    is_buccal = BooleanField(_('buccal'))
    is_disto_buccal = BooleanField(_('disto buccal'))
    is_disto_lingual = BooleanField(_('disto lingual'))
    is_lingual = BooleanField(_('lingual'))
    is_mesio_lingual = BooleanField(_('mesio lingual'))

def crown_sides():
    return [ 'is_occlusal', 'is_buccal', 'is_lingual', 'is_mesial', 
                                                                'is_distal' ]

def root_canals():
    return [ 'is_central', 'is_buccal', 'is_lingual', 'is_mesial', 'is_distal',
            'is_mesio_buccal', 'is_mesio_lingual', 'is_disto_buccal', 
            'is_disto_lingual', 'is_mesio_buccal_2' ]

def periodontal_locations():
    return [ 'is_mesio_buccal', 'is_buccal', 'is_disto_buccal',
            'is_disto_lingual', 'is_lingual', 'is_mesio_lingual' ]

@app.route('/patient/teeth?pid=<int:patient_id>')
@app.route('/patient/teeth?pid=<int:patient_id>&aid=<int:appointment_id>')
def list_teeth(patient_id, appointment_id=None):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    teeth = []
    for tooth in patient.teeth:
        teeth.append( ( tooth.id, 
                        constants.ANATOMIC_LOCATION_TEETH[tooth.codename][1], 
                        constants.TOOTH_STATES[tooth.state][0], 
                        tooth.surveillance )
                    )
    return render_template('list_teeth.html', patient=patient, 
                            appointment=appointment, teeth=teeth)

@app.route('/show/tooth?pid=<int:patient_id>&aid=<int:appointment_id>'
            '&tcn=<int:tooth_codename>')
def show_tooth(patient_id, appointment_id, tooth_codename):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    tooth = ( 
        meta.session.query(teeth.Tooth)
            .filter(teeth.Tooth.patient_id == patient_id,
                    teeth.Tooth.codename == tooth_codename
            )
            .one_or_none()
    )
    if tooth:
        gum = (
            meta.session.query(teeth.Gum)
                .filter(teeth.Gum.id == tooth.id).one()
        )
    # we want that appears only events that occured before the 
    # actual_appointment we're in.
    all_event_type = with_polymorphic(teeth.Event, '*')
    events = (
        meta.session.query(all_event_type)
            .filter(
                teeth.Event.tooth_id == tooth.id,
                teeth.Event.appointment_id.in_(
                    meta.session.query(schedule.Agenda.appointment_id)
                        .filter(
                            schedule.Agenda.starttime <=
                                        appointment.agenda.starttime
                        )
                    )
            )
            .join(schedule.Appointment, schedule.Agenda)
            .order_by(
                schedule.Agenda.starttime.desc(),
                teeth.Event.location
            )
            .all()
        )
    document_form = DocumentForm(request.form)
    return render_template('show_tooth.html', patient=patient,
                                              appointment=appointment,
                                              tooth=tooth,
                                              gum=gum,
                                              constants=constants,
                                              events=events,
                                              document_form=document_form)

@app.route('/add/file_to_tooth_event?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&eid=<int:event_id>', methods=['POST'])
def add_file_to_tooth_event(patient_id, appointment_id, event_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    event = ( meta.session.query(teeth.Event)
                .filter(teeth.Event.id == event_id)
                .one()
    )
    document_form = DocumentForm(request.form)
    if document_form.validate():
        document_data = request.files[document_form.document.name].read()
        if document_data:
            new_file = insert_document_in_db(document_data, 
                                document_form.document_type.data, appointment)
            if new_file not in event.files:
                event.files.append(new_file)
                meta.session.commit()

    return redirect(url_for('show_tooth', patient_id=patient_id,
                                        appointment_id=appointment_id,
                                        tooth_codename=event.tooth.codename))

def get_event_forms(appointment=None):
    tooth_form = ToothForm(request.form)
    event_form = EventForm(request.form)
    crown_event_form = CrownEventForm(request.form)
    root_event_form = RootCanalEventForm(request.form)
    periodontal_event_form = PeriodontalEventForm(request.form)

    tooth_form.choose_tooth_state.choices = [ (id, state[0]) 
                            for id, state in constants.TOOTH_STATES.items() ]

    anatomic_locations = constants.TOOTH_EVENT_LOCATIONS.items()
    event_form.location.choices = [ 
            (id, location[0]) for id, location in anatomic_locations ]
    tooth_model_form = ToothModelForm(request.form)
    tooth_model_form.choose_tooth_model_state.choices = [ (id, state[0]) 
                            for id, state in constants.TOOTH_STATES.items() ]

    if appointment:
        event_form.appointment_id.choices = [
            (a.id, str(a.agenda.starttime.date()) 
            + " " + str(a.agenda.starttime.time()) 
            ) for a in meta.session.query(schedule.Appointment)
                        .filter(schedule.Appointment.patient_id == 
                                                        appointment.patient.id)
                        .join(schedule.Agenda)
                        .order_by(schedule.Agenda.starttime.desc())
                        .all() 
        ]
    else:
        event_form.appointment_id.choices = [ (0, '--') ]

    crown_event_form.choose_crown_state.choices = [ (id, state[0]) 
                            for id, state in constants.CROWN_STATES.items() ]
    root_event_form.choose_root_state.choices = [ (id, state[0]) 
                            for id, state in constants.ROOT_STATES.items() ]
    periodontal_event_form.choose_periodontal_state.choices = [ (id, state[0]) 
                        for id, state in constants.PERIODONTAL_STATES.items() ]

    return tooth_form, event_form, crown_event_form, root_event_form,\
                                    periodontal_event_form, tooth_model_form

@app.route('/add/event_tooth_located?pid=<int:patient_id>'
                        '&aid=<int:appointment_id>', methods=['GET','POST'])
def add_event_tooth_located(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    ( tooth_form, event_form, crown_event_form, 
        root_event_form, periodontal_event_form,
        tooth_model_form ) = get_event_forms(appointment)

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
        values = {
            'appointment_id': event_form.appointment_id.data,
            'description': event_form.description.data,
            'comment': event_form.comment.data,
            'color': event_form.color.data,
            'location': event_form.location.data,
            'state': tooth_form.choose_tooth_state.data,
        }

        if ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_TOOTH ):
            
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                _update_tooth_datas(tooth, tooth_values)
                values['tooth_id'] = tooth.id
                new_tooth_event = teeth.ToothEvent(**values)
                meta.session.add(new_tooth_event)
                meta.session.commit()

        elif ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_CROWN
                                            and crown_event_form.validate() ):
            crown_values = {
                'state': crown_event_form.choose_crown_state.data,
                'tooth_shade': crown_event_form.tooth_shade.data,
                }
            values.update(crown_values)
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                values['tooth_id'] = tooth.id
                for side in crown_sides():
                    values[side] = getattr(crown_event_form, side).data
                new_crown_event = teeth.CrownEvent(**values)
                meta.session.add(new_crown_event)
                meta.session.commit()

        elif ( event_form.location.data == 
                                            constants.TOOTH_EVENT_LOCATION_ROOT
                                            and root_event_form.validate() ):
            root_values = {
                'state': root_event_form.choose_root_state.data,
                }
            values.update(root_values)
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                values['tooth_id'] = tooth.id
                for root_canal in root_canals():
                    values[root_canal] =\
                                    getattr(root_event_form, root_canal).data
                new_root_event = teeth.RootCanalEvent(**values)
                meta.session.add(new_root_event)
                meta.session.commit()
        
        elif ( event_form.location.data == 
                                    constants.TOOTH_EVENT_LOCATION_PERIODONTAL
                                    and periodontal_event_form.validate() ):
            periodontal_values = {
                'furcation': periodontal_event_form.furcation.data,
                'recession': periodontal_event_form.recession.data,
                'pocket_depth': periodontal_event_form.pocket_depth.data,
                }
            values.update(periodontal_values)
            del values['state'] # As there is no "state" in PeriodontalEvent
            for tooth_codename in teeth_to_add:
                tooth = get_patient_tooth(patient_id, tooth_codename)
                gum = get_patient_gum(patient_id, tooth_codename)
                # updating gum table
                gum.state = periodontal_event_form.choose_periodontal_state.data
                gum.bleeding = periodontal_event_form.bleeding.data
                # working with event_values for state !
                _update_tooth_datas(tooth, tooth_values)
                values['tooth_id'] = tooth.id
                for site in periodontal_locations():
                    values[site] = getattr(periodontal_event_form, site).data
                new_periodontal_event = teeth.PeriodontalEvent(**values)
                meta.session.add(new_periodontal_event)
                meta.session.commit()

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
                    periodontal_event_form=periodontal_event_form,
                    clear_form=clear_form)

@app.route('/add/new_event_model?cg_id=<int:clinic_gesture_id>'
            '&cid=<int:cotation_id>',                methods=['GET', 'POST'])
def add_event_model(clinic_gesture_id, cotation_id):
    ( tooth_form, event_form, crown_event_form, 
    root_event_form, periodontal_event_form,
    tooth_model_form ) = get_event_forms()
    clinic_gesture = ( meta.session.query(act.ClinicGesture)
        .filter(act.ClinicGesture.id == clinic_gesture_id)
        .one()
    )

    if ( request.method == 'POST' and event_form.validate() 
                                            and tooth_model_form.validate() ):
        values = {
            'description': event_form.description.data,
            'comment': event_form.comment.data,
            'color': event_form.color.data,
            'location': event_form.location.data,
            'tooth_state': tooth_model_form.choose_tooth_model_state.data,
            'surveillance': tooth_model_form.surveillance.data,
        }

        if ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_TOOTH ):

            values['state'] = tooth_model_form.choose_tooth_model_state.data
            new_tooth_event = teeth.ToothEventModel(**values)
            meta.session.add(new_tooth_event)
            meta.session.commit()
            new_event = new_tooth_event

        elif ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_CROWN
                                            and crown_event_form.validate() ):
            crown_values = {
                'state': crown_event_form.choose_crown_state.data,
                'tooth_shade': crown_event_form.tooth_shade.data,
                }
            values.update(crown_values)
            for side in crown_sides():
                values[side] = getattr(crown_event_form, side).data
            new_crown_event = teeth.CrownEventModel(**values)
            meta.session.add(new_crown_event)
            meta.session.commit()
            new_event = new_crown_event

        elif ( event_form.location.data == 
                                            constants.TOOTH_EVENT_LOCATION_ROOT
                                            and root_event_form.validate() ):
            root_values = {
                'state': root_event_form.choose_root_state.data,
                }
            values.update(root_values)
            for root_canal in root_canals():
                values[root_canal] =\
                                getattr(root_event_form, root_canal).data
            new_root_event = teeth.RootCanalEventModel(**values)
            meta.session.add(new_root_event)
            meta.session.commit()
            new_event = new_root_event
#        elif ( event_form.location.data == 
#                                    constants.TOOTH_EVENT_LOCATION_PERIODONTAL
#                                    and periodontal_event_form.validate() ):
#            periodontal_values = {
#                'furcation': periodontal_event_form.furcation.data,
#                'recession': periodontal_event_form.recession.data,
#                'pocket_depth': periodontal_event_form.pocket_depth.data,
#                }
#            values.update(periodontal_values)
#            del values['state'] # As there is no "state" in PeriodontalEvent
#                # updating gum table
#                gum.state = periodontal_event_form.choose_periodontal_state.data
#                gum.bleeding = periodontal_event_form.bleeding.data
#                # working with event_values for state !
#                _update_tooth_datas(tooth, tooth_values)
#                values['tooth_id'] = tooth.id
#                for site in periodontal_locations():
#                    values[site] = getattr(periodontal_event_form, site).data
#                new_periodontal_event = teeth.PeriodontalEventModel(**values)
#                meta.session.add(new_periodontal_event)
#                meta.session.commit()
        
        clinic_gesture.event_model_id = new_event.id
        meta.session.commit()
    
        return redirect(url_for('update_clinic_gesture',
                                        clinic_gesture_id=clinic_gesture_id,
                                        cotation_id=cotation_id))

    return render_template('add_event_model.html',
                    clinic_gesture_id=clinic_gesture_id,
                    event_form=event_form,
                    crown_event_form=crown_event_form,
                    root_event_form=root_event_form,
                    periodontal_event_form=periodontal_event_form,
                    tooth_model_form=tooth_model_form,
                    cotation_id=cotation_id)

@app.route('/update/event_model?cgid=<int:clinic_gesture_id>'
            '&cid=<int:cotation_id>',                methods=['GET', 'POST'])
def update_event_model(clinic_gesture_id, cotation_id):
    def get_event_model_attributes():
        return [ 'description', 'comment', 'color',
                    'location' ]
    def get_tooth_event_model_attributes():
        return [ 'surveillance']
    def get_crown_event_model_attributes():
        crown_event_list = [ 'tooth_shade' ]
        for side in crown_sides():
            crown_event_list.append(side)
        return crown_event_list
    def get_root_event_model_attributes():
        root_event_list = [ ]
        for root_canal in root_canals():
            root_event_list.append(root_canal)
        return root_event_list
    def get_periodontal_event_model_attributes():
        return []
        
    ( tooth_form, event_form, crown_event_form, 
        root_event_form, periodontal_event_form,
        tooth_model_form ) = get_event_forms()

    clinic_gesture = ( meta.session.query(act.ClinicGesture)
        .filter(act.ClinicGesture.id == clinic_gesture_id)
        .one()
    )
    event_model = ( meta.session.query(teeth.EventModel)
        .filter(teeth.EventModel.id == clinic_gesture.event_model_id)
        .one()
    )

    if ( request.method == 'POST' and event_form.validate() 
                                        and tooth_model_form.validate() ):
        
        event_model.tooth_state =\
                                tooth_model_form.choose_tooth_model_state.data
        event_model.surveillance = tooth_model_form.surveillance.data
        for f in get_event_model_attributes():
            setattr(event_model, f, getattr(event_form, f).data)
#        for f in get_tooth_event_model_attributes():
#            setattr(event_model, f, getattr(tooth_model_form, f).data)
        meta.session.commit()

        if ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_TOOTH ):
            pass

        elif ( event_form.location.data == 
                                        constants.TOOTH_EVENT_LOCATION_CROWN
                                            and crown_event_form.validate() ):
            event_model.state = crown_event_form.choose_crown_state.data
            for f in get_crown_event_model_attributes():
                setattr(event_model, f, getattr(crown_event_form, f).data)
                meta.session.commit()

        elif ( event_form.location.data == 
                                            constants.TOOTH_EVENT_LOCATION_ROOT
                                            and root_event_form.validate() ):
            event_model.state = root_event_form.choose_root_state.data
            for f in get_root_event_model_attributes():
                setattr(event_model, f, getattr(root_event_form, f).data)
                meta.session.commit()

        return redirect(url_for('update_clinic_gesture',
                                        clinic_gesture_id=clinic_gesture_id,
                                        cotation_id=cotation_id))

    tooth_model_form.choose_tooth_model_state.data = event_model.tooth_state
    tooth_model_form.surveillance.data = event_model.surveillance
    for f in get_event_model_attributes():
        getattr(event_form, f).data = getattr(event_model, f)
    if event_model.location == constants.TOOTH_EVENT_LOCATION_TOOTH :
        for f in get_tooth_event_model_attributes():
            getattr(tooth_form, f).data = getattr(event_model, f)
    elif event_model.location == constants.TOOTH_EVENT_LOCATION_CROWN:
        crown_event_form.choose_crown_state.data = event_model.state
        for f in get_crown_event_model_attributes():
            getattr(crown_event_form, f).data = getattr(event_model, f)
    elif event_model.location == constants.TOOTH_EVENT_LOCATION_ROOT :
        root_event_form.choose_root_state.data = event_model.state
        for f in get_root_event_model_attributes():
            getattr(root_event_form, f).data = getattr(event_model, f)
                
    return render_template('update_event_model.html',
                    clinic_gesture=clinic_gesture,
                    tooth_model_form=tooth_model_form,
                    event_form=event_form,
                    crown_event_form=crown_event_form,
                    root_event_form=root_event_form,
                    periodontal_event_form=periodontal_event_form,
                    cotation_id=cotation_id)

