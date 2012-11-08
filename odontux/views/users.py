# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/05
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, users, administration
from odontux.odonweb import app
from gettext import gettext as _

from odontux import constants

from odontux.views.log import index

from wtforms import (Form, IntegerField, TextField, FormField, PasswordField,
                    SelectField, BooleanField, TextAreaField, RadioField,
                    validators)
from odontux.views.forms import EmailField, TelField, DateField

general_fields = [ "username", "password", "role", "title",\
                    "lastname", "firstname", "qualifications",\
                    "registration", "correspondence_name", "sex", "dob"]
info_fields = [ "status", "comments", "avatar_id", "display_order",\
                "modified_by", "time_stamp" ]
address_fields = ["street", "building", "city","county", "country" ]
phone_fields = [ ("phonename", "name"), ("phonenum", "number") ]
mail_fields = [ "email" ]


class OdontuxUserForm(Form):
    # Create the list of role availables :
    title_list = [ (_("Mr"), _("Mr")), (_("Mme"), _("Mme")),\
                   (_("Dr"), _("Dr")) ]
    # Begin Form                     
    username = TextField('username', [validators.Required(),
                            validators.Length(min=1, max=20)])
    password = PasswordField('password', [validators.Required(),
                        validators.Length(min=4), 
                        validators.EqualTo('confirm', message="Password must\
                        match")])
    confirm = PasswordField('Repeat Password')
    role = SelectField('role', choices=constants.ROLES_LIST, coerce=int)
    title = SelectField('title', choices=title_list)
    lastname = TextField('lastname', [validators.Required(),
                            validators.Length(min=1, max=30,
                            message=_("Need to provide MD's lastname"))])
    firstname = TextField('firstname', [validators.Length(max=30)])
    qualifications = TextField('qualifications')
    registration = TextField('registration')
    correspondence_name = TextField('correspondence_name')
    sex = BooleanField('Male')
    dob = DateField('Date of Birth')
    status = BooleanField('status')
    comments = TextAreaField('comments')
    phonename = TextField('phonename', [validators.Length(max=15)])
    phonenum = TelField('phonenum')
    address_id = TextField('address_id')
    street = TextField('street', [validators.Length(max=50, message=_("""Number
    and street must be less than 50 characters please"""))])
    building = TextField('building', [validators.Length(max=50)])
    city = TextField('city', [validators.Length(max=25, message=_("City's name"
    ))])
    postal_code = IntegerField('postal_code')
    county = TextField('county', [validators.Length(max=15)])
    country = TextField('country', [validators.Length(max=15)])
    email = EmailField('email', [validators.Email()])
    avatar_id = IntegerField('avatar_id', [validators.Optional()])
    display_order = IntegerField('display_order', [validators.Optional()])
    modified_by = IntegerField('modified_by', [validators.Optional()])
    time_stamp = DateField("time_stamp")

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

@app.route('/user/update_user/id=<int:user_id>/', methods=['GET', 'POST'])
def update_user(user_id):
    try:
        user = meta.session.query(users.OdontuxUser).filter\
         (users.OdontuxUser.id == user_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('list_users'))

    if session['role'] != ROLE_ADMIN \
    and session['username'] != user.username:
        return redirect(url_for('list_users'))

    form = OdontuxUserForm(request.form)

    if request.method == 'POST' and form.validate():
        for f in fields:
            setattr(user, f, getattr(form, f).data)
        for f in addressfields:
            if doctor.addresses:
                setattr(doctor.addresses[-1], f, getattr(form, f).data)
            else:                
                doctor.addresses.append(administration.Address(
                            **{f: getattr(form, f).data}
                            ))
        for (f,g) in phonefields:
            if doctor.phones[-1]:
                setattr(doctor.phones[-1], g, getattr(form, f).data)
            else:
                doctor.phones.append(administration.Phones(
                            **{g: getattr(form, f).data}
                            ))
        for f in mailfields:
            if doctor.mails[-1]:
                setattr(doctor.mails[-1], f, getattr(form, f).data)
            else:
                doctor.mails.append(administration.Mail(
                            **{f: getattr(form, f).data}
                            ))
        meta.session.commit()
        return redirect(url_for('list_md'))
    return render_template('/update_md.html', form=form, doctor=doctor)
