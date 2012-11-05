# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/05
# v0.5
# Licence BSD
#

from flask import render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, users, administration
from odontux.odonweb import app
from gettext import gettext as _

from odontux.views.log import index

from wtforms import Form, IntegerField, TextField, FormField, validators
from odontux.views.forms import EmailField, TelField, DateField

class OdontuxUserForm(Form):
    username = TextField('username', [validators.Required(),
                         validators.Length(min=1, max=20)])
    password = PasswordField('password', [validators.Required(),
                         validators.Length(min=4)])
    role = IntegerField('role', [validators.Required()])
    lastname = TextField('lastname', [validators.Required(),
                         validators.Length(min=1, max=30,
                         message=_("Need to provide MD's lastname"))])
    firstname = TextField('firstname', [validators.Length(max=30)])
    qualification = TextField('qualification')
    registration = TextField('registration')
    correspondence_name = TextField('correspondence_name')
    sex = BooleanField('sex')
    dob = DateField('dob')
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
    avatar_id = IntegerField('avatar_id')
    display_order = IntegerField('display_order')
    modified_by = IntegerField('modified_by')
    update_date = DateField("update_date")

@app.route('/odontux_user/')
@app.route('/user/')
def list_users():
    if request.form and request.form['role']
        try:
            odontuxusers = meta.session.query(users.OdontuxUser)\
            .filter(users.OdontuxUser.role == request.form['role']).all()
            return render_template('list_users.html', 
                                    odontuxusers=odontuxusers)
    odontuxusers = meta.session.query(users.OdontuxUser).all()
    return render_template('list_md.html', odontuxusers=odontuxusers)

@app.route('/add/user/', methods=['GET', 'POST'])
@app.route('/user/add/', methods=['GET', 'POST'])
def add_user():
    form = OdontuxUserForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}
        values['username'] = form.username.data
        values['password'] = form.password.data
        values['role'] = form.role.data
        if form.title.data:
            values['title'] = form.title.data
        values['lastname'] = form.lastname.data
        if form.firstname.data:
            values['firstname'] = form.firstname.data
        if form.role.data:
            values['role'] = form.role.data
        
        new_odontuxuser = users.OdontuxUser(**values)
        meta.session.add(new_odontuxuser)

        new_odontuxuser.addresses.append(administration.Address(
                            street = form.street.data,
                            building = form.building.data,
                            city = form.city.data,
                            county = form.county.data,
                            country = form.country.data
                            ))
        
        if form.phonenum.data:
            if not form.phonename.data:
                form.phonename.data = _("default")
            new_odontuxuser.phones.append(administration.Phone(
                        name = form.phonename.data,
                        number = form.phonenum.data
                        ))
        if form.email.data:
            new_odontuxuser.mails.append(administration.Mail(
                        email = form.email.data
                        ))
        meta.session.commit()

@app.route('/md/update_md/id=<int:md_id>/', methods=['GET', 'POST'])
def update_user(user_id):
    try:
        doctor = meta.session.query(md.MedecineDoctor).filter\
         (md.MedecineDoctor.id == md_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for(list_md))

    form = MedecineDoctorForm(request.form)

    if request.method == 'POST' and form.validate():
        fields = [ "lastname", "firstname" ]
        addressfields = ["street", "building", "city","county", "country",\
                        "update_date" ]
        phonefields = [ ("phonename", "name"), ("phonenum", "number") ]
        mailfields = [ "email" ]
        for f in fields:
            setattr(doctor, f, getattr(form, f).data)
        for f in addressfields:
            try:
                if doctor.addresses[-1]:
                    setattr(doctor.addresses[-1], f, getattr(form, f).data)
            except IndexError:
                doctor.addresses.append(administration.Address(
                            **{f: getattr(form, f).data}
                            ))
        for (f,g) in phonefields:
            try:
                if doctor.phones[-1]:
                    setattr(doctor.phones[-1], g, getattr(form, f).data)
            except IndexError:
                doctor.phones.append(administration.Phones(
                            **{g: getattr(form, f).data}
                            ))
        for f in mailfields:
            try:
                if doctor.mails[-1]:
                    setattr(doctor.mails[-1], f, getattr(form, f).data)
            except IndexError:
                doctor.mails.append(administration.Mail(
                            **{f: getattr(form, f).data}
                            ))
        meta.session.commit()
        return redirect(url_for('list_md'))
    return render_template('/update_md.html', form=form, doctor=doctor)
