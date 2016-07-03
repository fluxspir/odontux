# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/29
# v0.5
# licence BSD
#

import pdb
import os
import datetime
import md5
from flask import ( session, render_template, request, redirect, url_for, 
                    make_response, abort ) 
import sqlalchemy
from sqlalchemy import or_
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import meta, compta, documents

from odontux.views.log import index

from odontux.pdfhandler import make_payment_receipt

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, IntegerField, validators,
                     FieldList, SubmitField)

class PaymentTypeForm(Form):
    id = HiddenField(_('id'))
    odontux_name = TextField(_('Odontux name'), [validators.Required()])
    gnucash_name = TextField(_('Gnucash name'), [validators.Required()])
    active = BooleanField(_('Active') )
    update = SubmitField(_('Update'))

class PatientPaymentForm(Form):
    patient_id = HiddenField(_('patient_id'))
    mean_id = SelectField(_("Payment's mean"), coerce=int)
    amount = DecimalField(_('Amount'), [validators.Required()])
    comments = TextAreaField(_('Comments'))
    make_payment = SubmitField(_('Make Payment'))

@app.route('/make/payment&pid=<int:patient_id>&aid=<int:appointment_id>', 
                                                    methods=['GET', 'POST'])
def make_payment(patient_id, appointment_id):
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    payment_form = PatientPaymentForm(request.form)
    payment_form.mean_id.choices = [ ( mean.id, mean.odontux_name ) for mean in
            meta.session.query(compta.PaymentType)
                .filter(compta.PaymentType.active.is_(True))
                .all() 
    ]
    
    if request.method == 'POST' and payment_form.validate():
        # get the gnucash mean_account_odontux_asset name
        mean = ( meta.session.query(compta.PaymentType)
            .filter(compta.PaymentType.id == payment_form.mean_id.data)
            .one()
        )
        pdf_out = make_payment_receipt(patient_id, appointment_id, 
                                            payment_form, mean.gnucash_name)
        if not pdf_out:
            return render_template('make_payment.html', patient=patient,
                                        appointment=appointment,
                                        payment_form=payment_form)
        filename = md5.new(pdf_out).hexdigest()
        with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
            f.write(pdf_out)
        file_values = {
            'md5': filename,
            'file_type': constants.FILE_RECEIPT,
            'mimetype': 'application/pdf'
        }
        new_file = ( meta.session.query(documents.Files)
            .filter(documents.Files.md5 == filename)
            .one_or_none()
        )
        if not new_file:
            new_file = documents.Files(**file_values)
            meta.session.add(new_file)
            meta.session.commit()

        receipt_values = {
            'patient_id': patient_id,
            'mean_id': payment_form.mean_id.data,
            'receipt_id': new_file.id,
            'amount': payment_form.amount.data,
            'comments': payment_form.comments.data,
            'cashin_date': datetime.date.today(),
        }
        new_payment = compta.Payment(**receipt_values)
        meta.session.add(new_payment)
        meta.session.commit()
        
        # Record payment in gnucash

        return redirect(url_for('list_acts', patient_id=patient_id,
                                            appointment_id=appointment_id))

    if request.method == 'GET':
        payment_form.amount.data = patient.due()

    payment_form.patient_id.data = patient.id
    return render_template('make_payment.html', patient=patient,
                                                appointment=appointment,
                                                payment_form=payment_form)

@app.route('/patient/payments/&pid=<int:patient_id>')
@app.route('/patient/payments/&pid=<int:patient_id>&aid=<int:appointment_id>')
def patient_payments(patient_id, appointment_id=0):
    
    patient = checks.get_patient(patient_id)
    if not appointment_id:
        appointment_id = patient.appointments[-1].id
    appointment = checks.get_appointment(appointment_id)
    payments = ( meta.session.query(compta.Payment)
                    .filter(compta.Payment.patient_id == patient_id)
                    .all()
    )
    return render_template('patient_payments.html', patient=patient,
                                                    appointment=appointment,
                                                    payments=payments)

@app.route('/show_payments_type&ptid=<int:payments_type_id>', 
                                                    methods=['GET', 'POST'])
def show_payments_type(payments_type_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    payment_type = ( meta.session.query(compta.PaymentType)
                        .filter(compta.PaymentType.id == payments_type_id)
                        .one()
    )
    payment_type_form = PaymentTypeForm(request.form)
    
    if request.method == 'POST' and payment_type_form.validate():
        payment_type.odontux_name = payment_type_form.odontux_name.data
        payment_type.gnucash_name = payment_type_form.gnucash_name.data
        payment_type.active = payment_type_form.active.data
        meta.session.commit()
        return redirect(url_for('show_payments_type',
                                            payments_type_id=payments_type_id))
    
    payment_type_form.odontux_name.data = payment_type.odontux_name
    payment_type_form.gnucash_name.data = payment_type.gnucash_name
    payment_type_form.active.data = payment_type.active
    return render_template('show_payments_type.html',
                                        payment_type=payment_type,
                                        payment_type_form=payment_type_form)

@app.route('/payments_type', methods=['GET', 'POST'])
def payments_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    payments_types = meta.session.query(compta.PaymentType).all()

    return render_template('payments_type.html', 
                                        payment_type_form=payment_type_form,
                                        payments_types=payments_types)

@app.route('/portal_comptability')
def portal_comptability():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)

    return render_template('portal_comptability.html')


