# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/10/16
# 
# licence BSD
#

import pdb
from flask import ( session, render_template, request, redirect, url_for, 
                    jsonify, abort )
import sqlalchemy
from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks
from odontux.models import ( meta, act, schedule, administration, traceability,
                            assets, teeth, compta)
import teeth, cost


from odontux.views.log import index
#from odontux.views.patient import list_acts

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, IntegerField, validators,
                     FieldList, FormField, SubmitField)
from odontux.views.forms import ColorField
from decimal import Decimal
import datetime


class ClinicGestureInClinicReportForm(Form):
    appointment_id = HiddenField(_('appointment_id'))
    clinic_gesture_id = HiddenField(_('clinic_gesture_id'))
    anatomic_location = HiddenField(_('anatomic_location'))
    sequence = IntegerField(_('Sequence'))
    memo = TextAreaField(_('Memo'))
    delete = BooleanField(_('Delete'))

class ClinicReportForm(Form):
    clinic_gestures = FieldList(FormField(ClinicGestureInClinicReportForm),
                                                            min_entries=1)
    submit = SubmitField(_('Submit'))


class ClinicGesturesFromAdmGestureForm(Form):
    clinic_gesture_id = HiddenField(_('cg_id'))
    delete = BooleanField(_('Delete'))

class ClinicReportFromAdmGestureForm(Form):
    clinic_gestures = FieldList(FormField(ClinicGesturesFromAdmGestureForm),
                                                            min_entries=1)
    submit = SubmitField(_('Submit'))

class ClinicGesturesFromCotationForm(Form):
    clinic_gesture_id = HiddenField(_('cg_id'))
    delete = BooleanField(_('Delete'))

class ClinicReportFromCotationForm(Form):
    clinic_gestures = FieldList(FormField(ClinicGesturesFromCotationForm),
                                                            min_entries=1)
    submit = SubmitField(_('Submit'))

class ChooseCotationForReportForm(Form):
    anatomic_location = TextField(_('Anatomic location'), 
                                                    [validators.Required()])
    cotation_id = SelectField(_('Cotation'), coerce=int)
    submit = SubmitField(_('Choose from Cotation'))

class ChooseClinicGestureForReportForm(Form):
    anatomic_location = TextField(_('Anatomic location'), 
                                                    [validators.Required()])
    clinic_gesture_id = SelectField(_('Clinic Gesture'), coerce=int)
    submit = SubmitField(_('Choose clinic gesture'))

@app.route('/view/clinic_report?aid=<int:appointment_id>', 
                                                    methods=['GET'])
def view_clinic_report(appointment_id):
    patient, appointment = checks.get_patient_appointment( 
                                            appointment_id=appointment_id)

    cotation_form = ChooseCotationForReportForm(request.form)
    cotation_form.cotation_id.choices = [
        ( cotation.id, cotation.gesture.name) for cotation in
         meta.session.query(act.Cotation)
            .filter(act.Cotation.healthcare_plan_id.in_(
                                            [ hc.id for hc in patient.hcs ] )
            )
            .join(act.Gesture, act.Specialty)
            .order_by(act.Specialty.name,
                        act.Gesture.name )
            .all()
    ]
    cg_form = ChooseClinicGestureForReportForm(request.form)
    cg_form.clinic_gesture_id.choices = [
        ( cg.id, cg.specialty.name[0:3] + " " + cg.name ) for cg in
            meta.session.query(act.ClinicGesture)
                .filter(act.ClinicGesture.is_daily.is_(False),
                        act.ClinicGesture.is_appointmently.is_(False)
                )
                .join(act.Specialty)
                .order_by(act.Specialty.name,
                            act.ClinicGesture.name )
                .all()
    ]
    clinic_gestures = []
    for clinic_report in sorted(appointment.clinic_reports,
                            key=lambda clinic_report: clinic_report.sequence):

        clinic_gestures.append(clinic_report)
    
    materio_vigilance = [ 
        mat_vig for mat_vig in
            sorted(appointment.materio_vigilance, key=lambda mat_vig: (
                mat_vig.material.asset_category.asset_specialty.name,
                        mat_vig.material.asset_category.commercial_name
            )
        )
    ]
    return render_template('view_clinic_report.html', 
                            patient=patient,
                            appointment=appointment,
                            clinic_gestures=clinic_gestures,
                            materio_vigilance=materio_vigilance,
                            cotation_form=cotation_form,
                            cg_form=cg_form,
                            constants=constants)

@app.route('/choose/cg_from_cot_to_cr?aid=<int:appointment_id>')
def choose_clinic_gestures_from_cotation_to_clinic_report(appointment_id):
    pass

@app.route('/add/cg_from_cot_to_cr?aid=<int:appointment_id>'
            '&cid=<int:cotation_id>', methods=['GET', 'POST'] )
def add_clinic_gestures_from_cotation_to_clinic_report(appointment_id,
                                                            cotation_id):
    pass

def add_to_materio_vigilance(appointment_id, mat_cg_ref, material):
    """ 
        update both:
            materio_vigilance.quantity_used and material.actual_quantity
    """
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    material_in_materio_vigilance = ( 
        meta.session.query(traceability.MaterioVigilance)
            .filter(
                traceability.MaterioVigilance.appointment_id == appointment_id,
                traceability.MaterioVigilance.material_id == material.id )
            .one_or_none()
    )
    if not material_in_materio_vigilance:
        values = {
            'material_id': material.id,
            'appointment_id': appointment_id,
            'quantity_used': mat_cg_ref.mean_quantity
        }
        new_materio_vigilance = traceability.MaterioVigilance(**values)
        meta.session.add(new_materio_vigilance)
        meta.session.commit()
    else:
        material_in_materio_vigilance.quantity_used = (
            material_in_materio_vigilance.quantity_used + 
                                                    mat_cg_ref.mean_quantity
        )
        meta.session.commit()

    material.actual_quantity = ( material.actual_quantity - 
                                                    mat_cg_ref.mean_quantity )
    meta.session.commit()

