# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

import pdb
from flask import ( session, render_template, request, redirect, url_for, 
                    jsonify, abort )
import sqlalchemy
from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import ( meta, act, schedule, administration, traceability,
                            assets, teeth, compta)
from odontux.views import cotation as views_cotation
from odontux.views import cost

from odontux.views.log import index
#from odontux.views.patient import list_acts

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, IntegerField, validators,
                     FieldList, FormField, SubmitField)
from odontux.views.forms import ColorField
from decimal import Decimal
import datetime

class SpecialtyForm(Form):
    name = TextField('name', [validators.Required(), 
                     validators.Length(min=1, max=20, 
                     message=_("Must be less than 20 characters"))])
    color = ColorField('color')

class ClinicGestureForm(Form):
    name = TextField(_('Name'), [validators.Required()])
    description = TextAreaField(_('Description'))
    duration = IntegerField(_('Duration in minutes'),
                                                [validators.Optional()],
                                                render_kw={'size': 8})
    before_first_patient = BooleanField(_('Before first patient of the day'))
    after_last_patient = BooleanField(_('After last patient of the day'))
    before_each_appointment = BooleanField(_('Before each appointment'))
    after_each_appointment = BooleanField(_('After each appointment'))
    specialty_id = SelectField(_('Specialty'), coerce=int)
    submit = SubmitField(_('Update'))

class MaterialCategoryClinicGestureForm(Form):
    mean_quantity = DecimalField(_('Quantity used'), [validators.Required()],
                                                render_kw={'size': '8'})
    enter_in_various_gestures = DecimalField(_('Various gestures'), 
                                                    render_kw={'size':'4'})
    submit = SubmitField('Update')

class ClinicGestureCotationReferenceForm(Form):
    appointment_number = IntegerField(_('Appointment_number'))
    appointment_sequence = IntegerField(_('Appointment_sequence'))
    official_cotation = BooleanField(_('official'))
    appears_on_clinic_report = BooleanField(_('Clinic Report'))
    submit = SubmitField(_('Update'))

class GestureForm(Form):
    specialty_id = SelectField('specialty', coerce=int)
    code = TextField('code')
    alias = TextField('alias')
    name = TextField('name')
    color = ColorField('color')

class AppointmentCotationReferenceForm(Form):
    anatomic_location = IntegerField(_('Teeth / Anatomic location'), 
                                            [validators.Optional()] )
    healthcare_plan_id = SelectField(_('Healthcare plan'), coerce=int,
                                    description='UpdateGesture()')
    gesture_id = SelectField(_('Choose gesture in list'), coerce=int,
                                        description='UpdateCodePrice()')
    code = TextField(_('Code'), validators=[validators.Optional(),
                validators.AnyOf( 
                [ gesture.code for gesture in 
                    meta.session.query(act.Gesture).all() ] 
                )
                ]
    )
    price = DecimalField(_('Price'), [validators.Optional()])
    majoration = SelectField(_('Majoration'), coerce=int)

class PriceForm(Form):
    gesture_id = HiddenField(_('gesture_id'))
    healthcare_plan_id = HiddenField(_('healthcare_plan_id'))
    price = DecimalField(_('Price'), [validators.Optional()],
                        render_kw={'size':'6px'})

class CloneCotationForm(Form):
    id = HiddenField(_('id'))
    cotation_id = SelectField(_('Cotation model'), coerce=int)
    submit = SubmitField(_('Clone'))

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

#@app.route('/get/clinic_gestures_in_cotation?cid=<int:cotation_id>')
#def clinic_gestures_in_cotation(cotation_id):
#    
#    cotation = ( meta.session.query(act.Cotation)
#                    .filter(act.Cotation.id == cotation_id)
#                    .one()
#    )
#    clinic_gestures = [ 
#        ( cgref.id, cgref.gesture.name ) for cgref in 
#            sorted(cotation.clinic_gestures,
#                                    key=lambda (cgref.appointment_number,
#                                                cgref.appointment_sequence,
#                                               cgref.gesture.name) 
#            )
#    ]
#    return jsonify(success=True, clinic_gestures)
#
def get_specialty_field_list():
    return [ "name", "color" ]

def get_gesture_field_list():
    return [ "specialty_id", "code", "alias", 
             "name", "color" ]
