# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import meta, act, cotation, schedule, administration
from odontux.views import cotation as views_cotation
from odontux.views import teeth
from odontux.views.log import index
from odontux.views.patient import list_acts

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, validators)
from odontux.views.forms import ColorField

class SpecialtyForm(Form):
    name = TextField('name', [validators.Required(), 
                     validators.Length(min=1, max=20, 
                     message=_("Must be less than 20 characters"))])
    color = ColorField('color')

class ActTypeForm(Form):
    specialty_id = SelectField('specialty', coerce=int)
    code = TextField('code')
    alias = TextField('alias')
    name = TextField('name')
    color = ColorField('color')

class AppointmentActReferenceForm(Form):
    appointment_id = SelectField(_('appointment'), coerce=int)
    act_code = TextField(_('act_code'))
    act_id = SelectField(_('Choose act in list'), coerce=int)
    tooth_id = SelectField(_('Choose tooth  in list'), coerce=int)
    majoration = SelectField(_('Majoration'), coerce=int)

class PriceForm(Form):
    acttype_id = HiddenField(_('acttype_id'))
    healthcare_plan_id = HiddenField(_('healthcare_plan_id'))
    price = DecimalField(_('Price'), [validators.Optional()])

def get_specialty_field_list():
    return [ "name", "color" ]

def get_acttype_field_list():
    return [ "specialty_id", "code", "alias", 
             "name", "color" ]
def get_appointmentactreference_field_list():
    return [ "appointment_id", "act_code", "act_id", "tooth_id", "majoration" ]

def get_specialty_choice_list():
    return [ (choice.id, choice.name) for choice in 
                                    meta.session.query(act.Specialty).all() ]

def get_appointment_choice_list(patient_id):
    appointment_list = []
    appointments = meta.session.query(schedule.Appointment).filter(
                   schedule.Appointment.patient_id == patient_id).all()
#    appointments = meta.session.query(schedule.Appointment).filter(
#                   schedule.Appointment.patient_id == patient_id).order_by(
#                   desc(schedule.Agenda.starttime)).all()
    for appointment in appointments : 
        appointment_list.append( (appointment.id, 
                                  appointment.agenda.starttime )
                               )
    return appointment_list

def get_act_choice_list():
    acts_list = []
    acts = meta.session.query(act.ActType).order_by(
           act.ActType.specialty_id).order_by(
           act.ActType.alias).all()
    for gesture in acts:
        acts_list.append((gesture.id, gesture.alias))
    return acts_list

def get_appointment_act_reference_choice_lists(patient_id):
    """ """
    return (get_appointment_choice_list(patient_id), 
            get_act_choice_list(),
            teeth.get_tooth_id_choice_list(patient_id), 
            get_majoration_choice_list() )


####
# Specialties
####

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
# Acts
#####

