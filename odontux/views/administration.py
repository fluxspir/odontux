# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# licence BSD
#
import pdb
from flask import ( session, render_template, request, redirect, url_for, 
                    abort, jsonify )
from wtforms import (Form, 
                     IntegerField, SelectField, TextField, BooleanField, 
                     RadioField, SelectMultipleField, DateField, HiddenField,
                     validators)
import sqlalchemy
from sqlalchemy import or_
from odontux.secret import SECRET_KEY
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants, checks
from odontux import gnucash_handler
from odontux.views import forms
from odontux.views.log import index
from odontux.models import ( meta, administration, users, act, headneck, 
                            endobuccal )


# Fields too use in treatment of forms
def get_gen_info_field_list():
    return [ "title", "lastname", "firstname", "qualifications", 
                    "preferred_name", "correspondence_name", "sex", "dob", 
                    "job", "inactive", "time_stamp",
                    "office_id", "dentist_id",
                    "identity_number_1", "identity_number_2" ]

class PatientGeneralInfoForm(Form):
    title = SelectField(_('title'))
    lastname = TextField(_('lastname'), [validators.Required(
                          message=_("Lastname required")),
                          validators.Length(min=1, max=30,
                          message=_("lastname between 1 and 30 characters"))],
                          filters=[forms.upper_field])
    firstname = TextField(_('firstname'), [validators.Length(max=30, 
                           message=_("firstname too long"))],
                           filters=[forms.title_field])
    identity_number_1 = TextField(_('Identity Number'))
    identity_number_2 = TextField(_('Licence number or CPF'))
    preferred_name = TextField(_('preferred_name'), [validators.Length(max=30,
                                message=_("preferred name too long"))])
    correspondence_name = TextField(_('correspondence_name'),
                                [validators.Length(max=30, 
                                message=_("correspondence name too long"))])
    sex = RadioField(_('Sex'), choices=[("m", _("Male")), ("f", _("Female"))])
    dob = DateField(_('Date of Birth'), [validators.Optional()])
    job = TextField(_('Job'))
    inactive = BooleanField(_('Inactive'))
    qualifications = TextField(_('qualifications'), 
                                filters=[forms.title_field])
#    family_id = HiddenField(_('family_id'), [validators.Optional()])
#    family_member = TextField(_('family_member'), [validators.Optional()])
    office_id = SelectField(_('Office_id'), [validators.Required(
                               message=_("Please specify office_id"))], 
                               coerce=int)
    dentist_id = SelectField(_('Dentist_id'), [validators.Required(
                                message=_("Please specify dentist_id"))],
                                coerce=int)
    time_stamp = DateField(_("Time_stamp"), [validators.Optional()])
   
class HealthCarePlanPatientForm(Form):
    healthcare_plans_id = SelectMultipleField(_('Healthcare plan'), coerce=int)

@app.route('/patients/')
def allpatients():
    patients = meta.session.query(administration.Patient)\
               .order_by(administration.Patient.lastname).all()
    return render_template('list_patients.html', patients=patients)

@app.route('/patient?id=<int:body_id>/')
def enter_patient_file(body_id):
    patient = checks.get_patient(body_id)
    return render_template('patient_file.html', patient=patient)

