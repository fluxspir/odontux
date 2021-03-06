# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/10/13
# 
# Licence BSD
#

import pdb
from flask import render_template, request, redirect, url_for, session, abort
from wtforms import ( Form, IntegerField, SubmitField, TextField, DecimalField,
                        TextAreaField, BooleanField, RadioField, HiddenField,
                        validators )
#from wtforms.fields.html5 import DateField
from gettext import gettext as _
from sqlalchemy import or_
from sqlalchemy import cast, Date, Time
import datetime
import decimal

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, users, act, assets, cost
#from odontux.views.forms import TimeField
from odontux.views.log import index

class ClinicGestureCotationReferenceForm(Form):
    appointment_number = IntegerField(_('Appointment_number'), 
                                                    render_kw={'size':'4'})
    sequence = IntegerField(_('Sequence'),
                                                    render_kw={'size':'4'})
    official_cotation = BooleanField(_('official'))
    appears_on_clinic_report = BooleanField(_('Clinic Report'))
    submit = SubmitField(_('Update'))

class OperationalCostForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Operation name'), [validators.Required()])
    description = TextAreaField(_('Description'))
    active = BooleanField(_('active'), default=True)
    cost = DecimalField(_('Cost'), render_kw={'size': 4})
    periodicity = RadioField(_('Periodicity'), choices=[ 
                                                ( 'yearly', _('Yearly') ),
                                                ( 'monthly', _('Monthly') ) ] )
    submit = SubmitField(_('Submit'))

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

def get_material_used(cg_mat_ref_id, appointment=None, 
                                                    sterilization_cycle=None):
    def _update_materials_potentials(materials, appointment=None,
                                                    sterilization_cycle=None):
        materials = ( materials
            .filter(assets.Material.actual_quantity <= 0)
            .all()
        ) 
        for material in materials:
            if material.actual_quantity <= 0:
                if appointment:
                    material.end_of_use = appointment.agenda.starttime.date()
                elif sterilization_cycle:
                    material.end_of_use = sterilization_cycle.cycle_date
                else:
                    material.end_of_use = datetime.date.today()
                material.end_use_reason = constants.END_USE_REASON_NATURAL_END
                meta.session.commit()


    cg_mat_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(assets.MaterialCategoryClinicGestureReference.id == 
                                                                cg_mat_ref_id
            ).one()
    )
    materials_potentials = ( meta.session.query(assets.Material)
        .filter(
            assets.Material.asset_category_id == 
                                    cg_mat_ref.material_category_id,
            assets.Material.end_of_use.is_(None),
            assets.Material.end_use_reason == 
                                        constants.END_USE_REASON_IN_USE_STOCK,
        )
    )

    _update_materials_potentials(materials_potentials, appointment, 
                                                        sterilization_cycle)

    materials_potentials = ( materials_potentials
                .filter(assets.Material.actual_quantity > 0)
    )
    material_in_use = ( materials_potentials
                .filter(assets.Material.start_of_use.isnot(None))
        .first()
    )

    if material_in_use:
        material_used = material_in_use
    else:
        material_used = (
            materials_potentials.order_by(assets.Material.expiration_date)
            .first()
        )
        if not material_used:
            return None

        if appointment:
            material_used.start_of_use = appointment.agenda.starttime.date()
        elif sterilization_cycle:
            material_used.start_of_use = sterilization_cycle.cycle_date
        else:
            material_used.start_of_use = datetime.date.today()
        meta.session.commit()
    return material_used

def get_material_cost(cg_mat_ref_id):
    cg_mat_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(assets.MaterialCategoryClinicGestureReference.id == 
                                                                cg_mat_ref_id
            ).one()
    )

    material_used = get_material_used(cg_mat_ref_id)
    if not material_used:
        return get_material_category_cost(cg_mat_ref_id)
                
    if not cg_mat_ref.mean_quantity:
        cg_mat_ref.mean_quantity =\
                                material_used.asset_category.automatic_decrease

    material_used_cost = ( 
        (
            (        
                cg_mat_ref.mean_quantity / 
                material_used.asset_category.initial_quantity 
            ) 
                * material_used.acquisition_price
        )
            / cg_mat_ref.enter_in_various_gestures
    )
    return material_used_cost

def get_material_category_cost(cg_mat_ref_id):
    cg_mat_ref = ( 
        meta.session.query(assets.MaterialCategoryClinicGestureReference)
            .filter(assets.MaterialCategoryClinicGestureReference.id == 
                                                            cg_mat_ref_id )
            .one()
    )
    material_category = ( meta.session.query(assets.AssetCategory)
        .filter(assets.AssetCategory.id == cg_mat_ref.material_category_id)
        .one()
    )
    
    if material_category.last_price is None:
        material_category.last_price = 0

    material_used_cost = (
        (
            (
                cg_mat_ref.mean_quantity /
                material_category.initial_quantity
            )
                * material_category.last_price
        )
            / cg_mat_ref.enter_in_various_gestures
    )
    
    return material_used_cost

