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
from sqlalchemy import cast, Date
from sqlalchemy.orm import with_polymorphic
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import ( meta, act, schedule, administration, traceability,
                            assets, compta)
from odontux.models import teeth as model_teeth
from odontux.views import teeth, cost


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

class ClinicGestureKeepForm(Form):
    clinic_gesture_id = HiddenField(_('cg_id'))
    clinic_gesture_data = HiddenField(_('cg_data'))
    keep = BooleanField(_('Keep'))

class ClinicGesturesFromCotationForm(Form):
    price = DecimalField(_('Price'))
    clinic_gestures = FieldList(FormField(ClinicGestureKeepForm))
    submit = SubmitField(_('Submit'))

class ChooseCotationForReportForm(Form):
    anatomic_location = TextField(_('Anatomic location'))
    cotation_id = SelectField(_('Cotation'), coerce=int)
    submit = SubmitField(_('Choose from Cotation'))

class ChooseClinicGestureForReportForm(Form):
    anatomic_location = TextField(_('Anatomic location'))
    clinic_gesture_id = SelectField(_('Clinic Gesture'), coerce=int)
    submit = SubmitField(_('Choose clinic gesture'))

class ChooseMaterialForReportForm(Form):
    material_id = SelectField(_('Material'), coerce=int)
    submit = SubmitField(_('Choose material'))

class MaterioVigilanceForm(Form):
    material_id = HiddenField(_('Material id'))
    old_quantity_used = HiddenField(_('Old Quantity Used'))
    new_quantity_used = DecimalField(_('Quantity used'), 
                                [validators.Optional()],
                                render_kw={'size':4})
    material_data = HiddenField(_('material_data'))

class ClinicGestureDurationForm(Form):
    clinic_report_id = HiddenField(_('clinic_report_id'))
    clinic_gesture_id = HiddenField(_('Clinic Gesture id'))
    anatomic_location = HiddenField(_('Anatomic location'))
    old_duration = HiddenField(_('Old clinic gesture duration'))
    new_duration = IntegerField(_('Clinic gesture duration'),
                                    [validators.Optional()],
                                    render_kw={'size': 4})
    clinic_gesture_data = HiddenField(_('cg_data'))

class ClinicReportForm(Form):
    materials_used = FieldList(FormField(MaterioVigilanceForm))
    clinic_gestures = FieldList(FormField(ClinicGestureDurationForm))
    update = SubmitField(_('Update'))


def anat_loc_is_list(anat_loc=""):
    """we want to recognize teeth ( 9 < teeth < 100 )
                   teeth sets ( 0 <= region < 10 )
        exoendobuccal regions ( 99 < exoendobuccal
    """
    if not anat_loc:
        anat_loc = 0
    try:
        if int(0) >= 0:
            return False
    except ValueError:
        return True
    else:
        return None

@app.route('/view/clinic_report?aid=<int:appointment_id>', 
                                                    methods=['GET'])
