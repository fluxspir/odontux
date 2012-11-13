# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
from wtforms import Form, IntegerField, SelectField, TextField, BooleanField
import sqlalchemy
from odontux.models import meta, administration
from odontux.secret import SECRET_KEY
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants
from odontux.views import forms
from odontux.views.log import index


class PatientGeneralInfoForm(Form):
    family_id = IntegerField(_('family_id'), [validators.Optional()])
    socialsecurity_id = IntegerField(_('socialsecurity_id'), 
                                     [validators.Optional()])
    title = SelectField(_('title'), choices=forms.title_list)
    lastname = TextField(_('lastname'), [validators.Required(
                          message=_("Lastname required")),
                          validators.Length(min=1, max=30,
                          message=_("Must provide lastname"))],
                          filters=[forms.upper_field])
    firstname = TextField(_('firstname'), [validators.Length(max=30, 
                           message=_("firstname too long"))],
                           filters=[forms.title_field])
    qualifications = TextField(_('qualifications'), 
                                filters=[forms.title_field])
    preferred_name = TextField(_('preferred_name'), [validators.Length(max=30,
                                message=_("preferred name too long"))])
    correspondence_name = TextField(_('correspondence_name'),
                                    [validators.Length(max=30, message=\
                                    _("correspondence name too long"))])
    sex = BooleanField(_('Male'))
    dob = forms.DateField(_('Date of Birth'))
    job = TextField(_('Job'))
    inactive = BooleanField(_('Inactive'))
    office_id = IntegerField(_('Office_id'), [validators.Required(
                               message=_("Please specify office_id"))])
    dentist_id = IntegerField(_('Dentist_id'), [validators.Required(
                                message=_("Please specify dentist_id"))])
    time_stamp = forms.DateField(_("Time_stamp"))

@app.route('/patient/')
def allpatients():
    patients = meta.session.query(administration.Patient).all()
    return render_template('search.html', patients=patients)

@app.route('/patient/<int:patient_id>/')
def patient(patient_id):
    patient = meta.session.query(administration.Patient)\
              .filter(administration.Patient.id == patient_id)\
              .one()

    if patient:
        session['patient_id'] = patient_id
        age = patient.age()
        birthday = patient.is_birthday()
        return render_template('patient_file.html', session=session,
                               patient=patient, age=age, birthday=birthday)

@app.route('/patient/add/', methods=['GET', 'POST'])
def add_patient():
    # the administrator don't have the right/use to create patient
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for("allpatients"))

    # Information general
    gen_info_form = PatientGeneralInfoForm(request.form)
