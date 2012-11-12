# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/03
# v0.5
# Licence BSD
#

from flask import render_template, request, redirect, url_for, session
import sqlalchemy
from odontux.models import meta, md, administration
from odontux.odonweb import app
from gettext import gettext as _

from odontux.views.log import index
from odontux import constants

from wtforms import Form, IntegerField, TextField, FormField, validators
from odontux.views import forms

class MedecineDoctorGeneralInfoForm(Form):
    lastname = TextField('lastname', [validators.Required(),
                         validators.Length(min=1, max=30,
                         message=_("Need to provide MD's lastname"))])
    firstname = TextField('firstname', [validators.Length(max=30)])
    address_id = TextField('address_id')
    update_date = forms.DateField("update_date")

@app.route('/medecine_doctor/')
@app.route('/md/')
def list_md():
    doctors = meta.session.query(md.MedecineDoctor).all()
    return render_template('list_md.html', doctors=doctors,
                           role_dentist=constants.ROLE_DENTIST,
                           role_nurse=constants.ROLE_NURSE,
                           role_assistant=constants.ROLE_ASSISTANT)

@app.route('/add/md/', methods=['GET', 'POST'])
@app.route('/md/add/', methods=['GET', 'POST'])
def add_md():
    if (session['role'] != constants.ROLE_DENTIST
    and session['role'] != constants.ROLE_NURSE
    and session['role'] != constants.ROLE_ASSISTANT):
        return redirect(url_for('list_md'))

    gen_info_form = MedecineDoctorGeneralInfoForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    
    if request.method == 'POST' and form.validate():
        values = {}
        values['lastname'] = form.lastname.data
        values['firstname'] = form.firstname.data
        
        new_medecine_doctor = md.MedecineDoctor(**values)
        meta.session.add(new_medecine_doctor)
        
        address_args = {f: getattr(form, f).data for f in forms.address_fields}
        new_medecine_doctor.addresses.append(administration.Address(
                                             **address_args))

        phone_args = {g: getattr(form, f).data for f,g in forms.phone_fields}
        new_medecine_doctor.phones.append(administration.Phone(**phone_args))

        mail_args = {f: getattr(form, f).data for f in forms.mail_fields}
        new_medecine_doctor.mails.append(administration.Mail(**mail_args))
                        
        meta.session.commit()
        return redirect(url_for('list_md'))

    return render_template("/add_md.html", 
                           gen_info_form=gen_info_form,
                           address_form=address_form,
                           phone_form=phone_form,
                           mail_form=mail_form)

def _get_doctor(md_id):
    try:
        doctor = meta.session.query(md.MedecineDoctor).filter\
                 (md.MedecineDoctor.id == md_id).one()
        return doctor
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('list_md'))

@app.route('/md/update_md/id=<int:md_id>/', methods=['GET', 'POST'])
def update_md(md_id):
    doctor = _get_doctor(md_id)
    if (session['role'] != constants.ROLE_DENTIST
    and session['role'] != constants.ROLE_NURSE
    and session['role'] != constants.ROLE_ASSISTANT):
        return redirect(url_for('list_md'))

    gen_info_form = MedecineDoctorGeneralInfoForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    
    if request.method == 'POST' and gen_info_form.validate():
        gen_info_fields = [ "lastname", "firstname" ]
        for f in fields:
            setattr(doctor, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('update_md', md_id=md_id))

    # Page for updating md :
    return render_template('/update_md.html', doctor=doctor,
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form,
                            role_dentist=constants.ROLE_DENTIST,
                            role_nurse=constants.ROLE_NURSE,
                            role_assistant=constants.ROLE_ASSISTANT)

@app.route('/md/update_md_address/id=<int:md_id>/', methods=['POST'])
def update_address_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.AddressForm(request.form)
    address_index = int(request.form['address_index'])
    if request.method == 'POST' and form.validate():
        for f in forms.address_fields:
            setattr(doctor.addresses[address_index], f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('update_md', md_id=md_id))

@app.route('/md/add_md_address/id=<int:md_id>/', methods=['POST'])
def add_address_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.AddressForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in forms.address_fields}
        doctor.addresses.append(administration.Address(**args))
        meta.session.commit()
        return redirect(url_for("update_md", md_id=md_id))

@app.route('/md/update_md_phone/id=<int:md_id>/', methods=['POST'])
def update_phone_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.PhoneForm(request.form)
    phone_index = int(request.form['phone_index'])
    if request.method == 'POST' and form.validate():
        for (f,g) in forms.phone_fields:
            setattr(doctor.phones[phone_index], g, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_md", md_id=md_id))

@app.route('/md/add_md_phone/id=<int:md_id>/', methods=['POST'])
def add_phone_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.PhoneForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {g: getattr(form, f).data for f,g in forms.phone_fields}
        doctor.phones.append(administration.Phone(**args))
        meta.session.commit()
        return redirect(url_for("update_md", md_id=md_id))

@app.route('/md/update_md_mail/id=<int:md_id>/', methods=['POST'])
def update_mail_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.MailForm(request.form)
    mail_index = int(request.form["mail_index"])
    if request.method == 'POST' and form.validate():
        for f in forms.mail_fields:
            setattr(doctor.mails[mail_index], f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for("update_md", md_id=md_id))

@app.route('/md/add_md_mail/id=<int:md_id>/', methods=['POST'])
def add_mail_md(md_id):
    doctor = _get_doctor(md_id)
    form = forms.MailForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in forms.mail_fields}
        doctor.mails.append(administration.Mail(**args))
        meta.session.commit()
        return redirect(url_for("update_md", md_id=md_id))