def view_clinic_report(appointment_id):
    patient, appointment = checks.get_patient_appointment( 
                                            appointment_id=appointment_id)

    cotation_form = ChooseCotationForReportForm(request.form)
    cotation_form.cotation_id.choices = [
        ( cotation.id, cotation.gesture.name +  " " + 
            cotation.healthcare_plan.name) for cotation in
         meta.session.query(act.Cotation)
            .filter(act.Cotation.healthcare_plan_id.in_(
                                            [ hc.id for hc in patient.hcs ] )
            )
            .join(act.Gesture, act.Specialty, act.HealthCarePlan)
            .order_by(act.Specialty.name,
                        act.Gesture.name,
                        act.HealthCarePlan.name.desc())
            .all()
    ]
    cg_form = ChooseClinicGestureForReportForm(request.form)
    cg_form.clinic_gesture_id.choices = [
        ( cg.id, cg.specialty.name[0:3] + " " + cg.name ) for cg in
            meta.session.query(act.ClinicGesture)
                .filter(act.ClinicGesture.before_first_patient.is_(False),
                        act.ClinicGesture.after_last_patient.is_(False),
                        act.ClinicGesture.before_each_appointment.is_(False),
                        act.ClinicGesture.after_each_appointment.is_(False)
                )
                .join(act.Specialty)
                .order_by(act.Specialty.name, act.ClinicGesture.name )
                .all()
    ]
    clinic_report_form = ClinicReportForm(request.form)

    clinic_gestures = [ clinic_report for clinic_report in 
                            sorted(appointment.clinic_reports,
                                key=lambda clinic_report: 
                                    clinic_report.sequence) 
    ]

    # Case dentist_fees and hour_cost isn't provided yet:
    if not appointment.dentist_fees:
        appointment.dentist_fees = ( 
            meta.session.query(act.HealthCarePlanUserReference.hour_fees)
                .filter(
                    act.HealthCarePlanUserReference.user_id == 
                                                        appointment.dentist_id,
                    act.HealthCarePlanUserReference.healthcare_plan_id.in_(
                        [ hcp.id for hcp in appointment.patient.hcs ] )
                )
                .order_by(act.HealthCarePlanUserReference.hour_fees)
                .first()
        )
        if not appointment.dentist_fees:
            appointment.dentist_fees = 1

        meta.session.commit()

    if not appointment.hour_cost:
        appointment.hour_cost = round(cost.get_hourly_operational_cost(), 2)
        meta.session.commit()

    # In case this day is the first where happens something, we add in this 
    # clinic report the material that is used every morning and every night 
    # before opening and closing the dental_unit
    # We need to check this first.
    # TODO Add a verification if material found is only materials use in an
    # autoclave cycle because it doesn't count
    material_used_this_day = ( 
        meta.session.query(traceability.MaterioVigilance)
        .filter(
            traceability.MaterioVigilance.appointment_id.in_(
                meta.session.query(schedule.Agenda.appointment_id)
                    .filter(
                        cast(schedule.Agenda.starttime, Date) == 
                                        appointment.agenda.starttime.date(),
                        schedule.Agenda.dental_unit_id ==
                                                    appointment.dental_unit_id
                    )
            )
        )
        .all()
    )
    # In case no material has been marqued used in this appointment, we now add
    # the minimum material used in each appointment
    # This query is made before adding eventual "material before first patient
    # TODO Add a verification if material found is only materials use in an
    # autoclave cycle because it doesn't count
    material_each_appointment = ( 
        meta.session.query(traceability.MaterioVigilance)
        .filter(traceability.MaterioVigilance.appointment_id == appointment.id)
        .all()
    )

    if not material_used_this_day:
        cg_every_work_day = (  meta.session.query(act.ClinicGesture)
            .filter(or_(
                act.ClinicGesture.before_first_patient.is_(True),
                act.ClinicGesture.after_last_patient.is_(True)
                ) )
            .all()
        )
        for cg in cg_every_work_day:
            for mat_cg_ref in cg.materials:
                material_used = cost.get_material_used(mat_cg_ref.id)
                opening_materio_vigilance = add_to_materio_vigilance(
                    appointment.id, mat_cg_ref.mean_quantity, material_used)

    if not material_each_appointment:
        cg_all_appointment = ( meta.session.query(act.ClinicGesture)
            .filter(or_(
                act.ClinicGesture.before_each_appointment.is_(True),
                act.ClinicGesture.after_each_appointment.is_(True)
                ) )
            .all()
        )
        for cg in cg_all_appointment:
            for mat_cg_ref in cg.materials:
                material_used = cost.get_material_used(mat_cg_ref.id)
                materio_vigilance_appointment = add_to_materio_vigilance(
                    appointment.id, mat_cg_ref.mean_quantity, material_used)

    material_form = ChooseMaterialForReportForm(request.form)
    
    materials_for_materio_vigilance = (
        meta.session.query(assets.Material)
            .filter(
                assets.Material.end_of_use.is_(None),
                assets.Material.end_use_reason ==
                                    constants.END_USE_REASON_IN_USE_STOCK,
                assets.Material.start_of_use.isnot(None),
                ~assets.Material.id.in_(
                    meta.session.query(
                        traceability.MaterioVigilance.material_id)
                        .filter(traceability.MaterioVigilance.appointment_id ==
                                                                appointment.id
                    )
                )
            )
            .join(assets.MaterialCategory, act.Specialty)
            .order_by(
                act.Specialty.name,
                assets.MaterialCategory.commercial_name,
                assets.MaterialCategory.brand )
            .all()
    )
    material_form.material_id.choices = [ 
        ( material.id, material.asset_category.commercial_name + " " +
                        material.asset_category.brand ) for material in
                        materials_for_materio_vigilance 
    ]

    # only appears cotation that were administraly officially indentified,
    # by a single clinic gesture in the global gesture repair.
    cotations = [ cot for cot in sorted(appointment.administrative_gestures,
                                key=lambda cot: (
                                    cot.gesture.name,
                                    cot.anatomic_location ) )
    ]
    
    for mat_vig in sorted(appointment.materio_vigilance, key=lambda mat_vig:(
                        mat_vig.material.asset_category.asset_specialty.name,
                            mat_vig.material.asset_category.commercial_name) ):

        mat_vig_form = MaterioVigilanceForm(request.form)
        mat_vig_form.material_id = mat_vig.material_id
        mat_vig_form.old_quantity_used = mat_vig.quantity_used
        mat_vig_form.new_quantity_used = mat_vig.quantity_used
        mat_vig_form.material_data = (
            mat_vig.material.asset_category.commercial_name + " | " +
            str(mat_vig.material.actual_quantity) + " " +
            constants.UNITIES[mat_vig.material.asset_category.unity][1] )

        clinic_report_form.materials_used.append_entry(mat_vig_form)

    for clinic_report in sorted(appointment.clinic_reports, 
                                    key=lambda clinic_report: (
                                        clinic_report.anatomic_location,
                                        clinic_report.sequence )
                                                                        ):
        
        hour_duration = clinic_report.duration.seconds / 3600 * 60
        minute_duration = clinic_report.duration.seconds % 3600 / 60
        cg_duration_form = ClinicGestureDurationForm(request.form)
        cg_duration_form.clinic_report_id = clinic_report.id
        cg_duration_form.clinic_gesture_id = clinic_report.clinic_gesture_id
        cg_duration_form.anatomic_location = clinic_report.anatomic_location
        cg_duration_form.old_duration = str(hour_duration + minute_duration)
        cg_duration_form.new_duration = hour_duration + minute_duration
        cg_duration_form.clinic_gesture_data =\
                                            clinic_report.clinic_gesture.name

        clinic_report_form.clinic_gestures.append_entry(cg_duration_form)

    return render_template('view_clinic_report.html', 
                            patient=patient,
                            appointment=appointment,
                            cotations=cotations,
                            clinic_report_form=clinic_report_form,
                            cotation_form=cotation_form,
                            cg_form=cg_form,
                            material_form=material_form,
                            constants=constants)

