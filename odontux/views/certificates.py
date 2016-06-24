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
                    abort, make_response )

from wtforms import (Form, TextField, TextAreaField, DecimalField,
                     HiddenField, DateField, SubmitField,
                    validators )
from forms import TimeField
#from sqlalchemy.orm import with_polymorphic

from odontux.views.log import index
from odontux.models import meta, certificates, schedule, documents
from odontux.odonweb import app
#from odontux.views import forms
from gettext import gettext as _

from odontux import constants, checks

from odontux.pdfhandler import ( make_presence_certificate, 
                                    make_cessation_certificate
                            )

CERTIFICATE_FIRST_PART = u"Atesto, com o fim específico de dispensa de atividades trabalhistas (ou escolares, ou judiciárias), que "
CERTIFICATE_SECOND_PART = u", portador(a) do CPF "
CERTIFICATE_THIRD_PART = u" esteve sob meus cuidados profissionais no dia "
CESSATION_FOURTH_PART = u" devendo permanecer em repouso por "

class CertificateForm(Form):
    certificate_id = HiddenField(_('presence_id'))
    first_part = TextAreaField(_('first part'), [validators.Required()],
                                        render_kw={'cols': '150', 'rows': 1})
    second_part = TextAreaField(_('second part'), [validators.Required()],
                                        render_kw={'cols': '50', 'rows': 1})
    identity_number = TextField(_('identity'), [validators.Required()])
    third_part = TextAreaField(_('third part'), [validators.Required()],
                                            render_kw={'cols': 50, 'rows':1})
    day = DateField(_('day'), [validators.Required()], format='%Y-%m-%d')
    preview = SubmitField(_('Preview'))
    save_print = SubmitField(_('Save and Print'))

class PresenceForm(CertificateForm):
    starttime = TimeField(_('start time'), [validators.Required()])
    endtime = TimeField(_('end time'), [validators.Required()])

class CessationForm(CertificateForm):
    fourth_part = TextAreaField(_('fourth part'), [validators.Required()])
    days_number = DecimalField(_('Number of days of cessation'), 
                        [validators.Required()], render_kw={'size': 4})

@app.route('/portal/certificate?pid=<int:patient_id>'
            '&aid=<int:appointment_id>')
def portal_certificate(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return abort(403)

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    certifs = ( meta.session.query(certificates.Certificate)
                    .filter(certificates.Certificate.patient_id == patient_id)
    )
    presences = ( certifs
                .filter(certificates.Certificate.certif_type ==\
                                                    constants.FILE_PRESENCE)
                .join(schedule.Appointment, schedule.Agenda)
                .order_by(schedule.Agenda.starttime.desc())
                .all()
    )
    cessations = ( certifs.join(certificates.Cessation)
                .filter(certificates.Certificate.certif_type ==\
                                                    constants.FILE_CESSATION)
                .join(schedule.Appointment, schedule.Agenda)
                .order_by(schedule.Agenda.starttime.desc())
                .all()
    )

    return render_template('list_certificates.html',
                                patient=patient,
                                appointment=appointment,
                                presences=presences,
                                cessations=cessations)

@app.route('/add/presence_certificate?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
def add_presence_certificate(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    presence_form = PresenceForm(request.form)

    if ( request.method == 'POST' and presence_form.validate()
        and 'save_print' in request.form ):
        pdf_out = make_presence_certificate(patient_id, appointment_id,
                                                        presence_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        filename = md5.new(pdf_out).hexdigest()
        with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
            f.write(pdf_out)

        file_values = {
            'md5': filename,
            'file_type': constants.FILE_PRESENCE,
            'mimetype': 'application/pdf',
        }
        file_in_db = ( meta.session.query(documents.Files)
            .filter(documents.Files.md5 == filename)
            .one_or_none()
        )
        
        if file_in_db:
            return response

        new_file = documents.Files(**file_values)
        meta.session.add(new_file)
        meta.session.commit()

        certificate_values = {
            'dentist_id': appointment.dentist_id,
            'patient_id': patient_id,
            'appointment_id': appointment_id,
            'file_id': new_file.id,
            'certif_type': constants.FILE_PRESENCE,
        }
        new_certificate = certificates.Certificate(**certificate_values)
        meta.session.add(new_certificate)
        meta.session.commit()

        return response

    if ( request.method == 'POST' and presence_form.validate()
        and 'preview' in request.form ):
        pdf_out = make_presence_certificate(patient_id, appointment_id,
                                                        presence_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        return response

    presence_form.first_part.data = CERTIFICATE_FIRST_PART
    presence_form.second_part.data = CERTIFICATE_SECOND_PART
    presence_form.third_part.data = CERTIFICATE_THIRD_PART
    presence_form.identity_number.data = patient.identity_number_2
    presence_form.day.data = appointment.agenda.starttime.date()
    presence_form.starttime.data =\
                        appointment.agenda.starttime.time()
    presence_form.endtime.data =\
                        appointment.agenda.endtime.time()
    return render_template('add_presence_certificate.html', patient=patient,
                                                appointment=appointment,
                                                presence_form=presence_form)

@app.route('/add/cessation_certificate?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'])
def add_cessation_certificate(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)
    cessation_form = CessationForm(request.form)

    if ( request.method == 'POST' and cessation_form.validate()
        and 'save_print' in request.form ):
        pdf_out = make_cessation_certificate(patient_id, appointment_id,
                                                        cessation_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        filename = md5.new(pdf_out).hexdigest()
        with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
            f.write(pdf_out)

        file_values = {
            'md5': filename,
            'file_type': constants.FILE_CESSATION,
            'mimetype': 'application/pdf',
        }
        file_in_db = ( meta.session.query(documents.Files)
            .filter(documents.Files.md5 == filename)
            .one_or_none()
        )
        
        if file_in_db:
            return response

        new_file = documents.Files(**file_values)
        meta.session.add(new_file)
        meta.session.commit()

        certificate_values = {
            'dentist_id': appointment.dentist_id,
            'patient_id': patient_id,
            'appointment_id': appointment_id,
            'file_id': new_file.id,
            'certif_type': constants.FILE_CESSATION,
            'days_number': cessation_form.days_number.data,
        }
        new_certificate = certificates.Cessation(**certificate_values)
        meta.session.add(new_certificate)
        meta.session.commit()

        return response

    if ( request.method == 'POST' and cessation_form.validate()
        and 'preview' in request.form ):
        pdf_out = make_cessation_certificate(patient_id, appointment_id,
                                                        cessation_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        return response

    cessation_form.first_part.data = CERTIFICATE_FIRST_PART
    cessation_form.second_part.data = CERTIFICATE_SECOND_PART
    cessation_form.third_part.data = CERTIFICATE_THIRD_PART
    cessation_form.fourth_part.data = CESSATION_FOURTH_PART
    cessation_form.identity_number.data = patient.identity_number_2
    cessation_form.day.data = appointment.agenda.starttime.date()
    return render_template('add_cessation_certificate.html', patient=patient,
                                                appointment=appointment,
                                                cessation_form=cessation_form)
