# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for, jsonify
import sqlalchemy
from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import ( meta, act, schedule, administration, traceability,
                            assets, teeth, compta)
from odontux.views import cotation as views_cotation

from odontux.views.log import index
#from odontux.views.patient import list_acts

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, IntegerField, validators,
                     FieldList, FormField, SubmitField)
from odontux.views.forms import ColorField
from decimal import Decimal

def get_code_list():
    return [ gesture.code for gesture in meta.session.query(act.Gesture).all() ]

class SpecialtyForm(Form):
    name = TextField('name', [validators.Required(), 
                     validators.Length(min=1, max=20, 
                     message=_("Must be less than 20 characters"))])
    color = ColorField('color')

class GestureForm(Form):
    specialty_id = SelectField('specialty', coerce=int)
    code = TextField('code')
    alias = TextField('alias')
    name = TextField('name')
    color = ColorField('color')

class AppointmentGestureReferenceForm(Form):
    anatomic_location = IntegerField(_('Teeth / Anatomic location'), 
                                            [validators.Optional()] )
    healthcare_plan_id = SelectField(_('Healthcare plan'), coerce=int,
                                    description='UpdateGesture()')
    gesture_id = SelectField(_('Choose gesture in list'), coerce=int,
                                        description='UpdateCodePrice()')
    code = TextField(_('Code'), validators=[validators.Optional(),
                validators.AnyOf(get_code_list())])
    price = DecimalField(_('Price'), [validators.Optional()])
    majoration = SelectField(_('Majoration'), coerce=int)

class PriceForm(Form):
    gesture_id = HiddenField(_('gesture_id'))
    healthcare_plan_id = HiddenField(_('healthcare_plan_id'))
    price = DecimalField(_('Price'), [validators.Optional()],
                        render_kw={'size':'6px'})

class AssetSterilizedUsedForm(Form):
    asset_sterilized_id = IntegerField(_('Asset sterilized id'),
                                            [validators.Required()] )

class MaterioVigilanceForm(Form):
#    def max_quantity(material_id):
#        max_quantity = ( meta.session.query(assets.Material)
#            .filter(assets.Material.id == material_id)
#            .one()[0]
#        )
#        return max_quantity
    material_id = HiddenField(_('Material id'))
    old_quantity_used = HiddenField(_('Old Quantity Used'))
    new_quantity_used = DecimalField(_('Quantity used'), 
#                                [validators.NumberRange(min=0)],
                                [validators.Optional()],
                                render_kw={'size':4})
    material_data = HiddenField(_('material_data'))

class MaterioVigilanceUsedForm(Form):
    materials_used = FieldList(FormField(MaterioVigilanceForm))
    update = SubmitField(_('Update'))

def get_specialty_field_list():
    return [ "name", "color" ]

def get_gesture_field_list():
    return [ "specialty_id", "code", "alias", 
             "name", "color" ]
def get_appointmentgesturereference_field_list():
    return [ "appointment_id", "gesture_id", "anatomic_location", 
            'healthcare_plan_id', "price", "majoration" ]

def get_specialty_choice_list():
    return [ (choice.id, choice.name) for choice in 
                                    meta.session.query(act.Specialty).all() ]

def get_appointment_choices(patient_id):
    appointments = ( meta.session.query(schedule.Appointment)
        .filter(schedule.Appointment.patient_id == patient_id)
        .join(schedule.Agenda)
        .order_by(schedule.Agenda.starttime.desc())
        .all()
    )
    return [ (appointment.id, appointment.agenda.starttime) for appointment in
                                                                appointments ]

def get_gesture_choices():
    gestures = ( meta.session.query(act.Gesture)
                    .order_by(
                        act.Gesture.specialty_id,
                        act.Gesture.alias
                    ).all()
    )
    return [ (gesture.id, gesture.alias) for gesture in gestures ]

