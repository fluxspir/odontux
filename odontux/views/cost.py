# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/10/13
# 
# Licence BSD
#

import pdb
from flask import render_template, request, redirect, url_for, session, abort
from wtforms import ( Form, IntegerField, SubmitField, validators )
#from wtforms.fields.html5 import DateField
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date, Time
import datetime
#import calendar

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, users, act, assets
#from odontux.views.forms import TimeField
from odontux.views.log import index

class ClinicGestureCotationReferenceForm(Form):
    appointment_number = IntegerField(_('Appointment_number'), 
                                                    render_kw={'size':'4'})
    appointment_sequence = IntegerField(_('Appointment_sequence'),
                                                    render_kw={'size':'4'})
    submit = SubmitField(_('Update'))

def get_cotation_dictionary(cotation_id):
    cotation = ( meta.session.query(act.Cotation)
                    .filter(act.Cotation.id == cotation_id)
                    .one()
    )
    dictionnary = {}
    # create cg_in_cotation = list of clinics gestures in this cotation
    # create materials_used = list of materials that may be used
    for cg_cot_ref in sorted(cotation.clinic_gestures,
                        key=lambda cg_cot_ref: ( cg_cot_ref.appointment_number,
                                            cg_cot_ref.appointment_sequence)):
        if cg_cot_ref.appointment_number not in dictionnary:
            dictionnary[cg_cot_ref.appointment_number] = [ 
                                                [], # ( cg_cot_ref, ref_form )
                                                datetime.timedelta(seconds=0), #duration
                                                [], # cg_mat_ref list
                                                0, # material_cost
            ]

        ref_form = ClinicGestureCotationReferenceForm(request.form)
        ref_form.appointment_number.data = cg_cot_ref.appointment_number
        ref_form.appointment_sequence.data = cg_cot_ref.appointment_sequence

        dictionnary[cg_cot_ref.appointment_number][0].append( 
                                                    ( cg_cot_ref, ref_form ) )
        
        dictionnary[cg_cot_ref.appointment_number][1] =\
            dictionnary[cg_cot_ref.appointment_number][1] +\
                                            cg_cot_ref.clinic_gesture.duration

        for cg_mat_ref in cg_cot_ref.clinic_gesture.materials:
            material = ( meta.session.query(assets.Material)
                .filter(
                    assets.Material.asset_category_id == 
                                            cg_mat_ref.material_category_id,
                    assets.Material.end_of_use.is_(None),
                    assets.Material.end_use_reason == 0
                )
            )
            material_in_use = (
                material.filter(assets.Material.start_of_use.isnot(None))
                .first()
            )
            if material_in_use:
                material_used = material_in_use
            else:
                material_used = (
                    material.order_by(assets.Material.expiration_date)
                    .first()
                )

            if not cg_mat_ref.mean_quantity:
                cg_mat_ref.mean_quantity = material.automatic_decrease

            material_used_cost = ( cg_mat_ref.mean_quantity / 
                    material_used.asset_category.initial_quantity ) *\
                                                material_used.acquisition_price

            dictionnary[cg_cot_ref.appointment_number][2].append( cg_mat_ref )
            # cost of appointment in material
            dictionnary[cg_cot_ref.appointment_number][3] =\
                dictionnary[cg_cot_ref.appointment_number][3] +\
                                                            material_used_cost
                                        
def get_cost_informations(cg_cot_dict):

    total_material_cost = 0
    duration_gesture = datetime.timedelta(seconds=0)
    for appointment in cg_cot_dict:
        # cost of materials specific to gesture
        total_material_cost = total_material_cost + cg_cot_dict[appointment][3]
        # duration specific to gesture
        total_duration = total_duration + cg_cot_dict[appointment][1]

    # test session['user_id'] int ou str
    dentist_hour_fees = ( meta.session.query(act.HealthCarePlanUserReference)
        .filter(act.HealthCarePlanUserReference.user_id == session['user_id'],
                act.HealthCarePlanUserReference.healthcare_plan_id ==
                                                cotation.healthcare_plan_id)
        .one_or_none()
    )
    if dentist_hour_cost:
        dentist_hour_fees = dentist_hour_cost.hour_fees
    else:
        dentist_hour_fees = 0

    cost_informations = {
        'duration_gesture': duration_gesture,
        'gesture_material_cost': total_material_cost,
        'dentist_hour_fees': dentist_hour_fees,
        'appointments_material_cost': 0,
        'appointments_duration': 0,
    }
 
    return dictionnary, cost_informations

@app.route('/portal/operation_cost/')
def portal_operation_cost():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)

    return render_template('operation_cost.html')

