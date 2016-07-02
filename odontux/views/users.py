# -*- coding: utf-8 -*-
# Franck Labadille
# 2016/02/06
# v0.6
# Licence BSD
#

import pdb
import scrypt
from base64 import b64encode
import os
import calendar
import datetime

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import and_, or_
from sqlalchemy.orm import with_polymorphic
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField,
                    SelectField, BooleanField, TextAreaField, HiddenField,
                    DateField, DateTimeField, validators)

from odontux import constants, checks
from odontux.models import meta, users, contact
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
    dob = DateField(_('Date of Birth'))
    avatar_id = IntegerField(_('avatar_id'), [validators.Optional()])
    display_order = IntegerField(_('display_order'), [validators.Optional()])

class OdontuxUserGeneralInfoAdminForm(Form):
    """ Contains Fields that only admin is allowed to modify."""
    username = TextField(_('username'), [validators.Required(),
                                    validators.Length(min=1, max=20)],
                                     filters=[forms.lower_field])
    role = SelectField(_('role'), coerce=int)
    active = BooleanField(_('active'))
    comments = TextAreaField(_('comments'))
    modified_by = IntegerField(_('modified_by'), [validators.Optional()])
    creation_date = DateField(_("creation_date"))

class DentistSpecificForm(Form):
    registration = TextField(_('registration'))

class DentistSpecificAdminForm(Form):
    gnucash_url = TextField(_("gnucash_url"))