def get_majoration_choices():
    majorations =  meta.session.query(compta.Majoration).all()
    maj = [ (0, _('None') ) ] + [ (m.id, m.reason + " " + 
                                    str(m.percentage) + "%") 
                                                        for m in majorations ]
    return maj

def create_cotation_dictionnary(patient):
    cotations = {}
    for healthcare_plan in patient.hcs:
        cotations[healthcare_plan.id] = {}
        for cotation in healthcare_plan.cotations:
            if not cotation.active:
                continue
            cotations[healthcare_plan.id][cotation.gesture_id] =\
                            ( cotation.gesture.name, cotation.gesture.code, 
                                                        str(cotation.price) )
    return cotations

@app.route('/portal/gesture/')
def portal_gesture():
    return render_template('portal_gestures.html')

@app.route('/specialty/')
@app.route('/specialties/')
def list_specialty(ordering=[]):
    query = meta.session.query(act.Specialty)
    if not ordering:
        ordering = [act.Specialty.id]
    for order in ordering:
        query = query.order_by(order)
    specialties = query.all()
    return render_template('list_specialty.html', specialties=specialties)

@app.route('/add/specialty/', methods=['GET', 'POST'])
def add_specialty():
    form = SpecialtyForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in get_specialty_field_list() }
        new_specialty = act.Specialty(**args)
        meta.session.add(new_specialty)
        meta.session.commit()
        return redirect(url_for('list_specialty'))
    return render_template('add_specialty.html', form=form)

@app.route('/act/update_specialty/id=<int:specialty_id>/', 
            methods=['GET', 'POST'])
def update_specialty(specialty_id):
    try:
        specialty = meta.session.query(act.Specialty).filter\
              (act.Specialty.id == specialty_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('list_specialty'))

    form = SpecialtyForm(request.form)

    if request.method == 'POST' and form.validate():
        specialty.name = form.name.data
        specialty.color = form.color.data
        meta.session.commit()
        return redirect(url_for('list_specialty'))
    

    return render_template('update_specialty.html', form=form, 
                            specialty=specialty)

@app.route('/delete/specialty?id=<int:specialty_id>')
def delete_specialty(specialty_id):
    specialty = meta.session.query(act.Specialty).filter(
                    act.Specialty.id == specialty_id).one()
    meta.session.delete(specialty)
    meta.session.commit()
    return redirect(url_for('list_specialty'))
        

#####
# Gestures
#####

@app.route('/list/gesture')
@app.route('/list/gesture?kwds=<keywords>&order=<ordering>')
def list_gesture(keywords="", ordering=""):
    """ The target is to display dentist's gesture, describing it, its values.
    Looking in Gesture table, we may decide to print only 
        acts from one specialty
        then filter by keyword
        ordering the printing
    
    The result will be a list of tuples :
     ( gesture, specialty, cotat, plan )
    """
    keywords = keywords.encode("utf_8").split()
    ordering = ordering.split()
    # Get the acts list, named as "gesture", because it is the gesture
    # the dentist make in the patient mouth.
    query = meta.session.query(act.Gesture)
    # If we only need ones of a specialty : 
    if request.form and request.form['specialty']:
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == request.form['specialty'].one())
            query = query.filter(act.Gesture.specialty_id == specialty.id)
        except sqlalchemy.orm.exc.NoResultFound:
            pass
    # Filter by keywords
    if keywords:
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                act.Gesture.alias.ilike(keyword),
                act.Gesture.name.ilike(keyword),
                act.Gesture.code.ilike(keyword),
                (and_(
                    act.Gesture.specialty_id == act.Specialty.id,
                    act.Specialty.name.ilike(keyword)
                    )
                )
            ))
    # We want to order the result to find what we are looking for more easily
    if not ordering:
        ordering = [ act.Gesture.specialty_id, act.Gesture.alias ]
    for o in ordering:
        query = query.order_by(o)
    gestures = query.all()

    gestures_list = []
    for gesture in gestures:
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == gesture.specialty_id)\
                .one()
        except sqlalchemy.orm.exc.NoResultFound:
            specialty = ""
        gestures_list.append( (gesture, specialty) )
    return render_template('list_gesture.html', 
                            gestures_list=gestures_list)

