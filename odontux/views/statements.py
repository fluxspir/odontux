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

#from odontux.pdfhandler import ( )

class QuotationGestureForm(Form):
    cotation_id = HiddenField(_('cotation_id'))
    anatomic_location = IntegerField(_('Anatomic location'), 
                                                    [validators.Required()])
#    specialty = SelectField(_('Specialty', coerce=int)
#    gesture_id = SelectField(_('Technical Gesture'), coerce=int,
#                                            [validators.Required()])
    gesture_code = TextField(_('Technical gesture code'), 
                                                    [validators.Required()])
    price = DecimalField(_('Price'), [validators.Optional()])
    add_gesture = SubmitField(_('Add gesture'))

class QuotationProjectForm(Form):
    healthcare_plan_id = SelectField(_('HealthCare Plan'), coerce=int)#,
    project = FieldList(FormField(QuotationGestureForm), min_entries=1)
    add_project = SubmitField(_('Add project'))

class QuotationForm(Form):
    quotation = FieldList(FormField(QuotationProjectForm), min_entries=1)
    validity = IntegerField(_('Validity in months'), [validators.Required()],
                                        render_kw={'size': 4})
    preview = SubmitField(_('Preview'))
    submit_quotation = SubmitField(_('Save and print'))

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

@app.route('/create_quotation?pid=<int:patient_id>&aid=<int:appointment_id>',
                                                    methods=['GET', 'POST'])
def create_quotation(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    quotation_form = QuotationForm(request.form)
    for quote_form in quotation_form.quotation:
        quote_form.healthcare_plan_id.choices = [ (hcp.id, hcp.name) for hcp in
            meta.session.query(act.HealthCarePlan)
                .filter(act.HealthCarePlan.id.in_(patient.healthcare_plans_id))
                .all()
        ]
    
    quotation_form.validity.data = 6
    return render_template('create_quotation.html', patient=patient,
                                    appointment=appointment,
                                    quotation_form=quotation_form)


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
                                        quotations=quotations,
                                        bills=bills)

@app.route('/add_bill?pid=<int:patient_id>&aid=<int:appointment_id>')
def add_bill(patient_id, appointment_id):
    pass

