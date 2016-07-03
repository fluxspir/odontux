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
from base64 import b64encode
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
from odontux.pdfhandler import make_quote

#from odontux.pdfhandler import ( )

class QuoteGestureForm(Form):
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

class QuotePropositionForm(Form):
    healthcare_plan_id = SelectField(_('HealthCare Plan'), coerce=int)
    validity = IntegerField(_('Validity in months'), [validators.Required()],
                                        render_kw={'size':'4'})
    treatment_duration = IntegerField(_('Treatment duration'), 
                                                    [validators.Optional()])
    duration_unity = SelectField(_('Duration in'),
                choices=[ ( 'month', _('Months')), ('week', _('Weeks')), 
                            ('day', _('Days')) ] )
    proposition = FieldList(FormField(QuoteGestureForm), min_entries=1)
    remove_last = SubmitField(_('Remove last gesture'))
    add_proposition = SubmitField(_('Make another proposition'))
    preview = SubmitField(_('Preview'))
    save_print = SubmitField(_('Save and Print'))


@app.route('/find_gesture/')
def find_gesture():
    gest_code = request.args.get('gesture', None)
    healthcare_plan_id = request.args.get('healthcare_plan_id', None)
    patient_id = int(request.args.get('patient_id', None))
    patient, appointment = checks.get_patient_appointment(
                                                        patient_id=patient_id)
    if gest_code:
        gest_code = gest_code.split(" ")
        words = u"%"
        for word in gest_code:
            words = words + u'{}%'.format(word)
        cotations = (
            meta.session.query(act.Cotation)
                .join(act.Gesture)
                .filter(act.Cotation.healthcare_plan_id == healthcare_plan_id)
                .filter(or_(
                    act.Gesture.alias.ilike(words),
                    act.Gesture.code.ilike(words),
                    act.Gesture.name.ilike(words)
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
            '&qid=<quotes_id>&qrm=<int:quote_to_remove>')
def remove_quote_proposition(patient_id, appointment_id, quotes_id,
                                                            quote_to_remove):
    quotes_id = quotes_id.split(",")
    quotes_id.remove(str(quote_to_remove))
    if quotes_id:
        quotes_id = ",".join(quotes_id)
        return redirect(url_for('create_quote_proposition',
                                    patient_id=patient_id, 
                                    appointment_id=appointment_id,
                                    quotes_id=quotes_id))
    else:
        return redirect(url_for('create_quote_proposition',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))

@app.route('/create_quote_proposition?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
@app.route('/create_quote_proposition?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&qid=<quotes_id>', 
                                                    methods=['GET', 'POST'])
def create_quote_proposition(patient_id, appointment_id, quotes_id=''):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
    if not quotes_id:
        quotes = ( 
            meta.session.query(statements.Quote)
                .filter(statements.Quote.appointment_id == appointment_id,
                        statements.Quote.file_id.is_(None) )
                .all()
        )
        for quote in quotes:
            if not quotes_id:
                quotes_id = str(quote.id)
                continue
            quotes_id = quotes_id + "," + str(quote.id)
    else:
        quotes = ( meta.session.query(statements.Quote)
                    .filter(statements.Quote.id.in_(
                            [ int(i) for i in quotes_id.split(",") ] ))
                    .all()
        )
    quote_form = QuotePropositionForm(request.form)
    quote_form.healthcare_plan_id.choices = [ (hcp.id, hcp.name) for hcp in
        meta.session.query(act.HealthCarePlan)
        .filter(act.HealthCarePlan.id.in_(patient.healthcare_plans_id))
        .all() ]
    quote_gesture_form = QuoteGestureForm(request.form)

    if request.method == 'POST':
        if ( 'proposition-0-add_gesture' in request.form
                                            and quote_form.validate() ):
            quote_gesture_form.cotation_id =\
                                quote_form.proposition[0].cotation_id.data
            quote_gesture_form.anatomic_location =\
                        quote_form.proposition[0].anatomic_location.data
            quote_gesture_form.gesture_code =\
                                quote_form.proposition[0].gesture_code.data
            quote_gesture_form.gesture_name =\
                                quote_form.proposition[0].gesture_name.data
            quote_gesture_form.price =\
                                quote_form.proposition[0].price.data
            quote_gesture_form.appointment_number =\
                        quote_form.proposition[0].appointment_number.data
            quote_form.proposition.append_entry(quote_gesture_form)
           
        elif 'remove_last' in request.form:
            quote_form.proposition.pop_entry()

        elif 'add_proposition' in request.form:
            if ( len(quote_form.proposition.entries) == 0 or
                len(quote_form.proposition.entries) == 1 and
                not quote_form.proposition.entries[0].gesture_code.data ):
                return redirect(url_for('create_quote_proposition',
                                            patient_id=patient_id,
                                            appointment_id=appointment_id,
                                            quotes_id=quotes_id))

            # create new proposition of quote
            if quote_form.treatment_duration.data:
                if quote_form.duration_unity.data == 'month':
                    treatment_duration =quote_form.treatment_duration.data * 30
                elif quote_form.duration_unity.data == 'week':
                    treatment_duration = quote_form.treatment_duration.data * 7
                else:
                    treatment_duration = quote_form.treatment_duration.data
                treatment_duration =datetime.timedelta(days=treatment_duration)
            else:
                treatment_duration = None
            values = {
                'patient_id': patient_id,
                'dentist_id': appointment.dentist_id,
                'appointment_id': appointment_id,
                'type': constants.FILE_QUOTE,
                'validity': appointment.agenda.starttime +\
                datetime.timedelta(days=quote_form.validity.data * 30),
                'treatment_duration': treatment_duration,
            }
            new_proposition_quote = statements.Quote(**values)
            meta.session.add(new_proposition_quote)
            meta.session.commit()
            # insert gesture in this proposition of quote
            while quote_form.proposition.entries:
                entry = quote_form.proposition.pop_entry().data
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
                    'quote_id': new_proposition_quote.id,
                    'cotation_id': entry['cotation_id'],
                    'gesture_id': gesture.id,
                    'anatomic_location': entry['anatomic_location'],
                    'price': entry['price'],
                    'appointment_number': entry['appointment_number'],
                }
                new_gesture_in_proposition =\
                        statements.QuoteGestureReference(**gesture_entry)
                meta.session.add(new_gesture_in_proposition)
                meta.session.commit()
            
            if not quotes_id:
                quotes_id = str(new_proposition_quote.id)
            else:
                quotes_id = quotes_id + "," +\
                                            str(new_proposition_quote.id)
            # We reload the create_quote_proposition to enter in a new GET
            return redirect(url_for('create_quote_proposition',
                                            patient_id=patient_id,
                                            appointment_id=appointment_id,
                                            quotes_id=quotes_id))
        
        elif 'preview' in request.form:
            pdf_out = make_quote(patient_id, appointment_id, quotes)
            response = make_response(pdf_out)
            response.mimetype = 'application/pdf'
            return response
           
        elif 'save_print' in request.form:
            pdf_out = make_quote(patient_id, appointment_id, quotes)
            response = make_response(pdf_out)
            response.mimetype = 'application/pdf'
            filename = md5.new(pdf_out).hexdigest()
            with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
                f.write(pdf_out)

            file_values = {
                'md5': filename,
                'file_type': constants.FILE_QUOTE,
                'mimetype': 'application/pdf',
            }
            file_in_db = ( meta.session.query(documents.Files)
                .filter(documents.Files.md5 == filename)
                .one_or_none()
            )

            new_file = documents.Files(**file_values)
            meta.session.add(new_file)
            meta.session.commit()
            
            for quote in quotes:
                quote.file_id = new_file.id
            meta.session.commit()

            return response
        
        return render_template('create_quote_proposition.html', 
                                                patient=patient,
                                                appointment=appointment,
                                                quotes=quotes,
                                                quote_form=quote_form,
                                                quotes_id=quotes_id)

    quote_form.healthcare_plan_id.data = quote_form.healthcare_plan_id.data
    quote_form.validity.data = constants.QUOTE_VALIDITY
    
    if quotes:
        pdf_out = make_quote(patient_id, appointment_id, quotes)
        pdf_out = b64encode(pdf_out)
        return render_template('create_quote_proposition.html', 
                                                patient=patient,
                                                appointment=appointment,
                                                quotes=quotes,
                                                quote_form=quote_form,
                                                quotes_id=quotes_id,
                                                pdf_out=pdf_out)

    return render_template('create_quote_proposition.html', 
                                                patient=patient,
                                                appointment=appointment,
                                                quotes=quotes,
                                                quote_form=quote_form,
                                                quotes_id=quotes_id,
                                                pdf_out=None)


@app.route('/list_statement&pid=<int:patient_id>&aid=<int:appointment_id>')
def list_statement(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    quotes = ( meta.session.query(statements.Quote)
            .filter(statements.Quote.patient_id == patient_id)
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
                                        quotes_id='',
                                        quotes=quotes,
                                        bills=bills)

@app.route('/add_bill?pid=<int:patient_id>&aid=<int:appointment_id>')
def add_bill(patient_id, appointment_id):
    pass