@app.route('/update/clinic_report?aid=<int:appointment_id>', methods=['POST'])
def update_clinic_report(appointment_id):

    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    clinic_report_form = ClinicReportForm(request.form)
    if clinic_report_form.validate():
        for entry in clinic_report_form.clinic_gestures.entries:
            if entry.old_duration.data != entry.new_duration.data:
                clinic_report = ( meta.session.query(act.ClinicReport)
                    .filter(act.ClinicReport.id == 
                                        int(entry.clinic_report_id.data) )
                    .one()
                )
                clinic_report.duration = datetime.timedelta(
                        seconds=int(entry.new_duration.data) * 60 )
                meta.session.commit()
                
        for entry in clinic_report_form.materials_used.entries:
            if entry.new_quantity_used.data is None:
                entry.new_quantity_used.data = 0
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
                                                                appointment.id,
                        traceability.MaterioVigilance.material_id == 
                                                                material.id)
                    .one()
            )

            delta_quantity = Decimal(entry.old_quantity_used.data) -\
                                                entry.new_quantity_used.data
            materio_vigilance.quantity_used -= delta_quantity
            material.actual_quantity += delta_quantity
            meta.session.commit()
            # Case the material was marked as terminated, but finally there is
            # some left :
            if ( material.end_of_use == appointment.agenda.endtime.date()
                    and material.end_use_reason == 
                                        constants.END_USE_REASON_NATURAL_END
                    and material.actual_quantity > 0 ):
                material.end_of_use = None
                material.end_use_reason = constants.END_USE_REASON_IN_USE_STOCK
                meta.session.commit()

            # Case material terminate :
            if material.actual_quantity <= 0:
                material.end_of_use = appointment.agenda.endtime.date()
                material.end_use_reason = constants.END_USE_REASON_NATURAL_END
                meta.session.commit()

    return redirect(url_for('view_clinic_report', 
                                                appointment_id=appointment.id))