#@app.route('/find/family_member')
#def find_family_member():
#    name = request.args.get('name', None)
#    if name:
##        # Won't work:part of keyword would be in firstname and other in last.
##        name = name.split(" ")
##        keyword = u"%"
#        keyword = u'%{}%'.format(name)
##        for name_part in name:
##            keyword = keyword + u'{}%'.format(name_part)
#        patients = ( meta.session.query(administration.Patient)
#                        .filter(or_(
#                            administration.Patient.firstname.ilike(keyword),
#                            administration.Patient.lastname.ilike(keyword) )
#                        ).order_by(administration.Patient.firstname,
#                                administration.Patient.lastname )
#                        .all()
#        )
#        if not patients:
#            return jsonify(success=False)
#        data = {}
#        for patient in patients:
#            data[str(patient.id)] = ( patient.firstname + " " + 
#                                                            patient.lastname,
#                                        patient.family.id )
#        return jsonify(success=True, **data)
#    return jsonify(success=False)
#
@app.route('/add/patient/', methods=['GET', 'POST'])
@app.route('/add/patient?meeting_id=<int:meeting_id>', methods=['GET', 'POST'])
def add_patient(meeting_id=0):
    """ Adding a new patient in database
    """
    # the administrator don't have the right/use to create patient
    # this task should be reserve to other roles, which are
    # Secretary (when the patient first call/come, she may create a file
    # Assisant/Nurse to help the dentist
    # The dentist himself
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                    constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for("allpatients"))
   
    # Forms used for adding a new patient : 
    # two are patient's specific :
    gen_info_form = PatientGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()
    gen_info_form.office_id.choices = [ (office.id, office.office_name) 
                for office in meta.session.query(users.DentalOffice).all() ]
    gen_info_form.dentist_id.choices = [ (dentist.id, dentist.firstname + " " 
                                                            + dentist.lastname)
                for dentist in meta.session.query(users.OdontuxUser).filter(
                users.OdontuxUser.role == constants.ROLE_DENTIST).order_by(
                users.OdontuxUser.lastname).all() ]

    hcp_patient_form = HealthCarePlanPatientForm(request.form)
    hcp_patient_form.healthcare_plans_id.choices = [ (hc.id, hc.name) 
                for hc in meta.session.query(act.HealthCarePlan).all() ]
    if not hcp_patient_form.healthcare_plans_id.choices:
        return redirect(url_for('add_healthcare_plan'))

    # three are used for odontux_users and medecine doctors, too
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)

    if (request.method == 'POST' and gen_info_form.validate()
        and address_form.validate()
        and phone_form.validate() and mail_form.validate() ):

        # Verify patient isn't already in database
        patient = checks.is_body_already_in_database(gen_info_form, "patient")
        if patient:
            return redirect(url_for('update_patient', 
                                    body_id=patient.id,
                                    form_to_display="gen_info"))
        
        values = {f: getattr(gen_info_form, f).data 
                        for f in get_gen_info_field_list()}
        new_patient = administration.Patient(**values)
        meta.session.add(new_patient)
        meta.session.commit()
        
        for healthcare_plan_id in hcp_patient_form.healthcare_plans_id.data:
            hcp = ( meta.session.query(act.HealthCarePlan)
                        .filter(act.HealthCarePlan.id == healthcare_plan_id)
                        .one()
                )
            new_patient.hcs.append(hcp)
        meta.session.commit()

#        # A family is define in odontux mostly by the fact that
#        # they live together. 
#        family_field_list = ['family_id']
#        for f in family_field_list:
#            # If patient in a family that is already in database, just tell 
#            # which family he's in.
#            if getattr(gen_info_form, f).data:
#                value[f] = int(getattr(gen_info_form, f).data)
#            else:
#                # Create new family and put the new patient in it.
#                new_family = administration.Family()
#                meta.session.add(new_family)
#                meta.session.commit()
#                new_patient.family_id = new_family.id
#                meta.session.commit()
                # Give the patient, member of family an address 
        address_args = {f: getattr(address_form, f).data 
                                for f in forms.address_fields}

        if any(address_args.values()):
            new_address = admnistration.Address(**address_args)
            meta.session.add(new_address)
            meta.session.commit()
            new_patient.address_id = new_address.id

#        # Now, we'll see if patient will pay for himself and for his family ;
#        # if not, it must be someone from his family who'll pay.
#        if gen_info_form.payer.data:
#            # Mark the patient as a payer
#            new_payer = administration.Payer(**{'id': new_patient.id})
#            meta.session.add(new_payer)
#            meta.session.commit()
#            # precise that in his family, he pays.
#            new_patient.family.payers.append(new_payer)
#            meta.session.commit()
#            
        # Phone number, in order to contact him.
        
        phone_args = {g: getattr(phone_form, f).data
                      for f,g in forms.phone_fields}

        if any(phone_args.values()):
            new_patient.phones.append(administration.Phone(**phone_args))
            meta.session.commit()

        # Mail
        mail_args = {f: getattr(mail_form, f).data for f in forms.mail_fields}
        if any(mail_args.values()):
            new_patient.mails.append(administration.Mail(**mail_args))
            meta.session.commit()

