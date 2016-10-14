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
from odontux.models import meta, users, act, assets, cost
#from odontux.views.forms import TimeField
from odontux.views.log import index

class ClinicGestureCotationReferenceForm(Form):
    appointment_number = IntegerField(_('Appointment_number'), 
                                                    render_kw={'size':'4'})
    appointment_sequence = IntegerField(_('Appointment_sequence'),
                                                    render_kw={'size':'4'})
    submit = SubmitField(_('Update'))

def get_dental_unit_week_hours():
    dental_units = ( meta.session.query(users.DentalUnit).filter(
                                        users.DentalUnit.active == True)
                    .all()
    )
    dental_unit_open_time = datetime.timedelta(seconds=0)
    for du in dental_units:
        timesheet = ( meta.session.query(users.DentalUnitTimeSheet)
                    .filter(users.DentalUnitTimeSheet.dental_unit_id == du.id)
                    .all()
        )
        dummydate = datetime.date(2000, 1, 1)
        for period_open in timesheet:
            
            open_time =\
                datetime.datetime.combine(dummydate, period_open.end) -\
                datetime.datetime.combine(dummydate, period_open.begin)
            dental_unit_open_time = dental_unit_open_time + open_time

    return dental_unit_open_time

def get_dentist_hour_fees(healthcare_plan_id, user_id=0):
    if not user_id:
        user_id = session['user_id']
    dentist_hour_fees = ( meta.session.query(act.HealthCarePlanUserReference)
        .filter(act.HealthCarePlanUserReference.user_id == user_id,
                act.HealthCarePlanUserReference.healthcare_plan_id ==
                                                            healthcare_plan_id)
        .one_or_none()
    )
    if dentist_hour_fees:
        return dentist_hour_fees.hour_fees
    else:
        return 0

def get_material_cost(clinic_gesture):
    cg_mat_ref_list = []
    for cg_mat_ref in clinic_gesture.materials:
        cg_mat_ref_list.append(cg_mat_ref)
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

    return cg_mat_ref_list, material_used_cost

def get_daily_data():
    daily = (
        meta.session.query(act.ClinicGesture)
            .filter(act.ClinicGesture.is_daily == True)
            .all()
    )
    material_cost = 0
    duration = datetime.timedelta(seconds=0)
    for clinic_gesture in daily:
        duration = duration + clinic_gesture.duration
        material_cost = material_cost + get_material_cost(clinic_gesture)[1]

    return duration, material_cost

def get_appointmently_data():
    appointmently = ( 
        meta.session.query(act.ClinicGesture)
            .filter(act.ClinicGesture.is_appointmently == True)
            .all()
    )
    total_material_cost = 0
    total_duration_time = datetime.timedelta(seconds=0)
    for clinic_gesture in appointmently:
        total_duration_time = total_duration_time + clinic_gesture.duration
        
        cg_mat_ref_list, material_used_cost = get_material_cost(clinic_gesture)
        total_material_cost = total_material_cost + material_used_cost

    return total_duration_time, total_material_cost
    
def get_hourly_operational_cost():
    operations_cost = ( meta.session.query(cost.OperationCost)
        .filter(cost.OperationCost.active == True)
        .all()
    )
    hour_cost = 0
    for operation in operations_cost:
        if operation.periodicity == datetime.timedelta(days=365):
            h_cost = ( operation.cost / 52 ) / get_dental_unit_week_hours()
        elif operation.periodicity == datetime.timedelta(days=30):
            h_cost = ( operation.cost / 4.5 ) / get_dental_unit_week_hours()

        hour_cost = hour_cost + h_cost

    return hour_cost

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

        cg_mat_ref_list, material_used_cost =\
                                get_material_cost(cg_cot_ref.clinic_gesture)

        dictionnary[cg_cot_ref.appointment_number][2] = cg_mat_ref_list
        # cost of appointment in material
        dictionnary[cg_cot_ref.appointment_number][3] =\
            dictionnary[cg_cot_ref.appointment_number][3] +\
                                                        material_used_cost
    return dictionnary

def get_day_base_cost(day_base_duration, day_base_material, 
                                hourly_operational_cost, dentist_hour_fees):
    duration_day_base_cost = float(day_base_duration.total_seconds()) *\
                                                hourly_operational_cost / 3600
    day_base_cost = duration_day_base_cost + day_base_material

    return duration_day_base_cost, day_base_cost

def get_appointment_base_cost(appointment_base_duration, 
                                            appointment_base_material_cost,
                                            hourly_operational_cost,
                                            dentist_hour_fees):

    duration_appointment_base_cost =\
                        float(appointment_base_duration.total_seconds()) *\
                ( hourly_operational_cost + float(dentist_hour_fees) ) / 3600

    appointment_base_cost = duration_appointment_base_cost +\
                                        float(appointment_base_material_cost)

    return duration_appointment_base_cost, appointment_base_cost