def get_appointmentcotationreference_field_list():
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
        for cotation in sorted(healthcare_plan.cotations, 
                                        key=lambda cotation: ( 
                                            cotation.gesture.specialty.name,
                                            cotation.gesture.name ) ):
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
    specialty = ( meta.session.query(act.Specialty)
                    .filter(act.Specialty.id == specialty_id)
                    .one_or_none()
    )
    if not specialty:
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

@app.route('/clone/material_category_gesture?gid=<int:gesture_id>'
            '&gcid=<int:gesture_to_clone_id>')
def clone_material_category_gesture(gesture_id, gesture_to_clone_id):
    gesture = ( meta.session.query(act.Gesture)
                    .filter(act.Gesture.id == gesture_id)
                    .one()
    )
    gesture_to_clone = ( meta.session.query(act.Gesture)
                            .filter(act.Gesture.id == gesture_to_clone_id)
                            .one()
    )
    for material_category in gesture_to_clone.materials:
        if material_category not in gesture.materials:
            gesture.materials.append(material_category)

    return redirect(url_for('update_gesture', gesture_id=gesture.id))

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
    
    other_gestures = ( meta.session.query(act.Gesture)
                        .filter(act.Gesture.id != gesture.id)
                        .join(act.Specialty)
                        .order_by(act.Specialty.name, act.Gesture.name)
                        .all()
    )
    other_materials = ( meta.session.query(assets.MaterialCategory)
                            .filter(~assets.MaterialCategory.id.in_(
                                [ mat.id for mat in gesture.materials ]
                                )
                            )
                            .all()
    )
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
                            gesture=gesture,
                            other_materials=other_materials,
                            other_gestures=other_gestures
                            )

@app.route('/add/clinic_gesture?crel=<int:cotation_id>', 
                                                    methods=['GET', 'POST'])
def add_clinic_gesture(cotation_id):
    form = ClinicGestureForm(request.form)
    form.specialty_id.choices = [ (spe.id, spe.name) for spe in
                                    meta.session.query(act.Specialty).all() ]
    if request.method == 'POST' and form.validate():
        new_clinic_gesture = ( meta.session.query(act.ClinicGesture)
                            .filter(act.ClinicGesture.name == form.name.data)
                            .one_or_none()
        )
        if not new_clinic_gesture:
            args = {
                'name': form.name.data,
                'description': form.description.data,
                'duration': datetime.timedelta(seconds=form.duration.data*60),
                'before_first_patient': False,
                'after_last_patient': False,
                'before_each_appointment': False,
                'after_each_appointment': False,
                'specialty_id': form.specialty_id.data,
            }
            new_clinic_gesture = act.ClinicGesture(**args)
            meta.session.add(new_clinic_gesture)
            meta.session.commit()
        return redirect(url_for('update_clinic_gesture', 
                                    clinic_gesture_id=new_clinic_gesture.id,
                                    cotation_id=cotation_id,
                                    form=form))
    return render_template('add_clinic_gesture.html', cotation_id=cotation_id, 
                                                        form=form)

@app.route('/clone/clinic_gesture?mcgid=<int:model_cg_id>'
            '&cg_upd_id=<int:cg_to_update_id>&cid=<int:cotation_id>')
def clone_clinic_gesture(model_cg_id, cg_to_update_id, cotation_id):
    model_cg = ( meta.session.query(act.ClinicGesture)
                .filter(act.ClinicGesture.id == model_cg_id)
                .one()
    )
    model_cg_mat_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(
            assets.MaterialCategoryClinicGestureReference.clinic_gesture_id ==
                                                                model_cg_id
            )
            .all()
    )
    cg_to_update = ( meta.session.query(act.ClinicGesture)
                        .filter(act.ClinicGesture.id == cg_to_update_id)
                        .one()
    )
    cg_to_update_mat_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(
            assets.MaterialCategoryClinicGestureReference.clinic_gesture_id == 
                                                            cg_to_update_id)
            .all()
    )
    cg_to_update.specialty_id = model_cg.specialty_id
    cg_to_update.duration = model_cg.duration
    cg_to_update.before_first_patient = model_cg.before_first_patient
    cg_to_update.after_last_patient = model_cg.after_last_patient
    cg_to_update.before_each_appointment = model_cg.before_each_appointment
    cg_to_update.after_each_appointment = model_cg.after_each_appointment
    
    for old_material in cg_to_update_mat_ref:
        meta.session.delete(old_material)
        meta.session.commit()

    for new_material in model_cg_mat_ref:
        values = {
            'material_category_id': new_material.material_category_id,
            'clinic_gesture_id': cg_to_update_id,
            'mean_quantity': new_material.mean_quantity,
            'enter_in_various_gestures': new_material.enter_in_various_gestures
        }
        new_mat_cg_ref = assets.MaterialCategoryClinicGestureReference(**values)
        meta.session.add(new_mat_cg_ref)
    
    meta.session.commit()

    return redirect(url_for('update_clinic_gesture', 
                                        clinic_gesture_id=cg_to_update_id,
                                        cotation_id=cotation_id))