def get_material_cost_in_clinic_gesture(clinic_gesture):
    cg_mat_ref_list = []
    material_used_cost = 0
    for cg_mat_ref in clinic_gesture.materials:
        cg_mat_ref_list.append(cg_mat_ref)
        material_used_cost = ( 
            material_used_cost + get_material_cost(cg_mat_ref.id)
        )
    return cg_mat_ref_list, material_used_cost

def get_daily_data():
    daily = (
        meta.session.query(act.ClinicGesture)
            .filter(or_(
                act.ClinicGesture.before_first_patient.is_(True),
                act.ClinicGesture.after_last_patient.is_(True)
                ) )
            .all()
    )
    material_cost = 0
    duration = datetime.timedelta(seconds=0)
    for clinic_gesture in daily:
        duration = duration + clinic_gesture.duration
        material_cost = ( material_cost + 
                        get_material_cost_in_clinic_gesture(clinic_gesture)[1]
        )

    return duration, material_cost

def get_appointmently_data():
    appointmently = ( 
        meta.session.query(act.ClinicGesture)
            .filter(or_(
                act.ClinicGesture.before_each_appointment.is_(True),
                act.ClinicGesture.after_each_appointment.is_(True)
            ))
            .all()
    )
    total_material_cost = 0
    total_duration_time = datetime.timedelta(seconds=0)
    for clinic_gesture in appointmently:
        total_duration_time = total_duration_time + clinic_gesture.duration
        
        cg_mat_ref_list, material_used_cost =\
                get_material_cost_in_clinic_gesture(clinic_gesture)
        total_material_cost = total_material_cost + material_used_cost

    return total_duration_time, total_material_cost
    
def get_hourly_operational_cost():
    operations_cost = ( meta.session.query(cost.OperationalCost)
        .filter(cost.OperationalCost.active == True)
        .all()
    )
    hour_cost = 0
    for operation in operations_cost:
        if operation.periodicity == datetime.timedelta(days=365):
            h_cost = ( float(operation.cost) / (
                ( get_dental_unit_week_hours().total_seconds() / 3600 ) * 52 )
            )
        elif operation.periodicity == datetime.timedelta(days=30):
            h_cost = ( float(operation.cost) /  (
                ( get_dental_unit_week_hours().total_seconds() / 3600 ) * 4.5 )
            )

        hour_cost = hour_cost + h_cost
    return hour_cost

def get_cotation_dictionary(cotation_id):
    """
        dictionnary = {
            int(appointment_number): [
                                [ object(cg_cot_ref), wtform(ref_form) ],
                                duration = datetime.timedelta(),
                                [ object(mat_cg_ref) ],
                                float(cost),
                            ],
        }
    """
    cotation = ( meta.session.query(act.Cotation)
                    .filter(act.Cotation.id == cotation_id)
                    .one()
    )
    dictionnary = {}
    # create cg_in_cotation = list of clinics gestures in this cotation
    # create materials_used = list of materials that may be used
    for cg_cot_ref in sorted(cotation.clinic_gestures,
                        key=lambda cg_cot_ref: ( cg_cot_ref.appointment_number,
                                            cg_cot_ref.sequence) ):
        if cg_cot_ref.appointment_number not in dictionnary:
            dictionnary[cg_cot_ref.appointment_number] = [ 
                                                [], # ( cg_cot_ref, ref_form )
                                                datetime.timedelta(seconds=0), #duration
                                                [], # cg_mat_ref list
                                                0, # material_cost
            ]

        ref_form = ClinicGestureCotationReferenceForm(request.form)
        ref_form.official_cotation.data = cg_cot_ref.official_cotation
        ref_form.appears_on_clinic_report.data =\
                                    cg_cot_ref.appears_on_clinic_report
        ref_form.appointment_number.data = cg_cot_ref.appointment_number
        ref_form.sequence.data = cg_cot_ref.sequence

        dictionnary[cg_cot_ref.appointment_number][0].append( 
                                                    ( cg_cot_ref, ref_form ) )
        
        dictionnary[cg_cot_ref.appointment_number][1] =\
            dictionnary[cg_cot_ref.appointment_number][1] +\
                                            cg_cot_ref.clinic_gesture.duration

        cg_mat_ref_list, material_used_cost =\
                get_material_cost_in_clinic_gesture(cg_cot_ref.clinic_gesture)

        dictionnary[cg_cot_ref.appointment_number][2] = cg_mat_ref_list
        # cost of appointment in material
        if cg_cot_ref.appears_on_clinic_report:
            dictionnary[cg_cot_ref.appointment_number][3] =\
                dictionnary[cg_cot_ref.appointment_number][3] +\
                                                        material_used_cost
    return dictionnary

