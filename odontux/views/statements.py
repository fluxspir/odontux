# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/23
# v0.5
# licence BSD
#

import pdb
import datetime
import os
import md5
from flask import ( session, render_template, request, redirect, url_for, 
                    abort, make_response, jsonify)

from wtforms import (Form, TextField, TextAreaField, DecimalField, 
                    IntegerField,HiddenField, DateField, SubmitField, 
                    FieldList, FormField, SelectField,
                    validators )
#from forms import TimeField
from sqlalchemy import or_
from sqlalchemy.orm import with_polymorphic

from odontux.views.log import index
from odontux.models import meta, schedule, documents, statements, act
from odontux.odonweb import app
#from odontux.views import forms
from gettext import gettext as _

from odontux import constants, checks
from odontux.pdfhandler import make_quotation

#from odontux.pdfhandler import ( )

class QuotationGestureForm(Form):
    cotation_id = HiddenField(_('cotation_id'))
    anatomic_location = IntegerField(_('Anatomic location'), 
                                                    [validators.Optional()])
    gesture_code = HiddenField(_('Technical gesture code'), 
                                                    [validators.Required()])
    gesture_name = TextField(_('Technical gesture denomination'),
                                                    [validators.Required()])
    price = DecimalField(_('Price'), [validators.Optional()])
    appointment_number = IntegerField(_('Appointment number'), 
                                                    [validators.Optional()])
    add_gesture = SubmitField(_('Add gesture'))

class QuotationPropositionForm(Form):
    healthcare_plan_id = SelectField(_('HealthCare Plan'), coerce=int)
    validity = IntegerField(_('Validity in months'), [validators.Required()],
                                        render_kw={'size': 4})
    treatment_duration = IntegerField(_('Treatment duration'), 
                                                    [validators.Optional()])
    duration_unity = SelectField(_('Duration in'),
                choices=[ ( 'month', _('Months')), ('week', _('Weeks')), 
                            ('day', _('Days')) ] )
    proposition = FieldList(FormField(QuotationGestureForm), min_entries=1)
    remove_last = SubmitField(_('Remove last gesture'))
    add_proposition = SubmitField(_('Make another proposition'))
    preview = SubmitField(_('Preview'))
    save_and_print = SubmitField(_('Save and Print'))
#    add_proposition = SubmitField(_('Add proposition'))

#class QuotationForm(Form):
#    quotation = FieldList(FormField(QuotationProjectForm), min_entries=1)
#    validity = IntegerField(_('Validity in months'), [validators.Required()],
#                                        render_kw={'size': 4})
#    preview = SubmitField(_('Preview'))
#    submit_quotation = SubmitField(_('Save and print'))
#
@app.route('/find_gesture/')
def find_gesture():
    gest_code = request.args.get('gesture', None)
    healthcare_plan_id = request.args.get('healthcare_plan_id', None)
    patient_id = int(request.args.get('patient_id', None))
    patient = checks.get_patient(patient_id)
    if gest_code:
        gest_code = u'%{}%'.format(gest_code)
        cotations = (
            meta.session.query(act.Cotation)
                .join(act.Gesture)
                .filter(act.Cotation.healthcare_plan_id == healthcare_plan_id)
                .filter(or_(
                    act.Gesture.alias.ilike(gest_code),
                    act.Gesture.code.ilike(gest_code),
                    act.Gesture.name.ilike(gest_code)
                    )
                )
                .all()
        )
        
        if not cotations:
            return jsonify(success=False)

        gestures = {}
        for cotation in cotations:
            gestures[str(cotation.id)] = (cotation.gesture.name,
                                            cotation.gesture.code,
                                            str(cotation.price))
        return jsonify(success=True, **gestures)

    return jsonify(success=False)

@app.route('/remove_proposition?pid=<int:patient_id>&aid=<int:appointment_id>'
            '&qid=<quotations_id>&qrm=<int:quotation_to_remove>')
def remove_quotation_proposition(patient_id, appointment_id, quotations_id,
                                                        quotation_to_remove):
    quotations_id = quotations_id.split(",")
    quotations_id.remove(str(quotation_to_remove))
    if quotations_id:
        quotations_id = ",".join(quotations_id)
        return redirect(url_for('create_quotation_proposition',
                                    patient_id=patient_id, 
                                    appointment_id=appointment_id,
                                    quotations_id=quotations_id))
    else:
        return redirect(url_for('create_quotation_proposition',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))