class OdontuxUserPasswordForm(Form):
    password = PasswordField(_('Password'), [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField(_('Repeat Password'))

class OdontuxUserNewPasswordForm(Form):
    old_password = PasswordField(_('Old Password'), [validators.Required()])
    new_password = PasswordField(_('New Password'), [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField(_('Repeat New Password'))

class OdontuxUserTimeSheetForm(Form):
    weekday = HiddenField(_('Weekday'))
    period = HiddenField(_('Period'))
    begin = TextField(_('Begin'), [validators.Optional()], 
                        render_kw={'size':'8px'})
    end = TextField(_('End'), [validators.Optional()], 
                        render_kw={'size':'8px'})
    dental_unit_id = SelectField(_('Dental Unit'), coerce=int )
    dentist_id = SelectField(_('Dentist'), coerce=int)

class DentalOfficeForm(Form):
    dental_office_id = HiddenField(_('id'))
    office_name = TextField(_("office_name"))
    owner_lastname = TextField(_("owner_lastname"))
    owner_firstname = TextField(_("owner_firstname"))
    url = TextField(_("url"))


def generate_timesheet_form(user_role):
    timesheet_form = {}
    for weekday in range(1,8):
        timesheet_form[weekday] = {}
        for period in constants.PERIODS.keys():
            timesheet_form[weekday][period] =\
                                    OdontuxUserTimeSheetForm(request.form)
            timesheet_form[weekday][period].weekday.data = weekday
            timesheet_form[weekday][period].period.data = period

#            if user_role == constants.ROLE_DENTIST:
            timesheet_form[weekday][period].dental_unit_id.choices =\
                        [ (dental_unit.id, dental_unit.name) for dental_unit in
                                meta.session.query(users.DentalUnit).all() ]

#            elif user_role == constants.ROLE_ASSISTANT:
            timesheet_form[weekday][period].dentist_id.choices =\
                [ (dentist.id, dentist.username) for dentist in
                    meta.session.query(users.OdontuxUser)
                    .filter(users.OdontuxUser.role == constants.ROLE_DENTIST)
                    .all()
                ]
            timesheet_form[weekday][period].dentist_id.choices.append(
                                                                    (0, ""))
    return timesheet_form

def get_gen_info_field_list():
    return [ "title", "lastname", "firstname", "qualifications", 
             "correspondence_name", "sex", "dob", "avatar_id" ]

def get_gen_info_admin_field_list():
    return [ "username", "role" , "active", "comments", "modified_by", 
             "creation_date" ]

def get_dentist_specific_field_list():
    return [ "registration" ]

def get_dentist_specific_admin_field_list():
    return [ "gnucash_url" ]

def get_password_field_list():
    return [ "password" ]

def get_dental_office_field_list():
    return [ "office_name", "owner_lastname", "owner_firstname", "url"]

@app.route('/portal/user/')
def portal_users():
    return render_template('portal_users.html')

@app.route('/odontux_user/')
@app.route('/user/')
def list_users():
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
    dental_offices = meta.session.query(users.DentalOffice).all()
    return render_template('list_dental_offices.html', 
                            dental_offices=dental_offices)

@app.route('/add/user/', methods=['GET', 'POST'])
@app.route('/user/add/', methods=['GET', 'POST'])
def add_user():
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for("index"))

    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()

    gen_info_admin_form = OdontuxUserGeneralInfoAdminForm(request.form)
    gen_info_admin_form.role.choices = constants.ROLES.items()
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
            values[f] = b64encode(scrypt.encrypt(os.urandom(64), 
                            getattr(password_form, f).data.encode("utf_8"), 
                            maxtime=0.5))
        for f in get_dentist_specific_field_list():
            values[f] = getattr(dentist_specific_form, f).data
        for f in get_dentist_specific_admin_field_list():
            values[f] = getattr(dentist_specific_admin_form, f).data

        new_odontuxuser = users.OdontuxUser(**values)
        meta.session.add(new_odontuxuser)
        
        address_args = {f: getattr(address_form, f).data 
                        for f in forms.address_fields}
        if any(address_args.values()):
            new_address = contact.Address(**address_args)
            meta.session.add(new_address)
            meta.session.commit()
            new_odontuxuser.address_id = new_address.id
#            new_odontuxuser.addresses.append(contact.Address(
#                                                            **address_args))
#
        phone_args = {g: getattr(phone_form, f).data 
                      for f,g in forms.phone_fields}
        if any(phone_args.values()):
            new_odontuxuser.phones.append(contact.Phone(**phone_args))

        mail_args = {f: getattr(mail_form, f).data for f in forms.mail_fields}
        if any(mail_args.values()):
            new_odontuxuser.mails.append(contact.Mail(**mail_args))

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
        new_dental_office.addresses.append(contact.Address(
                                                **address_args))
        phone_args = {g: getattr(phone_form, f).data
                        for f,g in forms.phone_fields}
        new_dental_office.phones.append(contact.Phone(
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

    user = forms._get_body(body_id, "user")
    if not forms._check_body_perm(user, "user"):
        return redirect(url_for('list_users'))

    # For updating info of user, we're dealing with the form 
    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    gen_info_form.title.choices = forms.get_title_choice_list()

    if session['role'] == constants.ROLE_ADMIN:
        gen_info_admin_form = OdontuxUserGeneralInfoAdminForm(request.form)
        gen_info_admin_form.role.choices = constants.ROLES.items()
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

    timesheet_form = generate_timesheet_form(user.role)
    # populate timesheet_form
    for weekday in range(1,8):
        for period in constants.PERIODS.keys():
            TS = (
                meta.session.query(users.TimeSheet)
                    .filter(
                        users.TimeSheet.user_id == user.id,
                        users.TimeSheet.weekday == weekday,
                        users.TimeSheet.period == period
                    )
                .one_or_none()
            )
            if TS:
                timesheet_form[weekday][period].begin.data = TS.begin
                timesheet_form[weekday][period].end.data = TS.end
                timesheet_form[weekday][period].dental_unit_id.data =\
                                                            TS.dental_unit_id

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
                            timesheet_form=timesheet_form,
                            calendar=calendar,
                            constants=constants,
                       dentist_specific_admin_form=dentist_specific_admin_form)

@app.route('/update/timesheet_1?body_id=<int:body_id>', methods=['POST'])
def update_timesheet_1(body_id):
 
    timesheet_fields = [ 'weekday', 'period', 'begin', 'end' ]
    dentist_timesheet_fields = [ 'dental_unit_id' ]
    assistant_timesheet_fields = [ 'dentist_id' ]
    
    user = (
        meta.session.query(users.OdontuxUser)
            .filter(users.OdontuxUser.id == body_id)
            .one()
        )
    
    timesheet_form = OdontuxUserTimeSheetForm(request.form)
#    if user.role == constants.ROLE_DENTIST:
    timesheet_form.dental_unit_id.choices =\
            [ (dental_unit.id, dental_unit.name) for dental_unit in
                meta.session.query(users.DentalUnit).all() ]
#    elif user.role == constants.ROLE_ASSISTANT:
    timesheet_form.dentist_id.choices =\
            [ (dentist.id, dentist.username) for dentist in
                meta.session.query(users.OdontuxUser)
                    .filter(users.OdontuxUser.role == constants.ROLE_DENTIST)
                    .all()
            ]
    timesheet_form.dentist_id.choices.append( (0, "" ) )
    try:
        begin = datetime.time(
        int(timesheet_form.begin.data.split(":")[0]),
        int(timesheet_form.begin.data.split(":")[1])
        )
        
        end = datetime.time(
        int(timesheet_form.end.data.split(":")[0]),
        int(timesheet_form.end.data.split(":")[1])
        )

        all_timesheets = with_polymorphic(users.TimeSheet, '*')
        TS = ( 
            meta.session.query(all_timesheets)
                .filter(
                    users.TimeSheet.user_id == body_id,
                    users.TimeSheet.weekday == timesheet_form.weekday.data,
                    users.TimeSheet.period == timesheet_form.period.data
                )
            )
        if user.role == constants.ROLE_DENTIST:
            TS = (
                TS.filter(
                    users.DentistTimeSheet.dental_unit_id ==
                    timesheet_form.dental_unit_id.data
                )
            )
        elif user.role == constants.ROLE_ASSISTANT:
            TS = (
                TS.filter(
                    users.AssistantTimeSheet.dentist_id ==
                        timesheet_form.dentist_id.data
                )
            )

        TS = TS.one_or_none()

        if not TS:
            values = { 
                f: getattr(timesheet_form, f).data
                for f in timesheet_fields 
            }
            values['user_id'] = user.id
            values['user_role'] = user.role
            if user.role == constants.ROLE_DENTIST:
                for f in dentist_timesheet_fields:
                    values[f] =\
                    getattr(timesheet_form, f).data

#                        [ values[f] =
#                            getattr(timesheet_form, f).data
#                            for f in dentist_timesheet_fields ]
                new_TS = users.DentistTimeSheet(**values)

            elif user.role == constants.ROLE_ASSISTANT:
                for f in assistant_timesheet_fields:
                    values[f] =\
                    getattr(timesheet_form, f).data
                    
#                        [ values[f] = 
#                            getattr(timesheet_form, f).data
#                            for f in assistant_timesheet_fields ]
                new_TS = users.AssistantTimeSheet(**values)

            else:
                new_TS = users.TimeSheet(**values)
            
            meta.session.add(new_TS)

        else:
            [ setattr(TS, f, 
                    getattr(timesheet_form, f).data)
                for f in timesheet_fields ]
            if user.role == constants.ROLE_DENTIST:
                [ setattr(TS, f,
                    getattr(timesheet_form, f).data)
                    for f in dentist_timesheet_fields ]
            elif user.role == constants.ROLE_ASSISTANT:
                [ setattr(TS, f,
                    getattr(timesheet_form, f).data)
                    for f in assistant_timesheet_fields ]

        meta.session.commit()

    except (ValueError, TypeError, IndexError):
        pass

    return redirect(url_for('update_user', body_id=body_id,
                                        form_to_display="time_sheet"))

   

@app.route('/update/timesheet?body_id=<int:body_id>', methods=['POST'])
def update_timesheet(body_id):

    timesheet_fields = [ 'weekday', 'period', 'begin', 'end' ]
    dentist_timesheet_fields = [ 'dental_unit_id' ]
    assistant_timesheet_fields = [ 'dentist_id' ]
    
    user = (
        meta.session.query(users.OdontuxUser)
            .filter(users.OdontuxUser.id == body_id)
            .one()
        )
    
    timesheet_form = generate_timesheet_form(user.role)
    
    for weekday in range(1,8):
        for period in constants.PERIODS.keys():
            if not timesheet_form[weekday][period].validate():
                continue
            try:
                begin = datetime.time(
                int(timesheet_form[weekday][period].begin.data.split(":")[0]),
                int(timesheet_form[weekday][period].begin.data.split(":")[1])
                )
                
                end = datetime.time(
                int(timesheet_form[weekday][period].end.data.split(":")[0]),
                int(timesheet_form[weekday][period].end.data.split(":")[1])
                )

                all_timesheets = with_polymorphic(users.TimeSheet, '*')
                TS = ( 
                    meta.session.query(all_timesheets)
                        .filter(
                            users.TimeSheet.user_id == body_id,
                            users.TimeSheet.weekday == weekday,
                            users.TimeSheet.period == period
                        )
                    )
                if user.role == constants.ROLE_DENTIST:
                    TS = (
                        TS.filter(
                            users.DentistTimeSheet.dental_unit_id ==
                            timesheet_form[weekday][period].dental_unit_id.data
                        )
                    )
                elif user.role == constants.ROLE_ASSISTANT:
                    TS = (
                        TS.filter(
                            users.AssistantTimeSheet.dentist_id ==
                                timesheet_form[weekday][period].dentist_id.data
                        )
                    )

                TS = TS.one_or_none()

                if not TS:
                    values = { 
                        f: getattr(timesheet_form[weekday][period], f).data
                        for f in timesheet_fields 
                    }
                    values['user_id'] = user.id
                    values['user_role'] = user.role
                    if user.role == constants.ROLE_DENTIST:
                        for f in dentist_timesheet_fields:
                            values[f] =\
                            getattr(timesheet_form[weekday][period], f).data

#                        [ values[f] =
#                            getattr(timesheet_form[weekday][period], f).data
#                            for f in dentist_timesheet_fields ]
                        new_TS = users.DentistTimeSheet(**values)

                    elif user.role == constants.ROLE_ASSISTANT:
                        for f in assistant_timesheet_fields:
                            values[f] =\
                            getattr(timesheet_form[weekday][period], f).data
                            
#                        [ values[f] = 
#                            getattr(timesheet_form[weekday][period], f).data
#                            for f in assistant_timesheet_fields ]
                        new_TS = users.AssistantTimeSheet(**values)

                    else:
                        new_TS = users.TimeSheet(**values)
                    
                    meta.session.add(new_TS)

                else:
                    [ setattr(TS, f, 
                            getattr(timesheet_form[weekday][period], f).data)
                        for f in timesheet_fields ]
                    if user.role == constants.ROLE_DENTIST:
                        [ setattr(TS, f,
                            getattr(timesheet_form[weekday][period], f).data)
                            for f in dentist_timesheet_fields ]
                    elif user.role == constants.ROLE_ASSISTANT:
                        [ setattr(TS, f,
                            getattr(timesheet_form[weekday][period], f).data)
                            for f in assistant_timesheet_fields ]

                meta.session.commit()

            except ValueError, TypeError:
                continue
    return redirect(url_for('update_user', body_id=body_id,
                                        form_to_display="time_sheet"))

@app.route('/dental_office/update?id=<int:body_id>'
            '&form_to_display=<form_to_display>/', methods=['GET', 'POST'])
def update_dental_office(body_id, form_to_display):
    """ """
    if not session['role'] == constants.ROLE_ADMIN:
        return redirect(url_for('index'))

    dental_office = meta.session.query(users.DentalOffice).filter(
                                        users.DentalOffice.id == body_id).one()

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
            setattr(user, f, b64encode(scrypt.encrypt(os.urandom(64),
                            getattr(password_form, f).data.encode("utf_8"), 
                            maxtime=0.5)))
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

@app.route('/delete/dental_office?id=<int:body_id>')
def delete_dental_office(body_id):
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for('list_dental_offices'))
   
    dental_office = meta.session.query(users.DentalOffice).filter(
                        users.DentalOffice.id == body_id).one_or_none()
    meta.session.delete(dental_office)
    meta.session.commit()
    return redirect(url_for('list_dental_offices'))


