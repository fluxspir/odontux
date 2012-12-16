# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/05
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import and_, or_
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField,
                    SelectField, BooleanField, TextAreaField, HiddenField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, users, administration
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.log import index

class OdontuxUserGeneralInfoForm(Form):
    title = SelectField(_('title'))
    lastname = TextField(_('lastname'), [validators.Required(),
                            validators.Length(min=1, max=30,
                            message=_("Need to provide MD's lastname"))],
                            filters=[forms.upper_field])
    firstname = TextField(_('firstname'), [validators.Length(max=30, 
                                        message=_("firstname too long"))],
                                        filters=[forms.title_field])
    qualifications = TextField(_('qualifications'), 
                                filters=[forms.title_field])
    correspondence_name = TextField(_('correspondence_name'), 
                                    filters=[forms.upper_field])
    sex = SelectField(_('Male'), 
                    choices=[ (_("M"), _("M")), (_("F"), _("F")) ])
    dob = forms.DateField(_('Date of Birth'))
    avatar_id = IntegerField(_('avatar_id'), [validators.Optional()])
    display_order = IntegerField(_('display_order'), [validators.Optional()])

class OdontuxUserGeneralInfoAdminForm(Form):
    """ Contains Fields that only admin is allowed to modify."""
    username = TextField(_('username'), [validators.Required(),
                                    validators.Length(min=1, max=20)],
                                     filters=[forms.lower_field])
    role = SelectField(_('role'), coerce=int)
    status = BooleanField(_('status'))
    comments = TextAreaField(_('comments'))
    modified_by = IntegerField(_('modified_by'), [validators.Optional()])
    time_stamp = forms.DateField(_("time_stamp"))

class DentistSpecificForm(Form):
    registration = TextField(_('registration'))

class DentistSpecificAdminForm(Form):
    gnucash_url = TextField(_("gnucash_url"))

