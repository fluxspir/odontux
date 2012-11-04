# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/03
# v0.5
# Licence BSD
#

from flask import render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, md, administration
from odontux.odonweb import app
from gettext import gettext as _

from odontux.views.log import index

from wtforms import Form, IntegerField, TextField, FormField, validators
from odontux.views.forms import EmailField, TelField, DateField

class MedecineDoctorForm(Form):
    lastname = TextField('lastname', [validators.Required(),
                         validators.Length(min=1, max=30,
                         message=_("Need to provide MD's lastname"))])
    firstname = TextField('firstname', [validators.Length(max=30)])
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
    update_date = DateField("update_date")

@app.route('/medecine_doctor/')
@app.route('/md/')
def list_md():
    doctors = meta.session.query(md.MedecineDoctor).all()
    return render_template('list_md.html', doctors=doctors)

@app.route('/add/md/', methods=['GET', 'POST'])
@app.route('/md/add/', methods=['GET', 'POST'])
def add_md():
    form = MedecineDoctorForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}
        values['lastname'] = form.lastname.data
        if form.firstname.data:
            values['firstname'] = form.firstname.data
        
        new_medecine_doctor = md.MedecineDoctor(**values)
        meta.session.add(new_medecine_doctor)

        new_medecine_doctor.addresses.append(administration.Address(
                            street = form.street.data,
                            building = form.building.data,
                            city = form.city.data,
                            county = form.county.data,
                            country = form.country.data
                            ))
        
        if form.phonenum.data:
            if not form.phonename.data:
                form.phonename.data = _("default")
            new_medecine_doctor.phones.append(administration.Phone(
                        name = form.phonename.data,
                        number = form.phonenum.data
                        ))
        if form.email.data:
            new_medecine_doctor.mails.append(administration.Mail(
                        email = form.email.data
                        ))
        meta.session.commit()

@app.route('/md/update_md/id=<int:md_id>/', methods=['GET', 'POST'])
def update_md(md_id):
    try:
        doctor = meta.session.query(md.MedecineDoctor).filter\
         (md.MedecineDoctor.id == md_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for(list_md))

    form = MedecineDoctorForm(request.form)

    if request.method == 'POST' and form.validate():
#        field = [ "lastname", "firstname", "street", "building", "city",\
#                "county", "country", "email", "phonename", "phonenum",\
#                "update_date"]
#        for f in field:
#            if form.f.data != doctor.f:
#                doctor.f = form.f.data
        if form.lastname.data != doctor.lastname:
            doctor.lastname = form.lastname.data
        if form.firstname.data != doctor.firstname:
            doctor.firstname = form.firstname.data
        if form.phonename.data != doctor.phones[-1].name:
            doctor.phones[-1].name = form.phonename.data
        if form.phonenum.data != doctor.phones[-1].number:
            doctor.phones[-1].number = form.phonenum.data
        if form.email.data != doctor.mails[-1].email:
            doctor.mails[-1].email = form.email.data
        if form.street.data != doctor.addresses[-1].street:
            doctor.addresses[-1].street = form.street.data
        if form.building.data != doctor.addresses[-1].building:
            doctor.addresses[-1].building = form.building.data
        if form.city.data != doctor.addresses[-1].city:
            doctor.addresses[-1].city = form.city.data
        if form.postal_code.data != doctor.addresses[-1].postal_code:
            doctor.addresses[-1].postal_code = form.postal_code.data
        if form.county.data != doctor.addresses[-1].county:
            doctor.addresses[-1].county = form.county.data
        if form.country.data != doctor.addresses[-1].country:
            doctor.addresses[-1].country = form.country.data
        return redirect(url_for('list_md'))
    return render_template('/update_md.html', form=form, doctor=doctor)