@app.route('/add/gesture/', methods=['GET', 'POST'])
def add_gesture():
    """ """
    # TODO  BECAUSE DIFFICULT TO MAKE IT "PERFECT"
    form = GestureForm(request.form)
    form.specialty_id.choices = get_specialty_choice_list()
    if request.method == 'POST' and form.validate():
        values = {}
        values['specialty_id'] = form.specialty_id.data
        values['code'] = form.code.data
        values['alias'] = form.alias.data
        values['name'] = form.name.data
        values['color'] = form.color.data
        new_gesture = act.Gesture(**values)
        meta.session.add(new_gesture)
        meta.session.commit()
        return redirect(url_for('list_gesture'))
    return render_template('/add_gesture.html', form=form)

@app.route('/update/gesture?gid=<int:gesture_id>/', methods=['GET', 'POST'])
def update_gesture(gesture_id):
    gesture = meta.session.query(act.Gesture).filter\
              (act.Gesture.id == gesture_id).one()
    if not gesture:
        return redirect(url_for('list_gesture'))
    try:
        specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == gesture.specialty_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        specialty=""

    gesture_form = GestureForm(request.form)
    gesture_form.specialty_id.choices = get_specialty_choice_list()
    
    #TODO (130202 : je me demande ce que je voulais faire à ce todo qui date 
    # d'on ne sait quand...
    # (update 160504 : toujours pas d'idée)
    
    if request.method == 'POST' and gesture_form.validate():
        for f in get_gesture_field_list():
            setattr(gesture, f, getattr(gesture_form, f).data)
        meta.session.commit()
        return redirect(url_for('view_gesture', 
                                    gesture_id=gesture_id))

    # For the GET method
    for f in get_gesture_field_list():
        getattr(gesture_form, f).data = getattr(gesture, f)

    specialty_form = SpecialtyForm(request.form)
    return render_template('/update_gesture.html', 
                            gesture_form=gesture_form, 
                            specialty_form=specialty_form,
                            gesture=gesture
                            )

