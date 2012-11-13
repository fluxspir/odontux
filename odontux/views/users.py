# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/05
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import and_, or_
from odontux.models import meta, users, administration
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants

from odontux.views.log import index

from wtforms import (Form, IntegerField, TextField, PasswordField,
                    SelectField, BooleanField, TextAreaField,
                    validators)
from odontux.views import forms

# form fields list
general_fields = [ "username", "role", "title", "lastname", "firstname", 
                   "qualifications", "registration", "correspondence_name", 
                   "sex", "dob"]
info_fields = [ "status", "comments", "avatar_id", "display_order",
                "modified_by", "time_stamp" ]
password_fields = [ "password" ]

class OdontuxUserGeneralInfoForm(Form):
    username = TextField('username', [validators.Required(),
                         validators.Length(min=1, max=20)],
                         filters=[forms.lower_field])
    role = SelectField('role', choices=constants.ROLES_LIST, coerce=int)
    title = SelectField('title', choices=forms.title_list)
    lastname = TextField('lastname', [validators.Required(),
                            validators.Length(min=1, max=30,
                            message=_("Need to provide MD's lastname"))],
                            filters=[forms.upper_field])
    firstname = TextField('firstname', [validators.Length(max=30)],
                            filters=[forms.title_field])
    qualifications = TextField('qualifications', filters=[forms.title_field])
    registration = TextField('registration')
    correspondence_name = TextField('correspondence_name', 
                                    filters=[forms.upper_field])
    sex = BooleanField('Male')
    dob = forms.DateField('Date of Birth')
    status = BooleanField('status')
    comments = TextAreaField('comments')
    avatar_id = IntegerField('avatar_id', [validators.Optional()])
    display_order = IntegerField('display_order', [validators.Optional()])
    modified_by = IntegerField('modified_by', [validators.Optional()])
    time_stamp = forms.DateField("time_stamp")

class OdontuxUserPasswordForm(Form):
    password = PasswordField('password', [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField('Repeat Password')


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
    return render_template('list_users.html', odontuxusers=odontuxusers, 
                            roles=constants.ROLES_LIST,
                            role_admin=constants.ROLE_ADMIN)


@app.route('/add/user/', methods=['GET', 'POST'])
@app.route('/user/add/', methods=['GET', 'POST'])
def add_user():
    if session['role'] != constants.ROLE_ADMIN:
        return redirect(url_for("index"))

    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    password_form = OdontuxUserPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}
        for f in general_fields:
            values[f] = getattr(form, f).data
        for f in info_fields:
            values[f] = getattr(form, f).data

        new_odontuxuser = users.OdontuxUser(**values)
        meta.session.add(new_odontuxuser)
        
        address_args = {f: getattr(form, f).data for f in forms.address_fields}
        new_odontuxuser.addresses.append(administration.Address(
                                         **address_args))

        phone_args = {g: getattr(form, f).data for f,g in forms.phone_fields}
        new_odontuxuser.phones.append(administration.Phone(**phone_args))

        mail_args = {f: getattr(form, f).data for f in forms.mail_fields}
        new_odontuxuser.mails.append(administration.Mail(**mail_args))

        meta.session.commit()
        return redirect(url_for('list_users'))

    return render_template('/add_user.html/', 
                           gen_info_form=gen_info_form,
                           address_form=address_form,
                           phone_form=phone_form,
                           mail_form=mail_form,
                           password_form=password_form)


# Function for printing the user's updating page, and getting 
# general and information fields.
@app.route('/user/update_user/id=<int:user_id>/', methods=['GET', 'POST'])
def update_user(user_id):
    user = forms._get_body(user_id, "user")
    if not forms._check_body_perm(user, "user"):
        return redirect(url_for('list_users'))

    # For updating info of user, we're dealing with the form 
    form = OdontuxUserGeneralInfoForm(request.form)
    if request.method == 'POST' and form.validate():
        for f in general_fields:
            setattr(user, f, getattr(form, f).data)
        for f in info_fields:
            setattr(user, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('update_user', user_id=user_id))

    # When loading the whole update page, we use the form containing all fields
    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    password_form = OdontuxUserPasswordForm(request.form)
    return render_template('/update_user.html', user=user,
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            password_form=password_form,
                            role_admin=constants.ROLE_ADMIN, 
                            role_dentist=constants.ROLE_DENTIST)

@app.route('/user/update_user_password/id=<int:user_id>/', methods=['POST'])
def update_user_password(user_id):
    user = forms._get_body(user_id, body_type="user")
    if not forms._check_user_perm(user, body_type="user"):
        return redirect(url_for('list_users'))
    form = OdontuxUserPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        for f in password_fields:
            setattr(user, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))

@app.route('/user/update_user_address/id=<int:user_id>/', methods=['POST'])
def update_user_address(user_id):
    if forms.update_body_address(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))
        
@app.route('/user/add_user_address/id=<int:user_id>/', methods=['POST'])
def add_user_address(user_id):
    if forms.add_body_address(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))

@app.route('/user/update_user_phone/id=<int:user_id>/', methods=['POST'])
def update_user_phone(user_id):
    if forms.update_body_phone(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))
    

@app.route('/user/add_user_phone/id=<int:user_id>/', methods=['POST'])
def add_user_phone(user_id):
    if forms.add_body_phone(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))

@app.route('/user/delete_user_phone/id=<int:user_id>/', methods=['POST'])
def del_user_phone(user_id):
    if forms.del_body_phone(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_form('list_users'))

@app.route('/user/update_user_mail/id=<int:user_id>/', methods=['POST'])
def update_user_mail(user_id):
    if forms.update_body_mail(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))

@app.route('/user/add_user_mail/id=<int:user_id>/', methods=['POST'])
def add_user_mail(user_id):
    if forms.add_body_mail(user_id, "user"):
        return redirect(url_for("update_user", user_id=user_id))
    return redirect(url_for('list_users'))