@app.route('/list/acttype?keywords=<keywords>&ordering=<ordering>')
def list_acttype(keywords="", ordering=""):
    """ The target is to display dentist's gesture, describing it, its values.
    Looking in ActType table, we may decide to print only 
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
    query = meta.session.query(act.ActType)
    # If we only need ones of a specialty : 
    if request.form and request.form['specialty']:
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == request.form['specialty'].one())
            query = query.filter(act.ActType.specialty_id == specialty.id)
        except sqlalchemy.orm.exc.NoResultFound:
            pass
    # Filter by keywords
    if keywords:
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                act.ActType.alias.ilike(keyword),
                act.ActType.name.ilike(keyword),
                act.ActType.code.ilike(keyword),
                (and_(
                    act.ActType.specialty_id == act.Specialty.id,
                    act.Specialty.name.ilike(keyword)
                    )
                )
            ))
    # We want to order the result to find what we are looking for more easily
    if not ordering:
        ordering = [ act.ActType.specialty_id, act.ActType.alias ]
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
    return render_template('list_act.html', 
                            gestures_list=gestures_list)

@app.route('/act/add/', methods=['GET', 'POST'])
@app.route('/add/act/', methods=['GET', 'POST'])
def add_acttype():
    """ """
    # TODO  BECAUSE DIFFICULT TO MAKE IT "PERFECT"
    form = ActTypeForm(request.form)
    form.specialty_id.choices = get_specialty_choice_list()
    if request.method == 'POST' and form.validate():
        values = {}
        values['specialty_id'] = form.specialty_id.data
        values['code'] = form.code.data
        values['alias'] = form.alias.data
        values['name'] = form.name.data
        values['color'] = form.color.data
        new_acttype = act.ActType(**values)
        meta.session.add(new_acttype)
        meta.session.commit()
        return redirect(url_for('list_acttype', keywords="", 
                                                ordering=""))
    return render_template('/add_act.html', form=form)

@app.route('/act/update_acttype=<int:acttype_id>/', methods=['GET', 'POST'])
def update_acttype(acttype_id):
    acttype = meta.session.query(act.ActType).filter\
              (act.ActType.id == acttype_id).one()
    if not acttype:
        return redirect(url_for('list_acttype'))
    try:
        specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == acttype.specialty_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        specialty=""

    acttype_form = ActTypeForm(request.form)
    acttype_form.specialty_id.choices = get_specialty_choice_list()
    
    #TODO (130202 : je me demande ce que je voulais faire à ce todo qui date 
    # d'on ne sait quand...
    # (update 160504 : toujours pas d'idée)
    
    if request.method == 'POST' and acttype_form.validate():
        for f in get_acttype_field_list():
            setattr(acttype, f, getattr(acttype_form, f).data)
        meta.session.commit()
        return redirect(url_for('view_acttype', 
                                    acttype_id=acttype_id))

    # For the GET method
    for f in get_acttype_field_list():
        getattr(acttype_form, f).data = getattr(acttype, f)

    specialty_form = SpecialtyForm(request.form)
    return render_template('/update_act.html', 
                            acttype_form=acttype_form, 
                            specialty_form=specialty_form,
                            acttype=acttype
                            )

@app.route('/view/acttype?id=<int:acttype_id>')
def view_acttype(acttype_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    acttype = ( meta.session.query(act.ActType)
                    .filter(act.ActType.id == acttype_id)
                    .one() )

    price_forms = []
    for cotation in acttype.cotations:
        form = PriceForm(request.form)
        form.acttype_id.data = acttype.id
        form.healthcare_plan_id.data = cotation.healthcare_plan_id
        
        if cotation.price:
            form.price.data = cotation.price
        else:
            form.price.data = 0
        price_forms.append((cotation, form))
    healthcare_plans_not_in_acttype = (
        meta.session.query(act.HealthCarePlan)
            .filter(~act.HealthCarePlan.cotations.any(
                act.ActType.id == acttype.id
                )
            ).all()
        )
    
    return render_template('view_acttype.html', acttype=acttype,
            price_forms=price_forms,
            healthcare_plans_not_in_acttype=healthcare_plans_not_in_acttype)

@app.route('/add/healthcare_plan_to_acttype?AT=<int:acttype_id>&HP=<int:healthcare_plan_id>')
def add_healthcare_plan_to_acttype(acttype_id, healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    values = {
        'acttype_id': acttype_id,
        'healthcare_plan_id': healthcare_plan_id
    }
    
    new_cotation = act.Cotation(**values)
    meta.session.add(new_cotation)
    meta.session.commit()
    return redirect(url_for('view_acttype', acttype_id=acttype_id))

@app.route('/remove/healthcare_plan_to_acttype?AT=<int:acttype_id>&HP=<int:healthcare_plan_id>')
def remove_healthcare_plan_to_acttype(acttype_id, healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    cotation = ( 
        meta.session.query(act.Cotation)
            .filter(act.Cotation.acttype_id == acttype_id,
                    act.Cotation.healthcare_plan_id == healthcare_plan_id
                )
            .one()
        )
    meta.session.delete(cotation)
    meta.session.commit()
    return redirect(url_for('view_acttype',acttype_id=acttype_id))

@app.route('/update/cotation', methods=['POST'])
def update_cotation():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    price_form = PriceForm(request.form)

    if price_form.validate():
        cotation = (
            meta.session.query(act.Cotation)
                .filter(act.Cotation.acttype_id== price_form.acttype_id.data,
                        act.Cotation.healthcare_plan_id ==
                                        price_form.healthcare_plan_id.data
                    )
                .one()
            )
        cotation.price = price_form.price.data
        meta.session.commit()
        
    return redirect(url_for('view_acttype', 
                            acttype_id=price_form.acttype_id.data))

def _add_administrativact(act_id, appointment_id, tooth_id=0, majoration_id=0):
    """ """
    values = {}
    majoration_price = 0
    if not act_id:
        raise Exception(_("Need the act_id"))
    if not appointment_id:
        raise Exception(_("Need the appointment_id"))

    # Get the majoration, if any...

    gesture = meta.session.query(act.ActType).filter(
              act.ActType.id == act_id).one()
    # Get data to evaluate the price for this act ; for this, we need to know
    # the age of the patient, and if it's the state that is going to pay (cmu).
    execution = meta.session.query(cotation.CotationFr).filter(
                cotation.CotationFr.id == gesture.cotationfr_id).one()
    patient = meta.session.query(administration.Patient).filter(
              administration.Patient.id == session['patient_id']).one()
#    if patient.age() < constants.KID_AGE:
#        multiplicator = execution.kid_multiplicator
#        exceeding = execution.exceeding_kid_normal
#    else:
#        multiplicator = execution.adult_multiplicator
#        exceeding = execution.exceeding_adult_normal
#
#    # For some acts, patient under state medical care (CMU) get special prices
#    # (paid directly by the state).
#    patient_right = meta.session.query(SocialSecurityLocale).filter(
#                    SocialSecurityLocale.id == patient.socialsecurity_id).one()
#    key = meta.session.query(cotation.NgapKeyFr).filter(
#          cotation.NgapKeyFr.id == execution.key_id).one()
#
    # In the appointment_act_reference table, we'll store
    # appointment, act, and if any, the tooth
    values['appointment_id'] = appointment_id
    values['act_id'] = act_id
    if tooth_id:
        values['tooth_id'] = tooth_id
    # the act code
    if patient_right.cmu:
        if execution.key_cmu_id:
            cmu_key = meta.session.query(cotation.CmuKeyFr)\
                        .filter(cotation.CmuKeyFr.id ==
                                execution.key_cmu_id).one().key
            values["code"] = cmu_key + str(execution.adult_cmu_num)
            exceeding = execution.exceeding_adult_cmu
            if patient.age() < constants.KID_AGE:
                exceeding = execution.exceeding_kid_cmu
        else:
            values["code"] = key.key + str(multiplicator)
    else:
        values["code"] = key.key + str(multiplicator)
    # the price to pay by the patient.
    values['price'] = execution.get_price(multiplicator, exceeding, 
                                          majoration_price)

    new_act = act.AppointmentActReference(**values)
    meta.session.add(new_act)
    meta.session.commit()

    if session['role'] == constants.ROLE_DENTIST:
        user_id = session['user_id']
    else:
        user_id = ""
    invoice = gnucash_handler.GnuCashInvoice(patient.id, appointment_id, 
                                             user_id)
    invoice_id = invoice.add_act(values['code'], values['price'], new_act.id)

    new_act.invoice_id = invoice_id
    meta.session.commit()
    return new_act.id

@app.route('/gesture/add?patient_id=<int:patient_id>'
           '&appointment_id=<int:appointment_id>', methods=['GET', 'POST'])
def add_administrativact(patient_id, appointment_id):
    if not patient_id or not appointment_id:
        raise Exception(_("Need a patient and an appointment to add an act"))

    if (session['role'] == constants.ROLE_ADMIN 
        or session['role'] == constants.ROLE_SECRETARY):
        return redirect(url_for('index'))

    # Prepare the formulary dealing with the act of adding an administrativ
    # act
    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()
    admin_act_form = AppointmentActReferenceForm(request.form)

    (admin_act_form.appointment_id.choices, 
        admin_act_form.act_id.choices, 
        admin_act_form.tooth_id.choices, 
        admin_act_form.majoration.choices
    ) = get_appointment_act_reference_choice_lists(patient_id)

    if request.method == 'POST' and admin_act_form.validate():
        new_act_id = _add_administrativact(admin_act_form.act_id.data,
                                            admin_act_form.appointment_id.data,
                                            admin_act_form.tooth_id.data,
                                            admin_act_form.majoration.data)
        if not new_act_id:
            return redirect(url_for("list_acts"))
        else:
            return redirect(url_for("list_acts"))

    # Case in GET method :
    admin_act_form.appointment_id.data = appointment_id

    return render_template("/add_administrativ_act.html",
                            patient=patient,
                            appointment=appointment,
                            admin_act_form = admin_act_form)

@app.route('/gesture/del?patient_id=<int:patient_id>'
           '&appointment_id=<int:appointment_id>&act_id=<int:act_id>'
           '&code=<code>')
def remove_administrativact(patient_id, appointment_id, act_id, code):
    """ """
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))
    patient = checks.get_patient(patient_id)
    gesture = meta.session.query(act.AppointmentActReference).filter(
            act.AppointmentActReference.id == act_id).one()

    if session['role'] == constants.ROLE_DENTIST:
        user_id = session['user_id']
    else:
        user_id = ""
    invoice = gnucash_handler.GnuCashInvoice(patient.id, appointment_id, 
                                             user_id)
    
    remove_from_gnucash = invoice.remove_act(code, act_id)
    if remove_from_gnucash:
        pass
        # was first made to be sure that all fit together with gnucash.
        # For the moment, we don't care.

    meta.session.delete(gesture)
    meta.session.commit()
    return redirect(url_for('list_acts'))