@app.route('/view/gesture?id=<int:gesture_id>')
def view_gesture(gesture_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    gesture = ( meta.session.query(act.Gesture)
                    .filter(act.Gesture.id == gesture_id)
                    .one() 
            )

    price_forms = []
    for cotation in gesture.cotations:
        if cotation.active == False:
            continue
        form = PriceForm(request.form)
        form.gesture_id.data = gesture.id
        form.healthcare_plan_id.data = cotation.healthcare_plan_id
        
        if cotation.price:
            form.price.data = cotation.price
        else:
            form.price.data = 0
        price_forms.append((cotation, form))

    healthcare_plans_not_in_gesture = (
        meta.session.query(act.HealthCarePlan)
        .filter(or_(
            # Gesture that never had the cotation
            ~act.HealthCarePlan.cotations.any(
                act.Cotation.gesture_id == gesture.id),
            # Gesture that already were associated with the cotation
            act.HealthCarePlan.cotations.any(
                act.Cotation.id.in_(
                    meta.session.query(act.Cotation.id)
                        .filter(
                            act.Cotation.gesture_id == gesture.id,
                            act.Cotation.active == False
                        )
                    )
                )
            )
        ).all()
    )
    return render_template('view_gesture.html', gesture=gesture,
            price_forms=price_forms,
            healthcare_plans_not_in_gesture=healthcare_plans_not_in_gesture)

@app.route('/add/healthcare_plan_to_gesture?gest=<int:gesture_id>'
            '&HP=<int:healthcare_plan_id>')
def add_healthcare_plan_to_gesture(gesture_id, healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    cotation = (
        meta.session.query(act.Cotation)
            .filter(act.Cotation.gesture_id == gesture_id,
                    act.Cotation.healthcare_plan_id == healthcare_plan_id
                )
            .one_or_none()
        )
    if cotation:
        cotation.active = True
    else:
        values = {
            'gesture_id': gesture_id,
            'healthcare_plan_id': healthcare_plan_id
        }
    
        new_cotation = act.Cotation(**values)
        meta.session.add(new_cotation)
    meta.session.commit()
    return redirect(url_for('view_gesture', gesture_id=gesture_id))

@app.route('/remove/healthcare_plan_from_gesture?gest=<int:gesture_id>'
            '&HP=<int:healthcare_plan_id>')
def remove_healthcare_plan_from_gesture(gesture_id, healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    cotation = ( 
        meta.session.query(act.Cotation)
            .filter(act.Cotation.gesture_id == gesture_id,
                    act.Cotation.healthcare_plan_id == healthcare_plan_id
                )
            .one()
        )
    cotation.active = False
    meta.session.commit()
    return redirect(url_for('view_gesture', gesture_id=gesture_id))

@app.route('/update/cotation', methods=['POST'])
def update_cotation():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    price_form = PriceForm(request.form)

    if price_form.validate():
        cotation = (
            meta.session.query(act.Cotation)
                .filter(act.Cotation.gesture_id== price_form.gesture_id.data,
                        act.Cotation.healthcare_plan_id ==
                                        price_form.healthcare_plan_id.data
                    )
                .one()
            )
        cotation.price = price_form.price.data
        meta.session.commit()
        
    return redirect(url_for('view_gesture', 
                            gesture_id=price_form.gesture_id.data))

@app.route('/add/gesture?pid=<int:patient_id>&_id=<int:appointment_id>', 
                                                    methods=['GET', 'POST'])
def add_administrativ_gesture(patient_id, appointment_id):
    """
        On the GET method, all possible gesture are sent,
        only healthcare_plans that patient belong to are sent,
        and a cotation_dict that we'll be use to select what will be 
        javascript's displayed.
    """
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_ASSISTANT,
                        constants.ROLE_NURSE ]
    if session['role'] not in authorized_roles:
        return abort(403)
    # Prepare the formulary dealing with the act of adding an administrativ
    # gesture
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    appointment_gesture_form = AppointmentGestureReferenceForm(request.form)

    # Patient is linked to some healthcare plans. Won't be included other plans
    appointment_gesture_form.healthcare_plan_id.choices = [
                    (hcs.id, hcs.name) for hcs in patient.hcs ]
    # Create a list of all existing gestures.
    appointment_gesture_form.gesture_id.choices = [
        (gesture.id, gesture.name) for gesture in 
                                    meta.session.query(act.Gesture).all() ]
    appointment_gesture_form.gesture_id.choices.insert( 0, (0, ""))
    appointment_gesture_form.majoration.choices =\
                                            get_majoration_choices()

    if request.method == 'POST' and appointment_gesture_form.validate():
        # if gesture_form comes with a code, upade form.gesture_id with the 
        # code provided by user. 
        if appointment_gesture_form.code.data:
            gesture = (
                meta.session.query(act.Gesture)
                    .filter(or_(
                    act.Gesture.code == appointment_gesture_form.code.data,
                    act.Gesture.id == appointment_gesture_form.gesture_id.data)
                    ).one_or_none()
            )
        if not gesture:
            # TODO : redirect error + message
            return redirect(url_for('index'))

        values = {}
        # In the appointment_gesture_reference table, we'll store
        # appointment, act, and anatomic_location
        values['appointment_id'] = appointment.id
        values['gesture_id'] = gesture.id
        values['healthcare_plan_id'] =\
                            appointment_gesture_form.healthcare_plan_id.data

        if ( 
            appointment_gesture_form.anatomic_location.data not in 
                                constants.ANATOMIC_LOCATION_SOFT_TISSUES.keys()
            and appointment_gesture_form.anatomic_location.data not in 
                                constants.ANATOMIC_LOCATION_TEETH_SET.keys()
            and appointment_gesture_form.anatomic_location.data not in
                                constants.ANATOMIC_LOCATION_TEETH.keys() ):
            # TODO redirect error + message
            return redirect(url_for('index'))
        if appointment_gesture_form.anatomic_location.data is None:
            appointment_gesture_form.anatomic_location.data = 0
        values['anatomic_location'] =\
                                appointment_gesture_form.anatomic_location.data

        values['price'] = appointment_gesture_form.price.data
        if not appointment_gesture_form.price.data:
            values['paid'] = True

        new_technical_gesture = act.AppointmentGestureReference(**values)
        meta.session.add(new_technical_gesture)
        meta.session.commit()

        invoice = gnucash_handler.GnuCashInvoice(patient.id, appointment_id, 
                                                        appointment.dentist_id)
        invoice_id = invoice.add_act(gesture.name, values['price'], 
                                                        new_technical_gesture.id)

        new_technical_gesture.invoice_id = invoice_id
        meta.session.commit()

        return redirect(url_for("add_administrativ_gesture", 
                        patient_id=patient_id, appointment_id=appointment_id))

    cotations = create_cotation_dictionnary(patient)
    return render_template("add_administrativ_gesture.html",
                            patient=patient,
                            appointment=appointment,
                            cotations=cotations,
                            admin_gesture_form=appointment_gesture_form)

@app.route('/remove/gesture?pid=<int:patient_id>'
           '&aid=<int:appointment_id>&gid=<int:gesture_id>'
           '&code=<code>')
def remove_administrativ_gesture(patient_id, appointment_id, gesture_id, code):
    """ """
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_ASSISTANT,
                        constants.ROLE_NURSE ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    gesture = meta.session.query(act.AppointmentGestureReference).filter(
            act.AppointmentGestureReference.id == gesture_id).one()

    invoice = gnucash_handler.GnuCashInvoice(patient.id, appointment_id, 
                                                     appointment.dentist_id)
    remove_from_gnucash = invoice.remove_act(gesture_id)

    meta.session.delete(gesture)
    meta.session.commit()
    return redirect(url_for('patient_appointment', 
                                        appointment_id=appointment_id))


@app.route('/sterilized_asset_used?pid=<int:patient_id>'
            '$aid=<int:appointment_id>', methods=['GET','POST'])
def sterilized_asset_used(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_ASSISTANT,
                    constants.ROLE_NURSE ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    asset_sterilized_form = AssetSterilizedUsedForm(request.form)

    if request.method == 'POST' and asset_sterilized_form.validate():
        asset_used = (
            meta.session.query(traceability.AssetSterilized)
                .filter(traceability.AssetSterilized.id == 
                            asset_sterilized_form.asset_sterilized_id.data)
                .one()
            )
        asset_used.appointment_id = appointment_id
        asset_used.sealed = False
        if asset_used.kit_id:
            asset_used.kit.end_of_use = appointment.agenda.endtime
            asset_used.kit.end_use_reason =\
                                        constants.END_USE_REASON_NATURAL_END
            asset_used.kit.appointment_id = appointment_id
        meta.session.commit()
        return redirect(url_for('sterilized_asset_used', 
                                patient_id=patient_id,
                                appointment_id=appointment_id) )

    assets_used = (
        meta.session.query(traceability.AssetSterilized)
            .filter(traceability.AssetSterilized.appointment_id == 
                                                                appointment_id)
            .all()
        )
    manufacture_sterilized_assets_used = (
        meta.session.query(assets.Device)
            .filter(assets.Device.appointment_id == appointment_id)
            .all()
        )
    material_used = (
        meta.session.query(assets.Material)
        .filter(assets.Material.id.in_(
            meta.session.query(assets.Material.id)
            .filter(traceability.MaterioVigilance.appointments.has(
                schedule.Appointment.id == appointment_id
                    )
                )
            )
        ).all()
    )
    for asset in manufacture_sterilized_assets_used:
        assets_used.append(asset)
    return render_template('sterilized_asset_used.html', patient=patient,
                            appointment=appointment,
                            asset_sterilized_form=asset_sterilized_form,
                            assets_used=assets_used,
                            material_used=material_used)

@app.route('/add/manufacture_sterilized_asset_to_appointment?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&asset_id=<int:asset_id>')
def add_manufacture_sterilized_asset_to_appointment(patient_id,
                                        appointment_id, asset_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    asset = (
        meta.session.query(assets.Device)
            .filter(assets.Device.id == asset_id)
            .one()
        )
    asset.appointment_id = appointment_id
    meta.session.commit()
    return redirect(url_for('choose_manufacture_sterilized_assets',
                        patient_id=patient_id, appointment_id=appointment_id))

@app.route('/choose/manufacture_sterilized_assets?pid=<int:patient_id>'
            '&aid=<int:appointment_id>')
def choose_manufacture_sterilized_assets(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_ASSISTANT,
                        constants.ROLE_NURSE ]
    if session['role'] not in authorized_roles:
        return redirecs(url_for('index'))
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    assets_manufacture_sterilized = (
        meta.session.query(assets.Device)
            .filter(
                assets.Device.appointment_id.is_(None),
                assets.Device.start_of_use.isnot(None)
                )
            .filter(assets.Device.id.in_(
                meta.session.query(assets.Device.id)
                    .filter(assets.Device.asset_category.has(
                        assets.AssetCategory.manufacture_sterilization.is_(True)
                        )
                    )
                )
            )
            .all()
        )
    return render_template('choose_manufacture_sterilized_assets_used.html', 
                patient=patient, appointment=appointment,
                assets_manufacture_sterilized=assets_manufacture_sterilized)

@app.route('/add/material_used_in_appointment?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&mid=<int:material_id>')
def add_material_used_in_appointment(patient_id, appointment_id, material_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    material_used = ( 
        meta.session.query(traceability.MaterioVigilance)
            .filter(
                traceability.MaterioVigilance.material_id == material_id,
                traceability.MaterioVigilance.appointment_id == appointment_id)
            .one_or_none()
    )
    if material_used:
        return redirect(url_for('view_material_used_in_appointment',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))
    material = ( meta.session.query(assets.Material)
                .filter(assets.Material.id == material_id)
                .one()
    )

    material_used_values = {
        'material_id': material_id,
        'appointment_id': appointment_id,
        'quantity_used': material.asset_category.automatic_decrease,
    }
    new_material_used = traceability.MaterioVigilance(**material_used_values)
    meta.session.add(new_material_used)

    material.actual_quantity -= new_material_used.quantity_used

    meta.session.commit()
    return redirect(url_for('view_material_used_in_appointment',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))

@app.route('/remove/material_used_in_appointment?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&mid=<int:material_id>')
def remove_material_used_in_appointment(patient_id, appointment_id, 
                                                                material_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    material_used = (
        meta.session.query(traceability.MaterioVigilance)
            .filter(
                traceability.MaterioVigilance.material_id == material_id,
                traceability.MaterioVigilance.appointment_id == appointment_id)
            .one()
    )
    material_used.material.actual_quantity += material_used.quantity_used
    meta.session.delete(material_used)
    meta.session.commit()
    return redirect(url_for('view_material_used_in_appointment',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))

@app.route('/view/material_used_in_appointment?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
def view_material_used_in_appointment(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    
    materials_used_form = MaterioVigilanceUsedForm(request.form)

    materials_used = (
        meta.session.query(assets.Material)
            .filter(assets.Material.id.in_(
            meta.session.query(traceability.MaterioVigilance.material_id)
                .filter(
                traceability.MaterioVigilance.appointment_id == appointment_id)
                    )
                )
            .all()
    )

    other_materials = (
        meta.session.query(assets.Material)
            .filter(
                # Elimination of materials already listed as used in this 
                # appointment
                ~assets.Material.id.in_( [mat.id for mat in materials_used] ),
                # Elimination of materials with are :
                ~assets.Material.id.in_(
                    meta.session.query(assets.Material.id)
                        .filter(or_(
                            # either they are in stock, already not used
                            assets.Material.start_of_use.is_(None),
                            # either they already were used and thrown away
                            assets.Material.end_of_use.isnot(None),
                            assets.Material.end_use_reason !=\
                                        constants.END_USE_REASON_IN_USE_STOCK,
                            # they are not any left.
                            assets.Material.actual_quantity <= 0 )
                        )
                )
            )
            .all()
    )

    if request.method == 'POST' and materials_used_form.validate():
        for entry in materials_used_form.materials_used.entries:
#            materio_vigilance_form = MaterioVigilanceForm(request.form)
            if Decimal(entry.old_quantity_used.data) ==\
                                                entry.new_quantity_used.data:
                continue
            material = ( 
                meta.session.query(assets.Material)
                    .filter(assets.Material.id == int(entry.material_id.data))
                    .one()
            )
            materio_vigilance = (
                meta.session.query(traceability.MaterioVigilance)
                    .filter(
                        traceability.MaterioVigilance.appointment_id == 
                                                                appointment_id,
                        traceability.MaterioVigilance.material_id == 
                                                                material.id)
                    .one()
            )

            delta_quantity = Decimal(entry.old_quantity_used.data) -\
                                                entry.new_quantity_used.data
            materio_vigilance.quantity_used -= delta_quantity
            material.actual_quantity += delta_quantity
            # Case the material was marked as terminated, but finally there is
            # some left :
            if ( material.end_of_use == appointment.agenda.endtime.date()
                    and material.end_use_reason == 
                                        constants.END_USE_REASON_NATURAL_END
                    and material.actual_quantity > 0 ):
                material.end_of_use = None
                material.end_use_reason = constants.END_USE_REASON_IN_USE_STOCK
                meta.session.commit()

            # Case se material terminate :
            if material.actual_quantity == 0:
                material.end_of_use = appointment.agenda.endtime.date()
                material.end_use_reason = constants.END_USE_REASON_NATURAL_END
                meta.session.commit()

        return redirect(url_for('view_material_used_in_appointment', 
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))

    for material in materials_used:
        materio_vigilance = ( 
            meta.session.query(traceability.MaterioVigilance)
            .filter(traceability.MaterioVigilance.material_id == material.id,
                traceability.MaterioVigilance.appointment_id == appointment_id)
            .one()
        )
        materio_vigilance_form =\
                                MaterioVigilanceForm(request.form, material.id)
        materio_vigilance_form.material_id = material.id
        materio_vigilance_form.old_quantity_used =\
                                                materio_vigilance.quantity_used
        materio_vigilance_form.new_quantity_used =\
                                                materio_vigilance.quantity_used
        pdb.set_trace()
        materio_vigilance_form.material_data = (
            str(material.id) + " " + material.asset_category.brand + " " +
            material.asset_category.commercial_name + " " +
            material.asset_category.description + " " +
            str(material.actual_quantity) + " " + 
            constants.UNITIES[material.asset_category.unity][1] )
        materials_used_form.materials_used.append_entry(materio_vigilance_form)

    return render_template('view_material_used_in_appointment.html',
                            patient=patient, appointment=appointment,
                            constants=constants,
#                            materials_used=materials_used,
                            materials_used_form=materials_used_form,
                            other_materials=other_materials)