def add_appointment_cotation(appointment_id, cotation_id, price,
                                                            anatomic_location):
    values = {
        'appointment_id': appointment_id,
        'cotation_id': cotation_id,
        'anatomic_location': anatomic_location,
    }
    if not price:
        values['is_paid'] = True
        values['price'] = 0
    else:
        values['price'] = price
    new_appointment_cotation_ref = act.AppointmentCotationReference(**values)
    meta.session.add(new_appointment_cotation_ref)
    meta.session.commit()

    invoice = gnucash_handler.GnuCashInvoice(
                        new_appointment_cotation_ref.appointment.patient.id, 
                                new_appointment_cotation_ref.appointment_id, 
                        new_appointment_cotation_ref.appointment.dentist_id)

    invoice_id = invoice.add_act(new_appointment_cotation_ref.gesture.name, 
                                            new_appointment_cotation_ref.price,
                                            new_appointment_cotation_ref.id)

    new_appointment_cotation_ref.invoice_id = invoice_id
    meta.session.commit()

    return new_appointment_cotation_ref

@app.route('/choose/cg_from_cot_inserted_in_cr?aid=<int:appointment_id>'
            '&cid=<int:cotation_id>&aloc=<anat_loc>', methods=['POST'])
def choose_cg_from_cot_inserted_in_cr(appointment_id, cotation_id, anat_loc):

    def _add_cg_to_cr(a_id, cg_id, anat_loc, cot_id, price):

        clinic_report = add_cg_to_cr(a_id, cg_id, anat_loc)

        cg_cot_refs = ( 
            meta.session.query(act.ClinicGestureCotationReference)
            .filter(
                act.ClinicGestureCotationReference.clinic_gesture_id == cg_id,
                act.ClinicGestureCotationReference.cotation_id == cot_id)
            .all()
        )

        for cg_cot_ref in cg_cot_refs:
            if cg_cot_ref.official_cotation:
                new_administrativ_cotation = add_appointment_cotation(
                                                    appointment_id=a_id,
                                                    cotation_id=cot_id,
                                                    price=price,
                                                    anatomic_location=anat_loc
                )

    form = ClinicGesturesFromCotationForm(request.form)
    if form.validate():
        cotation = ( meta.session.query(act.Cotation)
            .filter(act.Cotation.id == cotation_id)
            .one()
        )
        for entry in form.clinic_gestures.entries:
            if not entry.keep.data:
                continue
            if anat_loc_is_list(anat_loc):
                for anatomic_location in teeth.get_teeth_list(anat_loc):
                    clinic_report = _add_cg_to_cr(appointment_id, 
                                        int(entry.clinic_gesture_id.data),
                                        anatomic_location,
                                        cotation_id,
                                        form.price.data)
            else:
                clinic_report = _add_cg_to_cr(appointment_id, 
                                        int(entry.clinic_gesture_id.data), 
                                        str(anat_loc),
                                        cotation_id,
                                        form.price.data)
    
    return redirect(url_for('view_clinic_report', 
                                                appointment_id=appointment_id))