@app.route('/update/clinic_gesture?cgid=<int:clinic_gesture_id>'
            '?crel=<int:cotation_id>', methods=['GET', 'POST' ])
def update_clinic_gesture(clinic_gesture_id, cotation_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)

    all_clinic_gestures = ( meta.session.query(act.ClinicGesture)
                            .join(act.Specialty)
                            .order_by(act.Specialty.name,
                                        act.ClinicGesture.name)
                            .all()
    )

    clinic_gesture = ( meta.session.query(act.ClinicGesture)
                        .filter(act.ClinicGesture.id == clinic_gesture_id)
                        .one()
    )
    cotation = ( meta.session.query(act.Cotation)
                        .filter(act.Cotation.id == cotation_id)
                        .one()
    )

    cg_form = ClinicGestureForm(request.form)
    cg_form.specialty_id.choices = [ (spe.id, spe.name) for spe in
                                    meta.session.query(act.Specialty).all() ]
    other_materials = ( meta.session.query(assets.MaterialCategory)
        .filter(
                ~assets.MaterialCategory.id.in_(
            [ mat.material_category.id for mat in clinic_gesture.materials ]
                ),
                assets.MaterialCategory.id.in_(
                [ mat.id for mat in cotation.gesture.materials ]
                )
        )
        .join(act.Specialty)
        .order_by(act.Specialty.name, assets.MaterialCategory.commercial_name,
                    assets.MaterialCategory.brand )
        .all()
    )

    if request.method == 'POST' and cg_form.validate():
        # Verify if name update won't create IntegrityError (constraint unique)
        other_cg_same_new_name = ( meta.session.query(act.ClinicGesture)
                    .filter(act.ClinicGesture.id != clinic_gesture_id,
                            act.ClinicGesture.name == cg_form.name.data
                    )
                    .one_or_none()
        )
        # won't try to update with name already in db to avoid IntegrityError
        if not other_cg_same_new_name:
            for f in ( 'name', 'description', 'duration', 'specialty_id',
                    'before_first_patient', 'after_last_patient', 
                    'before_each_appointment', 'after_each_appointment' ):
                if f == 'duration':
                    setattr(clinic_gesture, f, 
                        datetime.timedelta(seconds=getattr(cg_form, f).data * 60))
                    
                else:
                    setattr(clinic_gesture, f, getattr(cg_form, f).data)
            meta.session.commit()
        return redirect(url_for('update_clinic_gesture', 
                                    clinic_gesture_id=clinic_gesture.id,
                                    cotation_id=cotation.id))

    # create update_form for each quantity
    quantity_forms = {}
    for cg_mat_ref in clinic_gesture.materials:
        material_cost = cost.get_material_cost(cg_mat_ref.id)
        mat_form = MaterialCategoryClinicGestureForm(request.form)
        mat_form.mean_quantity.data = cg_mat_ref.mean_quantity
        mat_form.enter_in_various_gestures.data =\
                                        cg_mat_ref.enter_in_various_gestures
        quantity_forms[cg_mat_ref.material_category_id] = ( 
                                    mat_form, "{0:.2f}".format(material_cost)
        )

    for f in ('name', 'description', 'duration', 'specialty_id',
                'before_first_patient', 'after_last_patient',
                'before_each_appointment', 'after_each_appointment' ):
        if f == 'duration':
            getattr(cg_form, f).data =\
                                getattr(clinic_gesture, f).seconds % 3600 / 60
        else:
            getattr(cg_form, f).data = getattr(clinic_gesture, f)

    return render_template('update_clinic_gesture.html', 
                                    clinic_gesture=clinic_gesture,
                                    cotation=cotation,
                                    other_materials=other_materials,
                                    all_clinic_gestures=all_clinic_gestures,
                                    quantity_forms=quantity_forms,
                                    cg_form=cg_form,
                                    constants=constants)

@app.route('/update/mean_quantity_mat_in_gest'
            '?mgid=<int:mat_gest_id>&cid=<int:cotation_id>', methods=['POST'])