@app.route('/create_quotation_proposition?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
@app.route('/create_quotation_proposition?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&qid=<quotations_id>', 
                                                    methods=['GET', 'POST'])
def create_quotation_proposition(patient_id, appointment_id, quotations_id=''):

#    def _make_healthcare_plan_id_choices(quotation_form):
#        for quote_form in quotation_form.quotation:
#            quote_form.healthcare_plan_id.choices = [ (hcp.id, hcp.name) 
#                for hcp in meta.session.query(act.HealthCarePlan)
#                .filter(act.HealthCarePlan.id.in_(patient.healthcare_plans_id))
#                .all()
#        ]
#        return quotation_form
# 
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    if not quotations_id:
        quotations = ( 
            meta.session.query(statements.Quotation)
                .filter(statements.Quotation.appointment_id == appointment_id,
                        statements.Quotation.file_id.is_(None) )
                .all()
        )
        for quotation in quotations:
            if not quotations_id:
                quotations_id = str(quotation.id)
                continue
            quotations_id = quotations_id + "," + str(quotation.id)
    else:
        quotations = ( meta.session.query(statements.Quotation)
                    .filter(statements.Quotation.id.in_(
                            [ int(i) for i in quotations_id.split(",") ] ))
                    .all()
        )
    quotation_form = QuotationPropositionForm(request.form)
    quotation_form.healthcare_plan_id.choices = [ (hcp.id, hcp.name) for hcp in
        meta.session.query(act.HealthCarePlan)
        .filter(act.HealthCarePlan.id.in_(patient.healthcare_plans_id))
        .all() ]
    quotation_gesture_form = QuotationGestureForm(request.form)

    if request.method == 'POST':
        if ( 'proposition-0-add_gesture' in request.form
                                            and quotation_form.validate() ):
            quotation_gesture_form.cotation_id =\
                                quotation_form.proposition[0].cotation_id.data
            quotation_gesture_form.anatomic_location =\
                        quotation_form.proposition[0].anatomic_location.data
            quotation_gesture_form.gesture_code =\
                                quotation_form.proposition[0].gesture_code.data
            quotation_gesture_form.gesture_name =\
                                quotation_form.proposition[0].gesture_name.data
            quotation_gesture_form.price =\
                                quotation_form.proposition[0].price.data
            quotation_gesture_form.appointment_number =\
                        quotation_form.proposition[0].appointment_number.data
            quotation_form.proposition.append_entry(quotation_gesture_form)
           
        elif 'remove_last' in request.form:
            quotation_form.proposition.pop_entry()

        elif 'add_proposition' in request.form:
            if ( len(quotation_form.proposition.entries) == 0 or
                len(quotation_form.proposition.entries) == 1 and
                not quotation_form.proposition.entries[0].gesture_code.data ):
                return redirect(url_for('create_quotation_proposition',
                                            patient_id=patient_id,
                                            appointment_id=appointment_id,
                                            quotations_id=quotations_id))

            # create new proposition of quotation
            if quotation_form.treatment_duration.data:
                if quotation_form.duration_unity.data == 'month':
                    treatment_duration =\
                                    quotation_form.treatment_duration.data * 30
                elif quotation_form.duration_unity.data == 'week':
                    treatment_duration =\
                                    quotation_form.treatment_duration.data * 7
                else:
                    treatment_duration =\
                                    quotation_form.treatment_duration.data
                treatment_duration =\
                                    datetime.timedelta(days=treatment_duration)
            else:
                treatment_duration = None
            values = {
                'patient_id': patient_id,
                'dentist_id': appointment.dentist_id,
                'appointment_id': appointment_id,
                'type': constants.FILE_QUOTATION,
                'validity': appointment.agenda.starttime +\
                datetime.timedelta(days=quotation_form.validity.data * 30),
                'treatment_duration': treatment_duration,
            }
            new_proposition_quotation = statements.Quotation(**values)
            meta.session.add(new_proposition_quotation)
            meta.session.commit()
            # insert gesture in this proposition of quotation
            while quotation_form.proposition.entries:
                entry = quotation_form.proposition.pop_entry().data
                if not entry['cotation_id']:
                    continue
                gesture = ( meta.session.query(act.Gesture)
                    .filter(act.Gesture.code == entry['gesture_code'],
                            act.Gesture.cotations.any(
                                act.Cotation.id == entry['cotation_id'])
                    )
                    .one_or_none()
                )
                if not gesture:
                    continue
                gesture_entry = {
                    'quotation_id': new_proposition_quotation.id,
                    'cotation_id': entry['cotation_id'],
                    'gesture_id': gesture.id,
                    'anatomic_location': entry['anatomic_location'],
                    'price': entry['price'],
                    'appointment_number': entry['appointment_number'],
                }
                new_gesture_in_proposition =\
                        statements.QuotationGestureReference(**gesture_entry)
                meta.session.add(new_gesture_in_proposition)
                meta.session.commit()
            
            if not quotations_id:
                quotations_id = str(new_proposition_quotation.id)
            else:
                quotations_id = quotations_id + "," +\
                                            str(new_proposition_quotation.id)
            # We reload the create_quotation_proposition to enter in a new GET
            return redirect(url_for('create_quotation_proposition',
                                            patient_id=patient_id,
                                            appointment_id=appointment_id,
                                            quotations_id=quotations_id))
        
        elif 'preview' in request.form:
            pdf_out = make_quotation(patient_id, appointment_id, quotations)
            response = make_response(pdf_out)
            response.mimetype = 'application/pdf'
            return response
            
#        elif 'quotation-0-add_project' in request.form:
#            quotation_project_form.healthcare_plan_id.choices = [ 
#                (hcp.id, hcp.name) for hcp in 
#                    meta.session.query(act.HealthCarePlan)
#                        .filter(act.HealthCarePlan.id.in_(
#                                                patient.healthcare_plans_id))
#                        .all() 
#            ]
#            quotation_project_form.healthcare_plan_id =\
#                quotation_form.quotation[0].healthcare_plan_id.data
#            new_quotation_project_form = QuotationProjectForm(request.form)
#            while quotation_form.quotation[0].project.entries:
#                entry = quotation_form.quotation[0].project.pop_entry
#                pdb.set_trace()
#            quotation_project_form.project =\
#                                            quotation_form.quotation[0].project
#
#            quotation_form.quotation.append_entry(quotation_project_form)
#            
#            while quotation_form.quotation[0].project.entries:
#                quotation_form.quotation[0].project.pop_entry()
#            
#            quotation_form.quotation[0].project.append_entry(
#                                                        quotation_gesture_form)
#
#            quotation_form = _make_healthcare_plan_id_choices(quotation_form)
#        
        return render_template('create_quotation_proposition.html', 
                                                patient=patient,
                                                appointment=appointment,
                                                quotations=quotations,
                                                quotation_form=quotation_form,
                                                quotations_id=quotations_id)
    
    quotation_form.healthcare_plan_id.data =\
                                        quotation_form.healthcare_plan_id.data
    quotation_form.validity.data = 6
    return render_template('create_quotation_proposition.html', 
                                                patient=patient,
                                                appointment=appointment,
                                                quotations=quotations,
                                                quotation_form=quotation_form,
                                                quotations_id=quotations_id)


@app.route('/list_statement&pid=<int:patient_id>&aid=<int:appointment_id>')
def list_statement(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    
    quotations = ( meta.session.query(statements.Quotation)
            .filter(statements.Quotation.patient_id == patient_id)
            .join(schedule.Appointment, schedule.Agenda)
            .order_by(schedule.Agenda.starttime.desc())
            .all()
    )
    bills = ( meta.session.query(statements.Bill)
            .filter(statements.Bill.patient_id == patient_id)
            .join(schedule.Appointment, schedule.Agenda)
            .order_by(schedule.Agenda.starttime.desc())
            .all()
    )

    return render_template('list_statements.html', patient=patient,
                                        appointment=appointment,
                                        quotations_id='',
                                        quotations=quotations,
                                        bills=bills)

@app.route('/add_bill?pid=<int:patient_id>&aid=<int:appointment_id>')
def add_bill(patient_id, appointment_id):
    pass