@app.route('/choose/cg_from_cot?aid=<int:appointment_id>', methods=['POST'])
def choose_clinic_gestures_from_cotation(appointment_id):
    """
        The POST action comes from view_clinic_report.
    """
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    form = ChooseCotationForReportForm(request.form)
    form.cotation_id.choices = [ (cot.id, cot.gesture.name) for cot in
        meta.session.query(act.Cotation)
            .join(act.Gesture, act.Specialty)
            .order_by(act.Specialty.name, act.Gesture.name)
            .all()
    ]
    if form.validate():
        # define which cotation we are working with
        cotation = ( meta.session.query(act.Cotation)
            .filter(act.Cotation.id == form.cotation_id.data)
            .one()
        )
        # Define anatomic_locations we are working with
        anatomic_locations = ""
        if not form.anatomic_location.data:
            form.anatomic_location.data = 0
        try:
            if int(form.anatomic_location.data) >= 0 :
                anatomic_locations = str(form.anatomic_location.data)
        except ValueError:
            for idx, anat_loc in\
                enumerate(teeth.get_teeth_list(form.anatomic_location.data)) :
                if idx:
                    anatomic_locations = anatomic_locations + ","
                anatomic_locations = anatomic_locations + str(anat_loc)

        # create form with clinic_gestures associated with this cotation
        cg_form = ClinicGesturesFromCotationForm(request.form)
        for cg_cot_ref in sorted(cotation.clinic_gestures,
                                key=lambda cg_cot_ref: (
                                    cg_cot_ref.appointment_number,
                                    cg_cot_ref.sequence )
                                                                         ):
            cg_keep_form = ClinicGestureKeepForm(request.form)
            cg_keep_form.clinic_gesture_id = cg_cot_ref.clinic_gesture_id
            cg_keep_form.clinic_gesture_data = cg_cot_ref.clinic_gesture.name
            cg_keep_form.keep = cg_cot_ref.appears_on_clinic_report
            cg_form.clinic_gestures.append_entry(cg_keep_form)
        
#        cg_form.clinic_gestures.entries = [ entry for entry in 
#            cg_form.clinic_gestures.entries if entry.data['clinic_gesture_id'] 
#        ]
        cg_form.price.data = cotation.price
        return render_template('choose_clinic_gestures_from_cotation.html', 
                                    anatomic_locations=anatomic_locations,
                                                    patient=patient,
                                                    appointment=appointment,
                                                    cotation_id=cotation.id,
                                                                form=cg_form,
                                                    constants=constants)
    return redirect(url_for('view_clinic_report', 
                                                appointment_id=appointment.id))
 
def add_to_materio_vigilance(appointment_id, quantity, material):
    """ 
        update both:
            materio_vigilance.quantity_used and material.actual_quantity
    """
    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    materio_vigilance = ( 
        meta.session.query(traceability.MaterioVigilance)
            .filter(
                traceability.MaterioVigilance.appointment_id == appointment_id,
                traceability.MaterioVigilance.material_id == material.id )
            .one_or_none()
    )
    if not materio_vigilance:
        values = {
            'material_id': material.id,
            'appointment_id': appointment_id,
            'quantity_used': quantity
        }
        new_materio_vigilance = traceability.MaterioVigilance(**values)
        meta.session.add(new_materio_vigilance)
        meta.session.commit()
        materio_vigilance = new_materio_vigilance
    else:
        materio_vigilance.quantity_used = (
            materio_vigilance.quantity_used + quantity )
        meta.session.commit()

    material.actual_quantity = ( material.actual_quantity - quantity )
    meta.session.commit()
    return materio_vigilance

