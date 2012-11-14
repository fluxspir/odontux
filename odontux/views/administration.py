# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
from wtforms import (Form, 
                     IntegerField, SelectField, TextField, BooleanField,
                     validators)
import sqlalchemy
from odontux.models import meta, administration
from odontux.secret import SECRET_KEY
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants
from odontux.views import forms
from odontux.views.log import index
from odontux.models import meta, administration


gen_info_fields = [ "title", "lastname", "firstname", "qualifications", 
                    "preferred_name", "correspondence_name", "sex", "dob", 
                    "job", "inactive", "time_stamp", 
                    "socialsecurity_id", "office_id", "dentist_id" ]

family_fields = [ "family_id" ]
SSN_fields = [ ("SSN", "number"), ("cmu", "cmu"), ("insurance", "insurance") ]

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
    payer = BooleanField(_('Is payer'))
    SSN = TextField(_('Social Security Number'))
    cmu = BooleanField(_('CMU(fr)'))
    insurance = TextField(_('Insurance'))
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
    """ Adding a new patient in database
        ...
    """
    # the administrator don't have the right/use to create patient
    # this task should be reserve to other roles, which are
    # Secretary (when the patient first call/come, she may create a file
    # Assisant/Nurse to help the dentist
    # The dentist himself
    if session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for("allpatients"))

    # Forms used for adding a new patient : 
    # one is patient's specific :
    gen_info_form = PatientGeneralInfoForm(request.form)
    # three are used for odontux_users and medecine doctors, too
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)

    if request.method == 'POST' and form.validate():

        # Stick general information about new patient in database
        {f: getattr(form, f).data for f in gen_info_fields}
        new_patient = administration.Patient(**values)
        meta.session.add(new_patient)
        meta.session.commit()

        # A family is define in odontux mostly by the fact that
        # they live together. 
        for f in family_fields:
            # If patient in a family that is already in database, just tell 
            # which family he's in.
            if getattr(form, f).data:
                value[f] = getattr(form, f).data
            else:
                # Create new family and put the new patient in it.
                new_family = administration.Family()
                meta.session.add(new_family)
                meta.session.commit()
                new_patient.family_id = new_family.id
                meta.session.commit()
                # Give the patient, member of family an address 
                address_args = {f: getattr(form, f).data 
                                for f in forms.address_fields}
                new_patient.family.addresses.append(administration.Address(
                                                    **address_args))
        meta.session.commit()

        # Now, we'll see if patient will pay for himself and for his family ;
        # if not, it must be someone from his family who'll pay.
        if form.payer.data:
            # Mark the patient as a payer
            new_payer = administration.Payer(**{"patient_id": new_patient.id,})
            meta.session.add(new_payer)
            meta.session.commit()
            # precise that in his family, he pays.
            new_patient.family.payers.append(new_payer)
            meta.session.commit()

        # Phone number, in order to contact him.
        phone_args = {g: getattr(form, f).data for f,g in forms.phone_fields}
        new_patient.phones.append(administration.Phone(**phone_args))
        meta.session.commit()

        # Mail
        mail_args = {f: getattr(form, f).data for f in forms.mail_fields}
        new_patient.mails.append(administration.Mail(**mail_args))
        meta.session.commit()

        ##################################
        # The Social Security Number : SSN
        # ################################
        if form.SSN.data:
            # Verify if number already in database, for example children who
            # are under parent's social security.
            try:
                SSN_id = meta.session.query(constants.SocialSecurityLocale)\
                    .filter(constants.SocialSecurityLocale.number\
                            == form.SSN.data).one().id

            # If the number is new to database :
            except sqlalchemy.orm.exc.NoResultFound:
                SSN_args = {g: getattr(form, f).data for f,g in SSN_fields}
                new_SSN = constants.SocialSecurityLocale(**SSN_args)
                meta.session.add(new_SSN)
                meta.session.commit()
                SSN_id = new_SSN.id

        else:
            # If there weren't any SSNumber given, try anyway to add "cmu"
            # and insurance hypothetic values into database
            SSN_args = {g: getattr(form, f).data for f,g in SSN_fields}
            new_SSN = constants.SocialSecurityLocale(**SSN_args)
            meta.session.add(new_SSN)
            meta.session.commit()
            SSN_id = new_SSN.id

        # Tell Patient class the SSN he is related to.
        new_patient.socialsecurity_id = SSN_id
        meta.session.commit()


    
    return render_template("/add/patient.html",
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form)
