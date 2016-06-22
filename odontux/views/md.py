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

from odontux import constants, checks
from odontux.views import forms
from odontux.views.log import index

from wtforms import (Form, IntegerField, TextField, FormField, HiddenField,
                    DateField, validators)

class MedecineDoctorGeneralInfoForm(Form):
    md_id = HiddenField('id')
    lastname = TextField('lastname', [validators.Required(),
                         validators.Length(min=1, max=30,
                         message=_("Need to provide MD's lastname"))])
    firstname = TextField('firstname', [validators.Length(max=30)])
    update_date = DateField(_("update_date"), [validators.Optional()])

def get_gen_info_field_list():
    return ['lastname', "firstname" ]

@app.route('/medecine_doctor/')
@app.route('/md/')
def list_md():
    doctors = meta.session.query(md.MedecineDoctor).order_by(
                md.MedecineDoctor.lastname).all()
    return render_template('list_md.html', doctors=doctors)

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
    
    if request.method == 'POST' and gen_info_form.validate():

        medecine_doctor = checks.is_body_already_in_database(
                                            gen_info_form, "md")
        values = {}
        values['lastname'] = gen_info_form.lastname.data
        values['firstname'] = gen_info_form.firstname.data
        
        new_medecine_doctor = md.MedecineDoctor(**values)
        meta.session.add(new_medecine_doctor)
        
        address_args = {f: getattr(address_form, f).data 
                        for f in forms.address_fields}
        if any(address_args.values()):
            new_medecine_doctor.addresses.append(administration.Address(
                                                             **address_args))

        phone_args = {g: getattr(phone_form, f).data 
                      for f,g in forms.phone_fields}
        if any(phone_args.values()):
            new_medecine_doctor.phones.append(administration.Phone(
                                                                **phone_args))

        mail_args = {f: getattr(mail_form, f).data for f in forms.mail_fields}
        if any(mail_args.values()):
            new_medecine_doctor.mails.append(administration.Mail(**mail_args))
                        
        meta.session.commit()
        return redirect(url_for('list_md'))

    return render_template("/add_md.html", 
                           gen_info_form=gen_info_form,
                           address_form=address_form,
                           phone_form=phone_form,
                           mail_form=mail_form)

@app.route('/md/update_md?<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['GET', 'POST'])
def update_md(body_id, form_to_display):
    doctor = forms._get_body(body_id, "md")
    if (session['role'] != constants.ROLE_DENTIST
    and session['role'] != constants.ROLE_NURSE
    and session['role'] != constants.ROLE_ASSISTANT):
        return redirect(url_for('list_md'))

    gen_info_form = MedecineDoctorGeneralInfoForm(request.form)
   
    if request.method == 'POST' and gen_info_form.validate():
        gen_info_fields = [ "lastname", "firstname" ]
        for f in get_gen_info_field_list():
            setattr(doctor, f, getattr(gen_info_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="gen_info"))

    for f in get_gen_info_field_list():
        getattr(gen_info_form, f).data = getattr(doctor, f)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    return render_template('/update_md.html', doctor=doctor,
                            gen_info_form=gen_info_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form)

@app.route('/md/delete_md?id=<int:body_id>')
def delete_md(body_id):
    doctor = forms._get_body(body_id, "md")
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('list_md'))
    meta.session.delete(doctor)
    meta.session.commit()
    return redirect(url_for('list_md'))

@app.route('/md/update_md_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_md_address(body_id, form_to_display):
    if forms.update_body_address(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_md'))

@app.route('/md/add_md_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_md_address(body_id, form_to_display):
    if forms.add_body_address(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_md'))

@app.route('/md/delete_md_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_md_address(body_id, form_to_display):
    if forms.delete_body_address(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="address"))
    return redirect(url_for('list_md'))

@app.route('/md/update_md_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_md_phone(body_id, form_to_display):
    if forms.update_body_phone(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_for('list_md'))

@app.route('/md/add_md_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_md_phone(body_id, form_to_display):
    if forms.add_body_phone(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_for('list_md'))

@app.route('/md/delete_md_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_md_phone(body_id, form_to_display):
    if forms.delete_body_phone(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="phone"))
    return redirect(url_for('list_md'))

@app.route('/md/update_md_mail?id=<int:body_id>/', methods=['POST'])
def update_md_mail(body_id, form_to_display):
    if forms.update_body_mail(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_for('list_md'))

@app.route('/md/add_md_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_md_mail(body_id, form_to_display):
    if forms.add_body_mail(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_for('list_md'))

@app.route('/md/delete_md_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_md_mail(body_id, form_to_display):
    if forms.delete_body_mail(body_id, "md"):
        return redirect(url_for('update_md', body_id=body_id,
                                form_to_display="mail"))
    return redirect(url_for('list_md'))