def add_cg_to_cr(appointment_id, clinic_gesture_id, anatomic_location):
    """
        anatomic_location = int.
        * Create a clinic_report entry with a clinic_gesture.
        * Add material in use from model_material_category from clinic_gesture
        to MaterioVigilance and update quantities
        * If clinic_gesture as a model_event, create the event adapted
    """
    def _needs_redondance(appointment, material, mat_cg_ref):

        number_of_same_cg_in_appointment = [ cr.clinic_gesture for cr in
                                            appointment.clinic_reports 
            if cr.clinic_gesture_id == mat_cg_ref.clinic_gesture_id
        ]
        if not ( ( len(number_of_same_cg_in_appointment) - 1 ) % 
                                mat_cg_ref.enter_in_various_gestures ):
            return True
        else:
            return False

    patient, appointment = checks.get_patient_appointment(
                                                appointment_id=appointment_id)
    clinic_gesture = ( meta.session.query(act.ClinicGesture)
                        .filter(act.ClinicGesture.id == clinic_gesture_id )
                        .one()
    )
    ##
    ## Create new clinic_report entry
    values = {
        'appointment_id': appointment_id,
        'clinic_gesture_id': clinic_gesture_id,
        'anatomic_location': int(anatomic_location),
        'duration': clinic_gesture.duration,
    }
    new_clinic_report = act.ClinicReport(**values)
    meta.session.add(new_clinic_report)
    # or: appointment.clinic_reports.append(new_clinic_report)
    try:
        meta.session.commit()
    except sqlalchemy.exc.IntegrityError:
        meta.session.rollback()

    appointment.clinic_reports.reorder()
    meta.session.commit()
    
    ##
    ## Update Material and MaterioVigilance
    for mat_cg_ref in new_clinic_report.clinic_gesture.materials:
        
        material_used = cost.get_material_used(mat_cg_ref.id)
        
        if ( _needs_redondance(appointment, material_used, mat_cg_ref)
            and material_used ):

            materio_vigilance = add_to_materio_vigilance(appointment_id, 
                                    mat_cg_ref.mean_quantity, material_used)
            new_clinic_report.materio_vigilance.append(materio_vigilance)
            meta.session.commit()
    
    ##
    ## Create event 
    if clinic_gesture.event_model_id:
        event_model = ( meta.session.query(model_teeth.EventModel)
            .filter(model_teeth.EventModel.id == clinic_gesture.event_model_id )
            .one()
        )
        tooth = teeth.get_patient_tooth(appointment.patient_id, 
                                                    int(anatomic_location))
        tooth.state = event_model.tooth_state
        tooth.surveillance = event_model.surveillance
        values = {
            'appointment_id': appointment_id,
            'tooth_id': tooth.id,
            'location': event_model.location,
            'state': event_model.state,
            'description': event_model.description,
            'comment': event_model.comment,
            'color': event_model.color,
        }
        if event_model.location == constants.TOOTH_EVENT_LOCATION_PERIODONTAL :
            pass
        elif event_model.location == constants.TOOTH_EVENT_LOCATION_TOOTH:
            pass
        elif event_model.location == constants.TOOTH_EVENT_LOCATION_CROWN:
            new_crown_event = model_teeth.CrownEvent(**values)
            meta.session.add(new_crown_event)
            meta.session.commit()
            for att in [ 'state', 'is_occlusal', 'is_buccal', 'is_lingual',
                    'is_mesial', 'is_distal', 'tooth_shade' ] :
                setattr(new_crown_event, att, getattr(event_model, att))
        elif event_model.location == constants.TOOTH_EVENT_LOCATION_ROOT:
            new_root_event = model_teeth.RootCanalEvent(**values)
            meta.session.add(new_root_event)
            meta.session.commit()
            for att in [ 'state', 'is_central', 'is_buccal', 'is_lingual',
                'is_mesial', 'is_distal', 'is_mesio_buccal', 'is_disto_buccal',
                'is_mesio_lingual', 'is_disto_lingual', 'is_mesio_buccal_2' ] :
                setattr(new_root_event, att, getattr(event_model, att))
        meta.session.commit()
 
    return new_clinic_report

