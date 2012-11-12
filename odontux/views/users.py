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

from wtforms import (Form, IntegerField, TextField, FormField, PasswordField,
                    SelectField, BooleanField, TextAreaField, RadioField,
                    validators)
from odontux.views import forms

# form fields list
general_fields = [ "username", "role", "title", "lastname", "firstname", 
                   "qualifications", "registration", "correspondence_name", 
                   "sex", "dob"]
info_fields = [ "status", "comments", "avatar_id", "display_order",
                "modified_by", "time_stamp" ]
address_fields = ["street", "building", "city","county", "country" ]
phone_fields = [ ("phonename", "name"), ("phonenum", "number") ]
mail_fields = [ "email" ]
password_fields = [ "password" ]
# form choices list
title_list = [ (_("Mr"), _("Mr")), (_("Mme"), _("Mme")),
                (_("Mlle"), _("Mlle")), (_("Dr"), _("Dr")) ]


class OdontuxUserGeneralInfoForm(Form):
    username = TextField('username', [validators.Required(),
                         validators.Length(min=1, max=20)],
                         filters=[forms.lower_field])
    role = SelectField('role', choices=constants.ROLES_LIST, coerce=int)
    title = SelectField('title', choices=title_list)
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


class OdontuxUserPasswordForm(Form):
    password = PasswordField('password', [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField('Repeat Password')

class OdontuxUserPhoneForm(Form):
    phonename = TextField('phonename', validators=[validators.Optional()])
    phonenum = forms.TelField('phonenum', [validators.Optional()])

class OdontuxUserAddressForm(Form):
    address_id = TextField('address_id')
    street = TextField('street', validators=[validators.Optional(),
                                 validators.Length(max=50, message=_("""Number
                                 and street must be less than 50 characters 
                                 please"""))])
    building = TextField('building', validators=[validators.Optional(), 
                                     validators.Length(max=50)])
    city = TextField('city', validators=[validators.Optional(),
                             validators.Length(max=25,
                             message=_("City's name"))], 
                             filters=[forms.title_field])
    postal_code = IntegerField('postal_code', [validators.Optional()])
    county = TextField('county', validators=[validators.Optional(), 
                                  validators.Length(max=15)], 
                                 filters=[forms.title_field])
    country = TextField('country', validators=[validators.Optional(),
                                   validators.Length(max=15)],
                                   filters=[forms.title_field])

class OdontuxUserMailForm(Form):
    email = forms.EmailField('email', validators=[validators.Optional(),
                                      validators.Email()],
                                      filters=[forms.lower_field])

    time_stamp = forms.DateField("time_stamp")

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

    form = OdontuxUserForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}

        for f in general_fields:
            values[f] = getattr(form, f).data
        for f in info_fields:
            values[f] = getattr(form, f).data

        new_odontuxuser = users.OdontuxUser(**values)
        meta.session.add(new_odontuxuser)

        for f in address_fields:
            new_odontuxuser.addresses.append(administration.Address(
                    **{f: getattr(form, f).data}
                    ))
        for (f,g) in phone_fields:
            new_odontuxuser.phones.append(administration.Phone(
                    **{g: getattr(form, f).data}
                    ))
        for f in mail_fields:
            new_odontuxuser.mails.append(administration.Mail(
                    **{f: getattr(form, f).data}
                    ))

        meta.session.commit()
        return redirect(url_for('list_users'))
    return render_template('/add_user.html/', form=form)

# verify the user is allowed to update
def _check_user_perm(user):
    if session['role'] != constants.ROLE_ADMIN \
    and session['username'] != user.username:
        return False
    return True

# Get user information in the database
def _get_user(user_id):
    try:
        user = meta.session.query(users.OdontuxUser).filter\
            (users.OdontuxUser.id == user_id).one()
        return user
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('list_users'))


# Function for printing the user's updating page, and getting 
# general and information fields.
@app.route('/user/update_user/id=<int:user_id>/', methods=['GET', 'POST'])
def update_user(user_id):
    user = _get_user(user_id) 
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))

    # For updating info of user, we're dealing with the form 
    form = OdontuxUserGeneralInfoForm(request.form)
    if request.method == 'POST' and form.validate():
        for f in general_fields:
            setattr(user, f, getattr(form, f).data)
        for f in info_fields:
            setattr(user, f, getattr(form, f).data)
        meta.session.commit()

    # When loading the whole update page, we use the form containing all fields
    gen_info_form = OdontuxUserGeneralInfoForm(request.form)
    address_form = OdontuxUserAddressForm(request.form)
    phone_form = OdontuxUserPhoneForm(request.form)
    mail_form = OdontuxUserMailForm(request.form)
    password_form = OdontuxUserPasswordForm(request.form)
    return render_template('/update_user.html', user=user,
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            password_form=password_form,
                            role_admin=constants.ROLE_ADMIN, 
                            role_dentist=constants.ROLE_DENTIST)

@app.route('/user/update_user_address/id=<int:user_id>/', methods=['POST'])
def update_user_address(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserAddressForm(request.form)
    address_id = int(request.form["address_id"])
    if request.method == 'POST' and form.validate():
        for f in address_fields:
            setattr(user.addresses[address_id], f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))
        
@app.route('/user/add_user_address/id=<int:user_id>/', methods=['POST'])
def add_user_address(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserAddressForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in phone_fields}
        user.addresses.append(users.OdontuxUser(**(args)))
        meta.session.commit()

@app.route('/user/update_user_phone/id=<int:user_id>/', methods=['POST'])
def update_user_phone(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserPhoneForm(request.form)
    phone_id = int(request.form["phone_id"])
    if request.method == 'POST' and form.validate():
        for (f,g) in phone_fields:
            setattr(user.phones[phone_id], g, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))
    

@app.route('/user/add_user_phone/id=<int:user_id>/', methods=['POST'])
def add_user_phone(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserPhoneForm(request.form)
    if request.method == 'POST' and form.validate():
        args = { g: getattr(form, f).data for f, g in phone_fields }
        user.phones.append(administration.Phone(**args))
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))

@app.route('/user/delete_user_phone/id=<int:user_id>/', methods=['POST'])
def del_user_phone(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_form('list_users'))
    form = OdontuxUserPhoneForm(request.form)
    phone_id = int(request.form["phone_id"])
    if request.method == 'POST' and form.validate():
        try:
            phone = meta.session.query(administration.Phone).filter(and_(
                        administration.Phone.name == form.phonename.data,
                        administration.Phone.number == form.phonenum.data
                        )or_(
                        administration.Phone.id == phone_id
                        )).one()
            meta.session.delete(phone)
            meta.session.commit()
            return redirect(url_for("update_user", user_id=user_id))
        except:
            raise Exception("phone delete problem")

@app.route('/user/update_user_mail/id=<int:user_id>/', methods=['POST'])
def update_user_mail(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserMailForm(request.form)
    mail_id = int(request.form["mail_id"])
    if request.method == 'POST' and form.validate():
        for f in mail_fields:
            setattr(user.mails[mail_id], f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))

@app.route('/user/add_user_mail/id=<int:user_id>/', methods=['POST'])
def add_user_mail(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserMailForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in mail_fields }
        user.mails.append(administration.Mail(**(args)))
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))

@app.route('/user/update_user_password/id=<int:user_id>/', methods=['POST'])
def update_user_password(user_id):
    user = _get_user(user_id)
    if not _check_user_perm(user):
        return redirect(url_for('list_users'))
    form = OdontuxUserPasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        for f in password_fields:
            setattr(user, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_user", user_id=user_id))
