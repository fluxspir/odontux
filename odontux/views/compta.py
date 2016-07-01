# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/06/29
# v0.5
# licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for, jsonify
import sqlalchemy
from sqlalchemy import or_
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import ( meta, compta)

from odontux.views.log import index

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     DecimalField, HiddenField, IntegerField, validators,
                     FieldList, SubmitField)

class PaymentTypeForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('name'), [validators.Required()])
    alias = TextField(_('alias'))
    add = SubmitField(_('Add'))
    update = SubmitField(_('Update'))

class PatientPaymentForm(Form):
    payer_id = HiddenField(_('payer_id'))
    patient_id = HiddenField(_('patient_id'))
    mean_id = SelectField(_("Payment's mean"), coerce=int)
    amount = DecimalField(_('Amount'), [validators.Required()])
    comments = TextAreaField(_('Comments'))

@app.route('/make/payment&pid=<int:patient_id>')
def make_payment(patient_id):
    
    patient = checks.get_patient(patient_id)
    payment_form = PatientPaymentForm(request.form)
    payment_form.mean_id.choices = [ ( mean.id, mean.name ) for mean in
                                meta.session.query(compta.PaymentType).all() ]
    
    if request.method == 'POST' and payment_form.validate():
        pass

    if request.method == 'GET':
        pass
        
    return render_template('make_payment', patient=patient)

@app.route('/patient/payments/&pid=<int:patient_id>')
def patient_payments(patient_id):
    
    patient = checks.get_patient(patient_id)
    payments = ( meta.session.query(compta.Payment)
                    .filter(compta.Payment.patient_id == patient_id)
                    .all()
    )
    return render_template('patient_payments.html', patient=patient,
                                                    payments=payments)

@app.route('/show_payments_type&ptid=<int:payments_type_id>')
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
        payment_type.name = payment_type_form.name.data
        payment_type.alias = payment_type_form.alias.data
        meta.session.commit()
        return redirect(url_for('show_payments_type'),
                                            payments_type_id=payments_type_id)
    
    payment_type_form.name.data = payment_type.name
    payment_type_form.alias.data = payment_type.alias
    return render_template('show_payments_type.html',
                                        payment_type=payment_type,
                                        payment_type_form=payment_type_form)

@app.route('/payments_type', methods=['GET', 'POST'])
def payments_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    payment_type_form = PaymentTypeForm(request.form)
    if request.method == 'POST' and payment_type_form.validate():
        values = {
            'name': payment_type_form.name.data,
            'alias': payment_type_form.alias.data,
        }
        new_payment_type = compta.PaymentType(**values)
        meta.session.add(new_payment_type)
        meta.session.commit()
        return redirect(url_for('payments_type'))

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