@app.route('/add_materio_vigilance_to_clinic_report'
            '?aid=<int:appointment_id>', methods=['POST'])
def add_materio_vigilance_to_clinic_report(appointment_id):
    patient, appointment = checks.get_patient_appointment(
                                    appointment_id=appointment_id)
    material_form = ChooseMaterialForReportForm(request.form)
    
    materials_for_materio_vigilance = (
        meta.session.query(assets.Material)
            .filter(
                assets.Material.end_of_use.is_(None),
                assets.Material.end_use_reason ==
                                    constants.END_USE_REASON_IN_USE_STOCK,
                assets.Material.start_of_use.isnot(None),
                ~assets.Material.id.in_(
                    meta.session.query(
                        traceability.MaterioVigilance.material_id)
                        .filter(traceability.MaterioVigilance.appointment_id ==
                                                                appointment.id
                    )
                )
            )
            .join(assets.MaterialCategory, act.Specialty)
            .order_by(
                act.Specialty.name,
                assets.MaterialCategory.commercial_name,
                assets.MaterialCategory.brand )
            .all()
    )
    material_form.material_id.choices = [ 
        ( material.id, material.asset_category.commercial_name + " " +
                        material.asset_category.brand ) for material in
                        materials_for_materio_vigilance 
    ]

    if material_form.validate():
        material = ( meta.session.query(assets.Material)
                        .get(material_form.material_id.data) 
        )
        materio_vigilance = add_to_materio_vigilance(appointment_id, 
                                material.asset_category.automatic_decrease, 
                                                                    material)

    return redirect(url_for('view_clinic_report', 
                                            appointment_id=appointment_id))
                

@app.route('/add/cg_to_cr?aid=<int:appointment_id>', methods=['POST'])
def add_clinic_gesture_to_clinic_report(appointment_id):
    form = ChooseClinicGestureForReportForm(request.form)
    form.clinic_gesture_id.choices = [
        ( cg.id, cg.specialty.name[0:3] + " " + cg.name ) for cg in
            meta.session.query(act.ClinicGesture)
                .filter(act.ClinicGesture.before_first_patient.is_(False),
                        act.ClinicGesture.after_last_patient.is_(False),
                        act.ClinicGesture.before_each_appointment.is_(False),
                        act.ClinicGesture.after_each_appointment.is_(False)
                )
                .join(act.Specialty)
                .order_by(act.Specialty.name,
                            act.ClinicGesture.name )
                .all()
    ]
    if form.validate():
        if not form.anatomic_location.data:
            form.anatomic_location.data = 0
        try:
            if int(form.anatomic_location.data) >= 0 : 
                add_cg_to_cr(appointment_id, form.clinic_gesture_id.data,
                                                form.anatomic_location.data)
        except ValueError:
            for anatomic_location in\
                            teeth.get_teeth_list(form.anatomic_location.data) :
                add_cg_to_cr(appointment_id, form.clinic_gesture_id.data,
                                                        anatomic_location)
        
    return redirect(url_for('view_clinic_report', 
                                            appointment_id=appointment_id))


