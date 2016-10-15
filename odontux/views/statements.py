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
import magic

from base64 import b64encode
from flask import ( session, render_template, request, redirect, url_for, 
                    abort, make_response, jsonify, send_from_directory)

from wtforms import (Form, TextField, TextAreaField, DecimalField, 
                    IntegerField, HiddenField, DateField, SubmitField, 
                    FieldList, FormField, SelectField, FileField,
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
from documents import insert_document_in_db
from odontux.pdfhandler import make_quote, make_invoice_payment_bill

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

class GestureForm(Form):
    gesture_id = HiddenField(_('gesture_id'))
    date = HiddenField(_('date'))
    gesture_name = TextAreaField(_('Gesture description'), 
                                            render_kw={'row':2,'cols':60})
    anatomic_location = HiddenField(_('anat_loc'))
    price = HiddenField(_('price'))

class BillForm(Form):
    gestures = FieldList(FormField(GestureForm), min_entries=1)
    update = SubmitField(_('Update'))
    preview = SubmitField(_('Preview'))
    save_print = SubmitField(_('Save and Print'))

if constants.LOCALE == 'br':
    class NotaFiscalForm(Form):
        document = FileField(_('Document'))
        document_type = SelectField(_('Type'), coerce=int,
            choices=[ ( nfe[0], nfe[1] ) for nfe in 
                        constants.NOTAS_FISCAIS.items() ] )
        add_file = SubmitField(_('Add document'))

@app.route('/choose/gestures_in_bill?pid=<int:patient_id>'
                                                '&aid=<int:appointment_id>')
@app.route('/choose/gestures_in_bill?pid=<int:patient_id>'
                        '&aid=<int:appointment_id>&gids=<gestures_id_in_bill>')
def choose_gestures_in_bill(patient_id, appointment_id, 
                                                    gestures_id_in_bill=""):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    patient_appointments_id = [ a.id for a in patient.appointments ]
    # get id list of gestures that could be in bill
    gestures_panel = (
        meta.session.query(act.AppointmentCotationReference)
            .join(schedule.Appointment, schedule.Agenda)
            .filter(
                act.AppointmentCotationReference.appointment_id.in_(
                                                    patient_appointments_id),
                act.AppointmentCotationReference.is_paid.is_(True),
                ~act.AppointmentCotationReference.id.in_(
                    meta.session.query(
            statements.BillAppointmentCotationReference.appointment_cotation_id)
                ),
                schedule.Agenda.starttime <= appointment.agenda.starttime
            )
            .order_by(schedule.Agenda.starttime)
            .all()
    )
    gestures_id_panel = [ gesture.id for gesture in gestures_panel ]

    # get id list of gestures that are to be in bill
    if not gestures_id_in_bill:
        gestures_id_in_bill = [ gesture.id for gesture in gestures_panel ]
    else:
        gestures_id_in_bill = [ int(i) for i in gestures_id_in_bill.split(",") ]

    gestures_in_bill = (
        meta.session.query(act.AppointmentCotationReference)
            .filter(
                act.AppointmentCotationReference.id.in_(gestures_id_in_bill))
            .join(schedule.Appointment, schedule.Agenda)
            .order_by(schedule.Agenda.starttime)
            .all()
    )

    # get id list of gestures that won't be in bill
    gestures_not_in_bill = (
        meta.session.query(act.AppointmentCotationReference)
            .filter(
                act.AppointmentCotationReference.id.in_(gestures_id_panel),
                ~act.AppointmentCotationReference.id.in_(gestures_id_in_bill)
            )
            .all()
    )
    
    gestures_id_in_bill = ",".join( [ str(gest.id) 
                                            for gest in gestures_in_bill ] )
    return render_template('choose_gestures_in_bill.html',
                                    patient=patient,
                                    appointment=appointment,
                                    constants=constants,
                                    gestures_in_bill=gestures_in_bill,
                                    gestures_not_in_bill=gestures_not_in_bill,
                                    gestures_id_in_bill=gestures_id_in_bill)

@app.route('/add/gesture_to_bill?pid=<int:patient_id>&aid=<int:appointment_id>'
            '&gid=<gesture_id_to_add>&gib=<gestures_id_in_bill>')
def add_gesture_to_bill(patient_id, appointment_id, gesture_id_to_add,
                                                        gestures_id_in_bill):

    gestures_id_in_bill = gestures_id_in_bill + "," + gesture_id_to_add
    return redirect(url_for('choose_gestures_in_bill', patient_id=patient_id,
                                    appointment_id=appointment_id,
                                    gestures_id_in_bill=gestures_id_in_bill))

@app.route('/remove/gesture_from_bill?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&gid=<gesture_id_to_remove>'
            '&gib=<gestures_id_in_bill>')
def remove_gesture_from_bill(patient_id, appointment_id, gesture_id_to_remove,
                                                        gestures_id_in_bill):
    gestures_id_in_bill = gestures_id_in_bill.split(",")
    gestures_id_in_bill.remove(gesture_id_to_remove)
    gestures_id_in_bill = ",".join( [ gid for gid in gestures_id_in_bill ] )
    if not gestures_id_in_bill:
        return redirect(url_for('choose_gestures_in_bill', 
                                                        patient_id=patient_id,
                                                appointment_id=appointment_id))
        
    return redirect(url_for('choose_gestures_in_bill', patient_id=patient_id,
                                    appointment_id=appointment_id,
                                    gestures_id_in_bill=gestures_id_in_bill))

@app.route('/make_bill?pid=<int:patient_id>&aid=<int:appointment_id>'
                        '&gib=<gestures_id_in_bill>', methods=['GET', 'POST'])
def make_bill(patient_id, appointment_id, gestures_id_in_bill):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    gestures_in_bill = ( 
        meta.session.query(act.AppointmentCotationReference)
        .filter(act.AppointmentCotationReference.id.in_( 
                [ int(gid) for gid in gestures_id_in_bill.split(",") ] ) )
        .all()
    )
    bill_form = BillForm(request.form)

    if request.method == 'GET':
        for gesture in gestures_in_bill:
            gesture_form = GestureForm(request.form)
            gesture_form.gesture_id = gesture.id
            gesture_form.gesture_name = gesture.gesture.name
            gesture_form.date =\
                        gesture.appointment.agenda.starttime.date().isoformat()
            gesture_form.anatomic_location = gesture.anatomic_location
            gesture_form.price = gesture.price
            bill_form.gestures.append_entry(gesture_form)

    pdf_out = make_invoice_payment_bill(patient_id, 
                                        gestures_in_bill[-1].appointment_id,
                                        bill_form)
 
    if request.method == 'POST' and bill_form.validate():
        if 'update' in request.form:
            return render_template('make_bill.html', patient=patient,
                                    appointment=appointment,
                                    constants=constants,
                                    bill_form=bill_form,
                                    gestures_id_in_bill=gestures_id_in_bill,
                                    pdf_out=b64encode(pdf_out))
        elif 'preview' in request.form:
            response = make_response(pdf_out)
            response.mimetype = 'application/pdf'
            return response

        elif 'save_print' in request.form:
            response = make_response(pdf_out)
            response.mimetype = 'application/pdf'
            filename = md5.new(pdf_out).hexdigest()

            with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
                f.write(pdf_out)

            file_values = {
                'md5': filename,
                'file_type': constants.FILE_BILL,
                'mimetype': 'application/pdf',
            }
            new_file = documents.Files(**file_values)
            meta.session.add(new_file)
            meta.session.commit()

            bill_values = {
                'patient_id': patient_id,
                'appointment_id': gestures_in_bill[-1].appointment_id,
                'dentist_id': appointment.dentist_id,
                'type': constants.FILE_BILL,
                'file_id': new_file.id,
            }
            new_bill = statements.Bill(**bill_values)
            meta.session.add(new_bill)
            meta.session.commit()

            for gesture in bill_form.gestures:
                values = {
                    'bill_id': new_bill.id,
                    'appointment_cotation_id': int(gesture.gesture_id.data),
                }
                new_gesture =\
                    statements.BillAppointmentCotationReference(**values)
                meta.session.add(new_gesture)
                meta.session.commit()

            return response

    return render_template('make_bill.html', patient=patient,
                                    appointment=appointment,
                                    constants=constants,
                                    bill_form=bill_form,
                                    gestures_id_in_bill=gestures_id_in_bill)
#                                            pdf_out=b64encode(pdf_out))

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
    if constants.LOCALE == 'br':
        nfes = (meta.session.query(statements.NotaFiscalBr)
            .filter(statements.NotaFiscalBr.patient_id == patient_id)
            .order_by(statements.NotaFiscalBr.timestamp.desc())
            .all()
        )
    else:
        nfes = []
    return render_template('list_statements.html', patient=patient,
                                        appointment=appointment,
                                        quotes_id='',
                                        quotes=quotes,
                                        bills=bills,
                                        nfes=nfes,
                                        constants=constants)

@app.route('/view/bill?bid=<int:bill_file_id>')
def view_bill(bill_file_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    bill_file = ( meta.session.query(documents.Files)
                    .filter(documents.Files.id == bill_file_id)
                    .one()
    )
    return send_from_directory(app.config['DOCUMENT_FOLDER'],
                                    bill_file.md5,
                                    mimetype=bill_file.mimetype)
 
@app.route('/view/quote?qid=<int:quote_file_id>')
def view_quote(quote_file_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    quote_file = ( meta.session.query(documents.Files)
                    .filter(documents.Files.id == quote_file_id)
                    .one()
    )
    return send_from_directory(app.config['DOCUMENT_FOLDER'],
                                    quote_file.md5,
                                    mimetype=quote_file.mimetype)

if constants.LOCALE == 'br':
    @app.route('/view/nota_fiscal&nfeid=<int:nfe_file_id>')
    def view_nota_fiscal(nfe_file_id):
        authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                            constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
        if session['role'] not in authorized_roles:
            return abort(403)
        
        nfe_file = ( meta.session.query(documents.Files)
                        .filter(documents.Files.id == nfe_file_id)
                        .one()
        )
        return send_from_directory(app.config['DOCUMENT_FOLDER'],
                                        nfe_file.md5,
                                        mimetype=nfe_file.mimetype)


    @app.route('/add/nota_fiscal?pid=<int:patient_id>', 
                                                    methods=['GET', 'POST'])
    @app.route('/add/nota_fiscal?pid=<int:patient_id>'
                '&aid=<int:appointment_id>', methods=['GET', 'POST'])
    def add_nota_fiscal(patient_id, appointment_id=0):
        authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
        if session['role'] not in authorized_roles:
            return abort(403)
        patient, appointment = checks.get_patient_appointment(patient_id,
                                                                appointment_id)
        
        document_form = NotaFiscalForm(request.form)
        if request.method == 'POST' and document_form.validate():
            document_data = request.files[document_form.document.name].read()
            if document_data:
                new_file = insert_document_in_db(document_data,
                                document_form.document_type.data, appointment)
                
                values = {
                    'patient_id': patient_id,
                    'document_id': new_file.id,
                }
                new_nota_fiscal = statements.NotaFiscalBr(**values)
                meta.session.add(new_nota_fiscal)
                meta.session.commit()

        return render_template('add_nota_fiscal.html', patient=patient,
                                            appointment=appointment,
                                            document_form=document_form)
        