def get_day_base_cost(day_base_duration, day_base_material, 
                                hourly_operational_cost, dentist_hour_fees):
    duration_day_base_cost = float(day_base_duration.total_seconds()) *\
                                                hourly_operational_cost / 3600
    day_base_cost = duration_day_base_cost + float(day_base_material)

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
        'duration_day_base_cost': "{0:.2f}".format(
                                    duration_day_base_cost * len(cg_cot_dict)),
        'appointment_base_duration': appointment_base_duration *\
                                                            len(cg_cot_dict),
        'duration_appointment_base_cost': "{0:.2f}".format(
                            duration_appointment_base_cost * len(cg_cot_dict)),
        'gestures_duration': gestures_duration,
        'duration_gestures_cost': "{0:.2f}".format(duration_gestures_cost),
        'day_base_material_cost': "{0:.2f}".format(
                                    day_base_material_cost * len(cg_cot_dict)),
        'day_base_cost': "{0:.2f}".format(day_base_cost * len(cg_cot_dict)),
        'appointment_base_material_cost': "{0:.2f}".format(
                            appointment_base_material_cost * len(cg_cot_dict)),
        'appointment_base_cost': "{0:.2f}".format(
                                    appointment_base_cost * len(cg_cot_dict)),
        'gestures_material_cost': "{0:.2f}".format(gestures_material_cost),
        'gestures_cost': "{0:.2f}".format(gestures_cost),
        'dentist_hour_fees': dentist_hour_fees,
        'hourly_operational_cost': "{0:.2f}".format(hourly_operational_cost),
        'dental_unit_week_hours': get_dental_unit_week_hours,
        'total_duration': total_duration,
        'total_duration_cost': "{0:.2f}".format(total_duration_cost),
        'total_material_cost': "{0:.2f}".format(total_material_cost),
        'total_cost': "{0:.2f}".format(total_cost),
    }
    
    return cost_informations

@app.route('/portal/operation_cost/', methods=['GET', 'POST'])
def portal_operational_cost():
    authorized_roles = [ constants.ROLE_ADMIN, constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    operations = ( meta.session.query(cost.OperationalCost)
                    .filter(cost.OperationalCost.active == True)
                    .all()
    )
    office_operations = []
    for operation in operations:
        hour_cost = ( float(operation.cost) / 
        ( operation.periodicity.total_seconds() /
            get_dental_unit_week_hours().total_seconds())
        )
        office_operations.append( (operation, 
            "{0:.2f}".format(hour_cost)) )
#            round(hour_cost,2) ) )
    return render_template('operational_cost.html', 
                                            operations=office_operations,
                                            constants=constants)

@app.route('/add/operation_cost/', methods=['POST'])
def add_operation_cost():
    authorized_roles = [ constants.ROLE_ADMIN ]
    if session['role'] not in authorized_roles:
        return abort(403)
    form = OperationalCostForm(request.form)
    if form.validate():
        if form.periodicity.data == 'yearly':
            period = datetime.timedelta(days=365)
        elif form.periodicity.data == 'monthly':
            period = datetime.timedelta(days=30)
        else:
            period = datetime.timedelta(days=1)

        values = {
            'name': form.name.data,
            'description': form.description.data,
            'cost': form.cost.data,
            'active': True,
            'periodicity': period,
        }
        new_op_cost = cost.OperationalCost(**values)
        meta.session.add(new_op_cost)
        meta.session.commit()

    return redirect(url_for('update_operational_cost'))

@app.route('/update/operational_cost/', methods=['GET', 'POST'])
def update_operational_cost():
    authorized_roles = [ constants.ROLE_ADMIN ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    operations = meta.session.query(cost.OperationalCost).all()
    ope_cost_form = OperationalCostForm(request.form)
    if request.method == 'POST' and ope_cost_form.validate():
        operation = ( meta.session.query(cost.OperationalCost)
                    .filter(cost.OperationalCost.id == ope_cost_form.id.data)
                    .one()
        )
        if ope_cost_form.periodicity.data == 'yearly':
            period = datetime.timedelta(days=365)
        elif ope_cost_form.periodicity.data == 'monthly':
            period = datetime.timedelta(days=30)
        else:
            period = datetime.timedelta(days=1)
        
        for c in "name", 'description', 'cost', 'active':
            setattr(operation, c, getattr(ope_cost_form, c).data)
        operation.periodicity = period
        meta.session.commit()
        return redirect(url_for('update_operational_cost'))

    office_operations = []
    for operation in operations:
        form = OperationalCostForm(request.form)
        for c in 'id', "name", "description", "cost":
            setattr(getattr(form, c), 'data', getattr(operation, c))
        if operation.periodicity == datetime.timedelta(days=365):
            form.periodicity.data = 'yearly'
            hours = get_dental_unit_week_hours().total_seconds() / 3600 * 52
        elif operation.periodicity == datetime.timedelta(days=30):
            form.periodicity.data = 'monthly'
            hours = get_dental_unit_week_hours().total_seconds() / 3600 * 4.5
        else:
            form.periodicity.data = 'yearly'
            hours = get_dental_unit_week_hours().total_seconds() * 52
        
        #"periodicity"
        hour_cost = operation.cost / decimal.Decimal(hours)
        office_operations.append( ( operation, "{0:.2f}".format(hour_cost), 
                                                                        form) )
    return render_template('update_operational_cost.html', 
                                        operations=office_operations,
                                                ope_cost_form=ope_cost_form,
                                                constants=constants)