def remove_from_materio_vigilance(clinic_report):
    """ 
        update both:
            materio_vigilance.quantity_used and material.actual_quantity
    """
    def _leave_for_other_cg_in_cr(appointment, mat_cg_ref, 
                                                number_of_cg_in_appointment):
        if ( mat_cg_ref.enter_in_various_gestures > 1
            and ( number_of_cg_in_appointment % 
                        mat_cg_ref.enter_in_various_gestures ) == 1 ):
            return False
        else:
            return True

    def _get_material_quantity(cr, cr_mv):
        material_used_in_cr = [
            mat_cg_ref for mat_cg_ref in 
            cr.clinic_gesture.materials
                if mat_cg_ref.material_category_id == 
                    cr_mv.material.asset_category.id
        ]
        quantity_material_used = 0
        for mat_cg_ref in material_used_in_cr:
            quantity_material_used = (
                quantity_material_used + mat_cg_ref.mean_quantity
            )
        return quantity_material_used
      
    for cr_mv in clinic_report.materio_vigilance:

        mean_quantity_mat_cr = _get_material_quantity(clinic_report, cr_mv)
        
        # get the quantity of the material used by other cg in the 
        # appointment_clinic_report.
        mean_quantity_material_appointment = 0
        for cr in clinic_report.appointment.clinic_reports:
            for materio_vigilance in cr.materio_vigilance:
                if materio_vigilance.material_id == cr_mv.material_id:
                    mean_quantity_material_appointment = (
                        mean_quantity_material_appointment +
                        _get_material_quantity(cr, materio_vigilance)
                    )
        if mean_quantity_material_appointment:  
            percent_mat_used_by_this_cr = Decimal(
                mean_quantity_mat_cr / mean_quantity_material_appointment
            )
        if len(cr_mv.clinic_reports) > 1:
            if not any([ mat_cg_ref for mat_cg_ref in 
                                    clinic_report.clinic_gesture.materials ]):
                raise Exception('odontux_exception_12345')

            mat_cg_ref = ( meta.session.query(
                assets.MaterialCategoryClinicGestureReference)
                .filter(
                assets.MaterialCategoryClinicGestureReference.material_category_id ==
                                            cr_mv.material.asset_category.id,
                assets.MaterialCategoryClinicGestureReference.clinic_gesture_id == 
                                            clinic_report.clinic_gesture_id )
                .one()
            )
            if ( mat_cg_ref.enter_in_various_gestures > 1
                and len(
                    [ cr for cr in clinic_report.appointment.clinic_reports
                        if cr.clinic_gesture_id == mat_cg_ref.clinic_gesture_id
                    ] ) %   mat_cg_ref.enter_in_various_gestures == 1 
                or mat_cg_ref.enter_in_various_gestures == 1 ):

                cr_mv.material.actual_quantity = round(Decimal( 
                    cr_mv.material.actual_quantity + 
                        percent_mat_used_by_this_cr * cr_mv.quantity_used
                ), 2)

                cr_mv.quantity_used = round(Decimal(
                    cr_mv.quantity_used -
                    percent_mat_used_by_this_cr * cr_mv.quantity_used
                ), 2)
                   
                meta.session.commit()
        
        # Case material in materio vigilance is only associated with 
        # clinic_report we're about to delete, we delete materio_vigilance 
        # entry and adapt material.actual_quantity.
        else:
            cr_mv.material.actual_quantity = (
                cr_mv.material.actual_quantity + cr_mv.quantity_used
            )
            meta.session.delete(cr_mv)
            meta.session.commit()

    return True 

@app.route('/remove/cg_from_cr?crid=<int:clinic_report_id>')
def remove_cg_from_cr(clinic_report_id):
    clinic_report = ( meta.session.query(act.ClinicReport)
                        .filter(act.ClinicReport.id == clinic_report_id)
                        .one_or_none()
    )
    appointment = (meta.session.query(schedule.Appointment)
            .filter(schedule.Appointment.id == clinic_report.appointment_id)
            .one()
    )
    remove_from_materio_vigilance(clinic_report)

    meta.session.delete(clinic_report)
    try:
        meta.session.commit()
        appointment.clinic_reports.reorder()
        meta.session.commit()
    except sqlalchemy.exc.InvalidRequestError:
        meta.session.rollback()
    return redirect(url_for('view_clinic_report', 
                                                appointment_id=appointment.id))