def update_mean_quantity_mat_in_gest(mat_gest_id, cotation_id):
    mat_gest_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(assets.MaterialCategoryClinicGestureReference.id == 
                                                                mat_gest_id)
            .one()
    )
    
    form = MaterialCategoryClinicGestureForm(request.form)
    if form.validate():
        mat_gest_ref.mean_quantity = form.mean_quantity.data
        mat_gest_ref.enter_in_various_gestures =\
                                form.enter_in_various_gestures.data
        meta.session.commit()
    return redirect(url_for('update_clinic_gesture', 
                            clinic_gesture_id=mat_gest_ref.clinic_gesture_id,
                                                    cotation_id=cotation_id))

@app.route('/add/material_category_to_clinic_gesture'
            '?cgid=<int:clinic_gesture_id>&mcid=<int:material_category_id>'
            '&cotid=<int:cotation_id>')
def add_material_category_to_clinic_gesture(clinic_gesture_id, 
                                            material_category_id, cotation_id):
    clinic_gesture = ( meta.session.query(act.ClinicGesture)
                        .filter(act.ClinicGesture.id == clinic_gesture_id)
                        .one()
    )
    material_category = ( meta.session.query(assets.MaterialCategory)
                    .filter(assets.MaterialCategory.id == material_category_id)
                    .one()
    )
    mat_cg_reference = assets.MaterialCategoryClinicGestureReference(
                        mean_quantity=material_category.automatic_decrease)
    mat_cg_reference.material_category = material_category
    clinic_gesture.materials.append(mat_cg_reference)
    meta.session.commit()

    return redirect(url_for('update_clinic_gesture', 
                                clinic_gesture_id=clinic_gesture.id,
                                cotation_id=cotation_id))

@app.route('/remove/material_category_from_clinic_gesture'
            '?mccgid=<int:material_category_clinic_gesture_ref_id>'
            '&cotid=<int:cotation_id>')
def remove_material_category_from_clinic_gesture(
                                    material_category_clinic_gesture_ref_id,
                                                                cotation_id):
    mc_cg_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
        .filter(
            assets.MaterialCategoryClinicGestureReference.id == 
                                        material_category_clinic_gesture_ref_id
        )
        .one()
    )
    clinic_gesture_id = mc_cg_ref.clinic_gesture_id
    meta.session.delete(mc_cg_ref)
    meta.session.commit()

    return redirect(url_for('update_clinic_gesture', 
                                clinic_gesture_id=clinic_gesture_id,
                                cotation_id=cotation_id))


@app.route('/remove/material_category_from_gesture&gid=<int:gesture_id>'
            '&mcid=<int:material_category_id>')
def remove_material_category_from_gesture(gesture_id, material_category_id):
    gesture = ( meta.session.query(act.Gesture)
                    .filter(act.Gesture.id == gesture_id)
                    .one()
    )
    material_category = ( meta.session.query(assets.MaterialCategory)
                    .filter(assets.MaterialCategory.id == material_category_id)
                    .one()
    )
    gesture.materials.remove(material_category)
    meta.session.commit()
    return redirect(url_for('update_gesture', gesture_id=gesture.id))


@app.route('/add/material_category_to_gesture&gid=<int:gesture_id>'
            '&mcid=<int:material_category_id>')
def add_material_category_to_gesture(gesture_id, material_category_id):
    gesture = ( meta.session.query(act.Gesture)
                    .filter(act.Gesture.id == gesture_id)
                    .one()
    )
    material_category = ( meta.session.query(assets.MaterialCategory)
                    .filter(assets.MaterialCategory.id == material_category_id)
                    .one()
    )
    gesture.materials.append(material_category)
    meta.session.commit()
    return redirect(url_for('update_gesture', gesture_id=gesture.id))

@app.route('/view/gesture?id=<int:gesture_id>')
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
            constants=constants,
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

@app.route('/clone/gestures_in_cotation?cid=<int:cotation_id>', 
                                                            methods=['POST'])