#        ##################################
#        # The Social Security Number : SSN
#        ##################################
#        # The social security info may have been entered via the 
#        # socialsecurity_id, encountered in gen_info_form, and which
#        # is used usually while insering children of already known patients
#        # in database.
#        if SSN_form.SSN.data:
#            # Verify if number already in database, for example children who
#            # are under parent's social security.
#            try:
#                SSN_id = meta.session.query(SocialSecurityLocale)\
#                    .filter(SocialSecurityLocale.number\
#                            == SSN_form.SSN.data).one().id
#
#            # If the number is new to database :
#            except sqlalchemy.orm.exc.NoResultFound:
#                SSN_args = {g: getattr(SSN_form, f).data 
#                                    for f,g in get_SSN_field_list() }
#                new_SSN = SocialSecurityLocale(**SSN_args)
#                meta.session.add(new_SSN)
#                meta.session.commit()
#                SSN_id = new_SSN.id
#        
#        else:
#            # If there weren't any SSNumber given, try anyway to add "cmu"
#            # and insurance hypothetic values into database
#            SSN_args = {g: getattr(SSN_form, f).data 
#                                    for f,g in get_SSN_field_list() }
#            new_SSN = SocialSecurityLocale(**SSN_args)
#            meta.session.add(new_SSN)
#            meta.session.commit()
#            SSN_id = new_SSN.id
#
#        # Tell Patient class the SSN he is related to.
#        new_patient.socialsecurity_id = SSN_id
#        meta.session.commit()

        #Add the new patient to gnucash !
        comptability = gnucash_handler.GnuCashCustomer(new_patient.id, 
                                                 new_patient.dentist_id)
        new_customer = comptability.add_customer()
        
        return redirect(url_for('add_patient_appointment', 
                                            body_id=new_patient.id,
                                            meeting_id=meeting_id))

    return render_template("add_patient.html",
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            hcp_patient_form=hcp_patient_form,
                            meeting_id=meeting_id)

@app.route('/delete/patient?id=<int:body_id>')
def delete_patient(body_id):
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for('index'))
   
    patient = meta.session.query(administration.Patient).filter(
                        administration.Patient.id == body_id).one_or_none()
    meta.session.delete(patient)
    meta.session.commit()
    return redirect(url_for('index'))


@app.route('/patient/update_patient?id=<int:body_id>'
           '&form_to_display=<form_to_display>/',
            methods=[ 'GET', 'POST'])
def update_patient(body_id, form_to_display):
    """ """
    patient = forms._get_body(body_id, "patient")
    if not forms._check_body_perm(patient, "patient"):
        return redirect(url_for('list_patients', body_id=body_id))

    # only need form for *patient_gen_info* update here.
    # Others are only needed for the 'GET', see below.
    gen_info_form = PatientGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()
    gen_info_form.office_id.choices = [ (office.id, office.office_name) 
                for office in meta.session.query(users.DentalOffice).all() ]
    gen_info_form.dentist_id.choices = [ (dentist.id, dentist.firstname + " " 
                                                            + dentist.lastname)
                for dentist in meta.session.query(users.OdontuxUser).filter(
                users.OdontuxUser.role == constants.ROLE_DENTIST).order_by(
                users.OdontuxUser.lastname).all() 
                                        ]
    if request.method == 'POST' and gen_info_form.validate():
        for f in get_gen_info_field_list():
            setattr(patient, f, getattr(gen_info_form, f).data)

#        if not gen_info_form.family_id.data or not gen_info_form.family_member.data:
#            new_family = administration.Family()
#            meta.session.add(new_family)
#            meta.session.commit()
#            patient.family_id = new_family.id
#        else:
#            patient.family_id = gen_info_form.family_id.data
        meta.session.commit()

        # We should update in gnucash too the patient
        comptability = gnucash_handler.GnuCashCustomer(patient.id,  
                                                       patient.dentist_id) 
        customer = comptability.update_customer()
        return redirect(url_for('update_patient', body_id=body_id,
                                form_to_display="gen_info"))


    # When we 'GET' the page, we need all form, and fill in
    # the gen_info and SSN_form from here
    for f in get_gen_info_field_list():
        getattr(gen_info_form, f).data = getattr(patient, f)

#    # payer
#    for payer in patient.family.payers:
#        if patient.id == payer.id:
#            gen_info_form.payer.data = True
#    gen_info_form.family_id.data = patient.family_id
#    
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    # need to return patient both as "patient" AND "body" :
    # as "patient" for the header pagetitle,
    # as "body" for the updating form.
    other_healthcare_plans = (
        meta.session.query(act.HealthCarePlan)
            .filter(
                ~act.HealthCarePlan.patients.any(
                    administration.Patient.id == patient.id)
            )
            .all()
        )
    return render_template('/update_patient.html', body=patient,
                            patient=patient,
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            other_healthcare_plans=other_healthcare_plans)

@app.route('/add/patient_to_healthcare_plan?pid=<int:patient_id>'
            '&hcpid=<int:healthcare_plan_id>')