def get_gestures_cost(gestures_duration, gestures_material_cost, 
                                hourly_operational_cost, dentist_hour_fees):
    duration_gestures_cost = (
                gestures_duration.total_seconds() *
            (hourly_operational_cost + float(dentist_hour_fees) ) / 3600
    )
    gestures_cost = duration_gestures_cost + float(gestures_material_cost)

    return duration_gestures_cost, gestures_cost

def get_cost_informations(cg_cot_dict, cotation_id):

    gestures_material_cost = 0
    gestures_duration = datetime.timedelta(seconds=0)

    cotation = ( meta.session.query(act.Cotation).filter(act.Cotation.id ==
                                                            cotation_id).one()
    )
    
    appointment_base_material_cost, appointment_base_duration =\
                                                    get_appointmently_data()

    for appointment in cg_cot_dict:
        # cost of materials specific to gesture
        gestures_material_cost = gestures_material_cost +\
                                                cg_cot_dict[appointment][3]
        # duration specific to gesture
        gestures_duration = gestures_duration + cg_cot_dict[appointment][1]

    day_base_duration, day_base_material_cost = get_daily_data()

    appointment_base_duration, appointment_base_material_cost =\
                                                    get_appointmently_data()

    duration_total = appointment_base_duration * len(cg_cot_dict) +\
                                                            gestures_duration
    dentist_hour_fees = get_dentist_hour_fees(cotation.healthcare_plan.id)
    hourly_operational_cost = get_hourly_operational_cost()

    duration_day_base_cost, day_base_cost =\
                                        get_day_base_cost(day_base_duration,
                                                    day_base_material_cost,
                                                    hourly_operational_cost,
                                                    dentist_hour_fees)

    duration_appointment_base_cost, appointment_base_cost =\
                        get_appointment_base_cost(appointment_base_duration,
                                            appointment_base_material_cost,
                                            hourly_operational_cost,
                                            dentist_hour_fees)

    duration_gestures_cost, gestures_cost =\
                        get_gestures_cost(gestures_duration,
                                            gestures_material_cost,
                                            hourly_operational_cost,
                                            dentist_hour_fees)
    total_duration = (
        day_base_duration * len(cg_cot_dict) +
        appointment_base_duration * len(cg_cot_dict) +
        gestures_duration
    )
    total_duration_cost = (
        total_duration.total_seconds() * 
                ( hourly_operational_cost + float(dentist_hour_fees) ) / 3600
    )
    total_material_cost = (
        day_base_material_cost * len(cg_cot_dict) +
        appointment_base_material_cost * len(cg_cot_dict) +
        gestures_material_cost
    )
    total_cost = (
        day_base_cost * len(cg_cot_dict) +
        appointment_base_cost * len(cg_cot_dict) +
        gestures_cost
    )

    cost_informations = {
        'day_base_duration': day_base_duration * len(cg_cot_dict),
        'duration_day_base_cost': duration_day_base_cost * len(cg_cot_dict),
        'appointment_base_duration': appointment_base_duration *\
                                                            len(cg_cot_dict),
        'duration_appointment_base_cost': duration_appointment_base_cost *\
                                                            len(cg_cot_dict),
        'gestures_duration': gestures_duration,
        'duration_gestures_cost': duration_gestures_cost,
        'day_base_material_cost': day_base_material_cost * len(cg_cot_dict),
        'day_base_cost': day_base_cost * len(cg_cot_dict),
        'appointment_base_material_cost': appointment_base_material_cost *\
                                                            len(cg_cot_dict),
        'appointment_base_cost': appointment_base_cost * len(cg_cot_dict),
        'gestures_material_cost': gestures_material_cost,
        'gestures_cost': gestures_cost,
        'dentist_hour_fees': dentist_hour_fees,
        'hourly_operational_cost': hourly_operational_cost,
        'dental_unit_week_hours': get_dental_unit_week_hours,
        'total_duration': total_duration,
        'total_duration_cost': total_duration_cost,
        'total_material_cost': total_material_cost,
        'total_cost': total_cost
    }
    
    return cost_informations

@app.route('/portal/operation_cost/', methods=['GET', 'POST'])
def portal_operation_cost():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)

    return render_template('operation_cost.html')

#@app.route('/update/annual_cost/', methods=['GET', 'POST'])
#def update_annual_cost():
#    authorized_roles = [ constants.ROLE_DENTIST ]
#    if session['role'] not in authorized_roles:
#        return abort(403)
#
#    return render_template('update_annual_cost.html')
#
#@app.route('/update/mensal_cost/', methods=['GET', 'POST'])
#def update_mensal_cost():
#    authorized_roles = [ constants.ROLE_DENTIST ]
#    if session['role'] not in authorized_roles:
#        return abort(403)
#
#    return render_template('update_anual_cost.html')
#