def clone_gestures_in_cotation(cotation_id):
    cotation = ( meta.session.query(act.Cotation)
                    .filter(act.Cotation.id == cotation_id)
                    .one()
    )
    form = CloneCotationForm(request.form)
    form.cotation_id.choices = [ 
        ( cot.id, cot.healthcare_plan.name + " " + str(cot.price) + 
                                        constants.CURRENCY_SYMBOL ) for cot in
            meta.session.query(act.Cotation)
                .filter(act.Cotation.gesture_id == cotation.gesture_id)
                .order_by(act.Cotation.price)
                .all()
    ]

    if form.validate():
        model_cotation = ( meta.session.query(act.Cotation)
                            .filter(act.Cotation.id == form.cotation_id.data)
                            .one()
        )
        cg_in_model_cotation_ref = (
            meta.session.query(act.ClinicGestureCotationReference)
                .filter(act.ClinicGestureCotationReference.cotation_id == 
                                                            model_cotation.id)
                .all()
        )
        for cg in cotation.clinic_gestures:
            meta.session.delete(cg)
            meta.session.commit()

        for model_cg in cg_in_model_cotation_ref:
            values = {
                'clinic_gesture_id': model_cg.clinic_gesture_id,
                'cotation_id': cotation_id,
                'official_cotation': model_cg.official_cotation,
                'appears_on_clinic_report':
                                    model_cg.appears_on_clinic_report,
                'appointment_number': model_cg.appointment_number,
                'appointment_sequence': model_cg.appointment_sequence,
            }
            clone_cotation = act.ClinicGestureCotationReference(**values)
            meta.session.add(clone_cotation)
            meta.session.commit()

    return redirect(url_for('update_cotation', cotation_id=cotation_id))

@app.route('/update/cotation?cid=<int:cotation_id>', methods=['GET', 'POST'])
def update_cotation(cotation_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)

    cotation = ( meta.session.query(act.Cotation)
                    .filter(act.Cotation.id == cotation_id)
                    .one()
    )
    clone_cotation_form = CloneCotationForm(request.form)
    clone_cotation_form.cotation_id.choices = [ 
        ( cot.id, cot.healthcare_plan.name + " " + str(cot.price) + 
                                        constants.CURRENCY_SYMBOL ) for cot in
            meta.session.query(act.Cotation)
                .filter(act.Cotation.gesture_id == cotation.gesture_id)
                .order_by(act.Cotation.price)
                .all()
    ]

    price_form = PriceForm(request.form)

    if request.method == 'POST' and price_form.validate():
        cotation.price = price_form.price.data
        meta.session.commit()
    else:
        price_form.price.data = cotation.price

    clinic_gestures_available = ( meta.session.query(act.ClinicGesture)
                                    .join(act.Specialty)
                                    .order_by(
                                        act.Specialty.name,
                                        act.ClinicGesture.name)
                                    .all()
    )
    
    # cg_cot_dics = { appointment_number: [ [ (cg_cot_ref, form) ], duration,
    #                                       [ cg_mat_ref ], material_cost ],
    #               }
    cg_cot_dict = cost.get_cotation_dictionary(cotation_id)
    cost_informations = cost.get_cost_informations(cg_cot_dict, cotation_id)
   
    return render_template('update_cotation.html', cotation=cotation,
                            price_form=price_form,
                            clinic_gestures=clinic_gestures_available,
                            cg_cot_dict=cg_cot_dict,
                            cost_informations=cost_informations,
                            clone_cotation_form=clone_cotation_form)

@app.route('/add/clinic_gesture_to_cotation?cid=<int:clinic_gesture_id>'
            '&cid=<int:cotation_id>')
def add_clinic_gesture_to_cotation(clinic_gesture_id, cotation_id):
    others = ( meta.session.query(act.ClinicGestureCotationReference)
        .filter(
        act.ClinicGestureCotationReference.clinic_gesture_id ==
                                                        clinic_gesture_id,
        act.ClinicGestureCotationReference.cotation_id == cotation_id
        )
    )
    
    values = {
        'clinic_gesture_id': clinic_gesture_id,
        'cotation_id': cotation_id,
        'appointment_number': 1,
        'appointment_sequence': 1,
    }
    new_cg_in_cot = act.ClinicGestureCotationReference(**values)
    meta.session.add(new_cg_in_cot)
    meta.session.commit()
    return redirect(url_for('update_cotation', cotation_id=cotation_id))

@app.route('/remove/clinic_gesture_from_cotation?cid=<int:cg_cot_ref_id>')
def remove_clinic_gesture_from_cotation(cg_cot_ref_id):
    query = meta.session.query(act.ClinicGestureCotationReference)
    cg_cot_ref = ( 
        query.filter(act.ClinicGestureCotationReference.id == cg_cot_ref_id )
        .one()
    )
    cotation_id = cg_cot_ref.cotation_id
    meta.session.delete(cg_cot_ref)
    meta.session.commit()
    return redirect(url_for('update_cotation', cotation_id=cotation_id))