class OdontuxUserPasswordForm(Form):
    password = PasswordField(_('password'), [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField(_('Repeat Password'))


class DentalOfficeForm(Form):
    dental_office_id = HiddenField(_('id'))
    office_name = TextField(_("office_name"))
    owner_lastname = TextField(_("owner_lastname"))
    owner_firstname = TextField(_("owner_firstname"))
    url = TextField(_("url"))


def get_gen_info_field_list():
    return [ "title", "lastname", "firstname", "qualifications", 
             "correspondence_name", "sex", "dob", "avatar_id" ]

def get_gen_info_admin_field_list():
    return [ "username", "role" , "status", "comments", "modified_by", 
             "time_stamp" ]

def get_dentist_specific_field_list():
    return [ "registration" ]

def get_dentist_specific_admin_field_list():
    return [ "gnucash_url" ]

def get_password_field_list():
    return [ "password" ]

def get_dental_office_field_list():
    return [ "office_name", "owner_lastname", "owner_firstname", "url"]


@app.route('/odontux_user/')
@app.route('/user/')
def list_users():
    checks.quit_patient_file()
    checks.quit_appointment()
    # when we only want user with role "request.form['role']
    if request.form and request.form['role']:
        try:
            odontuxusers = meta.session.query(users.OdontuxUser)\
            .filter(users.OdontuxUser.role == request.form['role']).all()
        except:
            pass
    # Print all users in database.
    else:
        odontuxusers = meta.session.query(users.OdontuxUser).all()
    
    # role_admin : role that is allowed to add new users ; should be "admin"
    return render_template('list_users.html', odontuxusers=odontuxusers) 

@app.route('/dental_office/')
def list_dental_offices():
    checks.quit_patient_file()
    checks.quit_appointment()
    dental_offices = meta.session.query(users.DentalOffice).all()
    return render_template('list_dental_offices.html', 
                            dental_offices=dental_offices)

@app.route('/add/user/', methods=['GET', 'POST'])
@app.route('/user/add/', methods=['GET', 'POST'])
def add_user():
    checks.quit_patient_file()
    checks.quit_appointment()
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for("index"))

    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()

    gen_info_admin_form = OdontuxUserGeneralInfoAdminForm(request.form)
    gen_info_admin_form.role.choices = constants.ROLES_LIST
    dentist_specific_form = DentistSpecificForm(request.form)
    dentist_specific_admin_form = DentistSpecificAdminForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    password_form = OdontuxUserPasswordForm(request.form)
    if (request.method == 'POST' and gen_info_form.validate()
        and address_form.validate() and phone_form.validate()
        and mail_form.validate and password_form.validate()
       ):
        values = {}
        for f in get_gen_info_field_list():
            values[f] = getattr(gen_info_form, f).data
        for f in get_gen_info_admin_field_list():
            values[f] = getattr(gen_info_admin_form, f).data
        for f in get_password_field_list():
            values[f] = getattr(password_form, f).data
        for f in get_dentist_specific_field_list():
            values[f] = getattr(dentist_specific_form, f).data
        for f in get_dentist_specific_admin_field_list():
            values[f] = getattr(dentist_specific_admin_form, f).data

        new_odontuxuser = users.OdontuxUser(**values)
        meta.session.add(new_odontuxuser)
        
        address_args = {f: getattr(address_form, f).data 
                        for f in forms.address_fields}
        new_odontuxuser.addresses.append(administration.Address(
                                         **address_args))

        phone_args = {g: getattr(phone_form, f).data 
                      for f,g in forms.phone_fields}
        new_odontuxuser.phones.append(administration.Phone(**phone_args))

        mail_args = {f: getattr(mail_form, f).data for f in forms.mail_fields}
        new_odontuxuser.mails.append(administration.Mail(**mail_args))

        meta.session.commit()
        return redirect(url_for('list_users'))

    return render_template('/add_user.html/', 
                        gen_info_form=gen_info_form,
                        gen_info_admin_form=gen_info_admin_form,
                        address_form=address_form,
                        phone_form=phone_form,
                        mail_form=mail_form,
                        password_form=password_form,
                       dentist_specific_form=dentist_specific_form,
                       dentist_specific_admin_form=dentist_specific_admin_form)

@app.route('/dental_office/add/', methods=['GET', 'POST'])
def add_dental_office():
    checks.quit_patient_file()
    checks.quit_appointment()
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    dental_office_form = DentalOfficeForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    if (request.method == 'POST' and dental_office_form.validate()
        and address_form.validate() and phone_form.validate()
        and mail_form.validate()
       ):
        values = {f: getattr(dental_office_form, f).data 
                            for f in get_dental_office_field_list()}
        new_dental_office = users.DentalOffice(**values)
        meta.session.add(new_dental_office)

        address_args = {f: getattr(address_form, f).data
                        for f in forms.address_fields}
        new_dental_office.addresses.append(administration.Address(
                                                **address_args))
        phone_args = {g: getattr(phone_form, f).data
                        for f,g in forms.phone_fields}
        new_dental_office.phones.append(administration.Phone(
                                                **phone_args))
        mail_args = {f: getattr(mail_form, f).data
                        for f in forms.mail_fields}
        meta.session.commit()
        return redirect(url_for('list_dental_offices'))
    return render_template('add_dental_office.html',
                            dental_office_form=dental_office_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form)

# Function for printing the user's updating page, and getting 
# general and information fields.
@app.route('/user/update_user?id=<int:body_id>&'
            'form_to_display=<form_to_display>/', methods=['GET', 'POST'])
def update_user(body_id, form_to_display):
    checks.quit_patient_file()
    checks.quit_appointment()

    user = forms._get_body(body_id, "user")
    if not forms._check_body_perm(user, "user"):
        return redirect(url_for('list_users'))

    # For updating info of user, we're dealing with the form 
    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()

    if session['role'] == constants.ROLE_ADMIN:
        gen_info_admin_form = OdontuxUserGeneralInfoAdminForm(request.form)
        gen_info_admin_form.role.choices = constants.ROLES_LIST
    else:
        gen_info_admin_form = ""
    if user.role == constants.ROLE_DENTIST: 
        dentist_specific_form = DentistSpecificForm(request.form)
    else:
        dentist_specific_form = ""
    if (session['role'] == constants.ROLE_ADMIN 
            and user.role == constants.ROLE_DENTIST):
        dentist_specific_admin_form = DentistSpecificAdminForm(request.form)
    else:
        dentist_specific_admin_form = ""

    if request.method == 'POST' and gen_info_form.validate():
        for f in get_gen_info_field_list():
            setattr(user, f, getattr(gen_info_form, f).data)
        if user.role == constants.ROLE_DENTIST:
            for f in get_dentist_specific_field_list():
                setattr(user, f, getattr(dentist_specific_form, f).data)
        if (session['role'] == constants.ROLE_ADMIN
            and gen_info_admin_form.validate() ):
            for f in get_gen_info_admin_field_list():
                setattr(user, f, getattr(gen_info_admin_form, f).data)
            if user.role == constants.ROLE_DENTIST:
                for f in get_dentist_specific_admin_field_list():
                    setattr(user, f, 
                            getattr(dentist_specific_admin_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_user', 
                                 body_id=body_id, 
                                 form_to_display="gen_info"))

    # When loading the whole update page, we use the form containing all fields
    # after prepopulating it
    for f in get_gen_info_field_list():
        getattr(gen_info_form, f).data = getattr(user, f)
    if user.role == constants.ROLE_DENTIST:
        for f in get_dentist_specific_field_list():
            getattr(dentist_specific_form, f).data = getattr(user, f)
    if session['role'] == constants.ROLE_ADMIN:
        for f in get_gen_info_admin_field_list():
            getattr(gen_info_admin_form, f).data = getattr(user, f)
        if user.role == constants.ROLE_DENTIST:
            for f in get_dentist_specific_admin_field_list():
                try:
                    getattr(dentist_specific_admin_form, f).data =\
                    getattr(user, f)
                except:
                    pass

    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    password_form = OdontuxUserPasswordForm(request.form)
    return render_template('/update_user.html', 
                            user=user,
                            form_to_display=form_to_display,
                            gen_info_form=gen_info_form,
                            gen_info_admin_form=gen_info_admin_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            password_form=password_form,
                            dentist_specific_form=dentist_specific_form,
                       dentist_specific_admin_form=dentist_specific_admin_form)

@app.route('/dental_office/update?id=<int:body_id>'
            '&form_to_display=<form_to_display>/', methods=['GET', 'POST'])
def update_dental_office(body_id, form_to_display):
    """ """
    checks.quit_patient_file()
    checks.quit_appointment()
    if not session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    dental_office = meta.session.query(users.DentalOffice)\
            .filter(users.DentalOffice.id == body_id).one()

    dental_office_form = DentalOfficeForm(request.form)
    if request.method == 'POST' and dental_office_form.validate():
        for f in get_dental_office_field_list():
            setattr(dental_office, f, getattr(dental_office_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_dental_office', 
                            body_id=dental_office.id,
                            form_to_display = "gen_info"))

    # When loading the whole update page, we use the form containing all fields
    dental_office_form = DentalOfficeForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    return render_template('/update_dental_office.html',
                            dental_office=dental_office,
                            form_to_display=form_to_display,
                            dental_office_form=dental_office_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form)

@app.route('/user/update_user_password?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_user_password(body_id, form_to_display):
    user = forms._get_body(body_id, "user")
    if not forms._check_body_perm(user, "user"):
        return redirect(url_for('list_users'))
    password_form = OdontuxUserPasswordForm(request.form)
    if request.method == 'POST' and password_form.validate():
        for f in get_password_field_list():
            setattr(user, f, getattr(password_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_user', 
                                 body_id=body_id,
                                 form_to_display="gen_info"))

@app.route('/dental_office/update_address?id=<int:body_id>'
            '&form_to_display=<form_to_display>/', methods=['POST'])
def update_dental_office_address(body_id, form_to_display):
    if forms.update_body_address(body_id, "dental_office"):
        return redirect(url_for("update_dental_office",
                                body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_dental_offices'))

@app.route('/user/update_user_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_user_address(body_id, form_to_display):
    if forms.update_body_address(body_id, "user"):
        return redirect(url_for("update_user", 
                                 body_id=body_id,
                                 form_to_display="address"))
    return redirect(url_for('list_users'))
 
@app.route('/dental_office/add_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_dental_office_address(body_id, form_to_display):
    if forms.add_body_address(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id, 
                                 form_to_display="address"))
    return redirect(url_for('list_dental_offices'))
       
@app.route('/user/add_user_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_user_address(body_id, form_to_display):
    if forms.add_body_address(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id, 
                                 form_to_display="address"))
    return redirect(url_for('list_users'))

@app.route('/dental_office/delete_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_dental_office_address(body_id, form_to_display):
    if forms.delete_body_address(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="address"))
    return redirect(url_for('list_dental_offices'))

@app.route('/user/delete_user_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_user_address(body_id, form_to_display):
    if forms.delete_body_address(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="address"))
    return redirect(url_for('list_users'))

@app.route('/dental_office/update_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_dental_office_phone(body_id, form_to_display):
    if forms.update_body_phone(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_dental_offices'))
 
@app.route('/user/update_user_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_user_phone(body_id, form_to_display):
    if forms.update_body_phone(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_users'))
 
@app.route('/dental_office/add_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_dental_office_phone(body_id, form_to_display):
    if forms.add_body_phone(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_dental_offices'))
   
@app.route('/user/add_user_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_user_phone(body_id, form_to_display):
    if forms.add_body_phone(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_users'))

@app.route('/dental_office/delete_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_dental_office_phone(body_id, form_to_display):
    if forms.delete_body_phone(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_form('list_dental_offices'))

@app.route('/user/delete_user_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_user_phone(body_id, form_to_display):
    if forms.delete_body_phone(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_form('list_users'))

@app.route('/dental_office/update_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_dental_office_mail(body_id, form_to_display):
    if forms.update_body_mail(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_dental_offices'))

@app.route('/user/update_user_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_user_mail(body_id, form_to_display):
    if forms.update_body_mail(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_users'))

@app.route('/dental_office/add_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_dental_office_mail(body_id, form_to_display):
    if forms.add_body_mail(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_dental_offices'))

@app.route('/user/add_user_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_user_mail(body_id, form_to_display):
    if forms.add_body_mail(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_users'))

@app.route('/dental_office/delete_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_dental_office_mail(body_id, form_to_display):
    if forms.delete_body_mail(body_id, "dental_office"):
        return redirect(url_for("update_dental_office", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_dental_offices'))

@app.route('/user/delete_user_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_user_mail(body_id, form_to_display):
    if forms.delete_body_mail(body_id, "user"):
        return redirect(url_for("update_user", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_users'))