def add_cg_to_cr(appointment_id, clinic_gesture_id, anatomic_location):
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    values = {
        'appointment_id': appointment_id,
        'clinic_gesture_id': clinic_gesture_id,
        'anatomic_location': anatomic_location,
    }
    new_cg_in_cr = act.ClinicReport(**values)
    meta.session.add(new_cg_in_cr)
#    appointment.clinic_reports.append(new_cg_in_cr)
    try:
        meta.session.commit()
        appointment.clinic_reports.reorder()
        meta.session.commit()
    except sqlalchemy.exc.IntegrityError:
        meta.session.rollback()

    for mat_cg_ref in new_cg_in_cr.clinic_gesture.materials:

        material_used = cost.get_material_used(mat_cg_ref.id)

        add_to_materio_vigilance(appointment_id, mat_cg_ref, material_used)

@app.route('/add/cg_to_cr?aid=<int:appointment_id>', methods=['POST'])
def add_clinic_gesture_to_clinic_report(appointment_id):
    form = ChooseClinicGestureForReportForm(request.form)
    form.clinic_gesture_id.choices = [
        ( cg.id, cg.specialty.name[0:3] + " " + cg.name ) for cg in
            meta.session.query(act.ClinicGesture)
                .filter(act.ClinicGesture.is_daily.is_(False),
                        act.ClinicGesture.is_appointmently.is_(False)
                )
                .join(act.Specialty)
                .order_by(act.Specialty.name,
                            act.ClinicGesture.name )
                .all()
    ]
    if form.validate():
        try:
            if int(form.anatomic_location.data):
                add_cg_to_cr(appointment_id, form.clinic_gesture_id.data,
                                                form.anatomic_location.data)
        except ValueError:
            for anatomic_location in\
                            teeth.get_teeth_list(form.anatomic_location.data) :
                add_cg_to_cr(appointment_id, form.clinic_gesture_id.data,
                                                        anatomic_location)
        
    return redirect(url_for('view_clinic_report', 
                                            appointment_id=appointment_id))

def remove_from_materio_vigilance(appointment_id, mat_cg_ref):
    """ 
        update both:
            materio_vigilance.quantity_used and material.actual_quantity
    """
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    material = ( 
        meta.session.query(assets.Material)
            .filter(
                assets.Material.asset_category_id ==
                                            mat_cg_ref.material_category_id, 
                assets.Material.id.in_( [ materio_vigilance.material_id 
                    for materio_vigilance in appointment.materio_vigilance
                    ]
                )
            )
        .first()
    )
    if material:
        materio_vigilance = ( meta.session.query(traceability.MaterioVigilance)
                .filter(
                    traceability.MaterioVigilance.appointment_id == 
                                                                appointment_id,
                    traceability.MaterioVigilance.material_id == material.id )
                .one()
        )
        if mat_cg_ref.mean_quantity >= materio_vigilance.quantity_used:
            meta.session.delete(materio_vigilance)
            meta.session.commit()
        else:
            materio_vigilance.quantity_used = ( 
                materio_vigilance.quantity_used - mat_cg_ref.mean_quantity 
            )
            materio_vigilance.material.actual_quantity = (
                                materio_vigilance.material.actual_quantity + 
                                                    mat_cg_ref.mean_quantity )
            meta.session.commit()


@app.route('/remove/cg_from_cr?crid=<int:clinic_report_id>')
def remove_cg_from_cr(clinic_report_id):
    clinic_report = ( meta.session.query(act.ClinicReport)
                        .filter(act.ClinicReport.id == clinic_report_id)
                        .one_or_none()
    )
    for mat_cg_ref in clinic_report.clinic_gesture.materials:
        remove_from_materio_vigilance(clinic_report.appointment_id,
                                                                mat_cg_ref )
        appointment = (meta.session.query(schedule.Appointment)
            .filter(schedule.Appointment.id == clinic_report.appointment_id)
            .one()
    )
    meta.session.delete(clinic_report)
    try:
        meta.session.commit()
        appointment.clinic_reports.reorder()
        meta.session.commit()
    except sqlalchemy.exc.InvalidRequestError:
        meta.session.rollback()
    return redirect(url_for('view_clinic_report', 
                                                appointment_id=appointment.id))


#def add_clin_gest_on_clin_report_from_adm_gest(app_cot_ref_id):
#    app_cot_ref = ( meta.session.query(act.AppointmentCotationReference)
#                .filter(act.AppointmentCotationReference.id == app_cot_ref_id )
#                .one()
#    )
#    
#    clinic_report_form = ClinicReportFromAdmGestureForm(request.form)
#    
#    if request.method == 'POST' and cg_form.validate():
#        pass
#    
#    for cg_data in sorted(app_cot_ref.cotation.clinic_gestures,
#                        key=lambda cg_data: ( cg_data.appointment_number,
#                                            cg_data.appointment_sequence,
#                                            cg_data.clinic_gesture.name ) )
#        cg_form = ClinicGestureFromAdmGestureForm(request.form)
#
#        cg_form.clinic_gestures_id = cg_data.clinic_gesture_id
#        cg_form.clinic_gestures_delete = False
#
#        clinic_report.form.append_entry(cg_form)
#
#    return render_template('choose_clinic_gestures_from_adm_gesture.html',
#                                                    app_cot_ref=app_cot_ref)