@app.route('/update/clinic_gesture_cotation_reference?rid=<int:cg_cot_ref_id>',
                                                            methods=['POST'])
            
def update_clinic_gesture_cotation_reference(cg_cot_ref_id):
    ref = ( meta.session.query(act.ClinicGestureCotationReference)
            .filter(act.ClinicGestureCotationReference.id == cg_cot_ref_id)
            .order_by(
                act.ClinicGestureCotationReference.appointment_number,
                act.ClinicGestureCotationReference.appointment_sequence )
            .one()
    )
    ref_form = ClinicGestureCotationReferenceForm(request.form)
    if ref_form.validate():
        # only one clinic gesture of cotation bears the official global gesture
        if ref_form.official_cotation.data:
            other_cg = ( meta.session.query(act.ClinicGestureCotationReference)
                .filter(act.ClinicGestureCotationReference.cotation_id == 
                                                            ref.cotation_id)
                .all()
            )
            for cg in other_cg:
                cg.official_cotation = False
        ref.appears_on_clinic_report =\
                                    ref_form.appears_on_clinic_report.data
        ref.official_cotation = ref_form.official_cotation.data
        ref.appointment_number = ref_form.appointment_number.data
        ref.appointment_sequence = ref_form.appointment_sequence.data
        meta.session.commit()
    return redirect(url_for('update_cotation', cotation_id=ref.cotation_id))
        

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
    appointment_cotation_form = AppointmentCotationReferenceForm(request.form)

    # Patient is linked to some healthcare plans. Won't be included other plans
    appointment_cotation_form.healthcare_plan_id.choices = [
                    (hcs.id, hcs.name) for hcs in sorted(patient.hcs,
                                            key=lambda hcs: hcs.name) ]
    # Create a list of all existing gestures.
    appointment_cotation_form.gesture_id.choices = [
        (gesture.id, gesture.name) for gesture in 
                                    meta.session.query(act.Gesture)
                                        .join(act.Specialty)
                                        .order_by(act.Specialty.name,
                                                    act.Gesture.name)
                                        .all() ]
    appointment_cotation_form.gesture_id.choices.insert( 0, (0, ""))
    appointment_cotation_form.majoration.choices =\
                                            get_majoration_choices()

    if request.method == 'POST' and appointment_cotation_form.validate():
        # if gesture_form comes with a code, upade form.gesture_id with the 
        # code provided by user. 
        if appointment_cotation_form.code.data:
            gesture = (
                meta.session.query(act.Gesture)
                    .filter(or_(
                    act.Gesture.code == appointment_cotation_form.code.data,
                    act.Gesture.id == appointment_cotation_form.gesture_id.data)
                    ).one_or_none()
            )
        if not gesture:
            # TODO : redirect error + message
            return redirect(url_for('index'))
        cotation = ( meta.session.query(act.Cotation)
            .filter(act.Cotation.gesture_id == gesture.id,
                    act.Cotation.healthcare_plan_id ==
                            appointment_cotation_form.healthcare_plan_id.data
            )
            .one()
        )
        values = {}
        # In the appointment_gesture_reference table, we'll store
        # appointment, act, and anatomic_location
        values['appointment_id'] = appointment.id
        values['cotation_id'] = cotation.id

        if ( 
            appointment_cotation_form.anatomic_location.data not in 
                                constants.ANATOMIC_LOCATION_SOFT_TISSUES.keys()
            and appointment_cotation_form.anatomic_location.data not in 
                                constants.ANATOMIC_LOCATION_TEETH_SET.keys()
            and appointment_cotation_form.anatomic_location.data not in
                                constants.ANATOMIC_LOCATION_TEETH.keys() ):
            # TODO redirect error + message
            return redirect(url_for('index'))
        if appointment_cotation_form.anatomic_location.data is None:
            appointment_cotation_form.anatomic_location.data = 0
        values['anatomic_location'] =\
                            appointment_cotation_form.anatomic_location.data

        values['price'] = appointment_cotation_form.price.data
        if not appointment_cotation_form.price.data:
            values['is_paid'] = True

        new_technical_gesture = act.AppointmentCotationReference(**values)
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
                            admin_cotation_form=appointment_cotation_form)

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
    gesture = meta.session.query(act.AppointmentCotationReference).filter(
            act.AppointmentCotationReference.id == gesture_id).one()

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