def add_patient_to_healthcare_plan(patient_id, healthcare_plan_id):
    patient = (
        meta.session.query(administration.Patient)
            .filter(administration.Patient.id == patient_id)
            .one()
        )
    healthcare_plan = (
        meta.session.query(act.HealthCarePlan)
            .filter(act.HealthCarePlan.id == healthcare_plan_id)
            .one()
        )
    patient.hcs.append(healthcare_plan)
    meta.session.commit()
    return redirect(url_for('update_patient', body_id=patient_id,
                                form_to_display='healthcare_plans'))

@app.route('/remove/patient_from_healthcare_plan?pid=<int:patient_id>&hcpid=<int:healthcare_plan_id>')
def remove_patient_from_healthcare_plan(patient_id, healthcare_plan_id):
    patient = (
        meta.session.query(administration.Patient)
            .filter(administration.Patient.id == patient_id)
            .one()
        )
    healthcare_plan = (
        meta.session.query(act.HealthCarePlan)
            .filter(act.HealthCarePlan.id == healthcare_plan_id)
            .one()
        )
    patient.hcs.remove(healthcare_plan)
    meta.session.commit()
    return redirect(url_for('update_patient', body_id=patient_id,
                                form_to_display='healthcare_plans'))


#@app.route('/patient/update_patient_SSN?id=<int:body_id>'
#           '&form_to_display=<form_to_display>', methods=['POST'])
#def update_patient_SSN(body_id, form_to_display):
#    patient = forms._get_body(body_id, "patient")
#    if not forms._check_body_perm(patient, "patient"):
#        return redirect(url_for('list_patients', body_id=body_id))
#    SSN_form = SocialSecurityForm(request.form)
#    if request.method == "POST" and SSN_form.validate():
#        if SSN_form.SSN.data:
#            # Verify if number already in database, for example children who
#            # are under parent's social security.
#            try:
#                SSN = meta.session.query(SocialSecurityLocale)\
#                    .filter(SocialSecurityLocale.number\
#                            == SSN_form.SSN.data).one()
#                # The SSN already exists, the patient will enter under this SSN
#                # and we are now going to update the cmu and insurance.
#                for f,g in get_SSN_field_list():
#                    setattr(SSN, g, getattr(SSN_form, f).data)
#                meta.session.commit()
#                SSN_id = SSN.id
#
#            # If the number is new to database :
#            except sqlalchemy.orm.exc.NoResultFound:
#                SSN_args = {g: getattr(SSN_form, f).data 
#                                            for f,g in get_SSN_field_list() }
#                new_SSN = SocialSecurityLocale(**SSN_args)
#                meta.session.add(new_SSN)
#                meta.session.commit()
#                SSN_id = new_SSN.id
#        
#        else:
#            # If there weren't any SSNumber given, try anyway to add "cmu"
#            # and insurance hypothetic values into database
#            SSN_args = {g: getattr(SSN_form, f).data 
#                                            for f,g in get_SSN_field_list() }
#            new_SSN = SocialSecurityLocale(**SSN_args)
#            meta.session.add(new_SSN)
#            meta.session.commit()
#            SSN_id = new_SSN.id
#
#        # Tell Patient class the SSN he is related to.
#        patient.socialsecurity_id = SSN_id
#        meta.session.commit()
#        return redirect(url_for('update_patient', body_id=body_id,
#                                form_to_display="SSN"))
#

@app.route('/patient/update_patient_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_patient_address(body_id, form_to_display):
    if forms.update_body_address(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_patients'))
        
@app.route('/patient/add_patient_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_patient_address(body_id, form_to_display):
    if forms.add_body_address(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_patients'))

@app.route('/patient/delete_patient_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_patient_address(body_id, form_to_display):
    if forms.delete_body_address(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="address"))
    return redirect(url_form('list_patients'))

@app.route('/patient/update_patient_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_patient_phone(body_id, form_to_display):
    if forms.update_body_phone(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_for('list_patients'))
    
@app.route('/patient/add_patient_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_patient_phone(body_id, form_to_display):
    if forms.add_body_phone(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_for('list_patients'))

@app.route('/patient/delete_patient_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_patient_phone(body_id, form_to_display):
    if forms.delete_body_phone(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_form('list_patients'))

@app.route('/patient/update_patient_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_patient_mail(body_id, form_to_display):
    if forms.update_body_mail(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_for('list_patients'))

@app.route('/patient/add_patient_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_patient_mail(body_id, form_to_display):
    if forms.add_body_mail(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_for('list_patients'))

@app.route('/patient/delete_patient_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_patient_mail(body_id, form_to_display):
    if forms.delete_body_mail(body_id, "patient"):
        return redirect(url_for("update_patient", body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_form('list_patients'))

