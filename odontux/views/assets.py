# -*- coding: utf-8 -*-
# Franck Labadille
# 2016-02-02
# v1.0
# Licence BSD
#

import pdb
import os

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import and_, or_
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField,
                    SelectField, BooleanField, TextAreaField, HiddenField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, assets, administration
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.log import index

class AssetProviderForm(Form):
    name = TextField(_('Asset provider name'), [validators.Required(
                                message=_("Provider's name required")),
                                validators.Length(max=30, 
                                message=_('Max : 30 characters'))],
                                filters=[forms.title_field])
    active = BooleanField(_('Active'))

def get_general_form_field_list():
    return [ "name", "active" ]


@app.route('/provider/add/', methods=['GET', 'POST'])
@app.route('/add/provider/', methods=['GET', 'POST'])
def add_provider():
    if (session['role'] == 0 or session['role'] == 1
        or session['role'] == 2 or session['role'] == 3):

        checks.quit_patient_file()
        checks.quit_appointment()
        general_form = AssetProviderForm(request.form)
        address_form = forms.AddressForm(request.form)
        phone_form = forms.PhoneForm(request.form)
        mail_form = forms.MailForm(request.form)
        general_form.active.data = True

        if (request.method == 'POST' 
            and general_form.validate()
            and address_form.validate()
            and phone_form.validate()
            and mail_form.validate()):

            provider = checks.is_body_already_in_database(general_form, 
                                                            "provider")
            if provider:
                return redirect(url_for('update_provider'))
            values = {f: getattr(general_form, f).data
                        for f in get_general_form_field_list()}
            new_provider = assets.AssetProvider(**values)
            meta.session.add(new_provider)
            meta.session.commit()

            address_args = {f: getattr(address_form, f).data
                        for f in forms.address_fields}
            new_provider.addresses.append(
                                        administration.Address(**address_args))
            meta.session.commit()

            phone_args = {g: getattr(phone_form, f).data
                        for f,g in forms.phone_fields}
            new_provider.phones.append(administration.Phone(**phone_args))
            meta.session.commit()

            mail_args = {f: getattr(mail_form, f).data 
                                for f in forms.mail_fields}
            new_provider.mails.append(administration.Mail(**mail_args))
            meta.session.commit()
            return redirect(url_for('list_providers'))

        return render_template('add_provider.html',
                                general_form=general_form,
                                address_form=address_form,
                                phone_form=phone_form,
                                mail_form=mail_form)
    return redirect(url_for('index'))

@app.route('/list_providers/')
def list_providers():
    checks.quit_patient_file()
    checks.quit_appointment()
    
    providers = meta.session.query(assets.AssetProvider).all()
    return render_template('list_providers.html', providers=providers)

@app.route('/update/provider?id=<int:body_id>&'
            'form_to_display=<form_to_display>/', methods=['GET', 'POST'])
def update_provider(body_id, form_to_display):
    checks.quit_patient_file()
    checks.quit_appointment()

    provider = forms._get_body(body_id, "provider")
    if not forms._check_body_perm(provider, "provider"):
        return redirect(url_for('list_providers'))

    if session['role'] != 0:
        return redirect(url_for('list_providers'))

    general_form = AssetProviderForm(request.form)
    provider = meta.session.query(assets.AssetProvider).filter(
                            assets.AssetProvider.id == body_id).one()
    
    if request.method == "POST" and general_form.validate():
        for f in get_general_form_field_list():
            setattr(provider, f, getattr(general_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_provider', body_id=provider.id,
                                    form_to_display="general_form"))
            

    for f in get_general_form_field_list():
        getattr(general_form, f).data = getattr(provider, f)

    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)

    return render_template('update_provider.html', 
                            provider=provider,
                            form_to_display=general_form,
                            general_form=general_form,
                            address_form=address_form,
                            phone_form=phone_form,
                            mail_form=mail_form)


@app.route('/provider/update_provider_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_provider_address(body_id, form_to_display):
    if forms.update_body_address(body_id, "provider"):
        return redirect(url_for("update_provider", 
                                 body_id=body_id,
                                 form_to_display="address"))
    return redirect(url_for('list_providers'))
 
@app.route('/provider/add_provider_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_provider_address(body_id, form_to_display):
    if forms.add_body_address(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id, 
                                 form_to_display="address"))
    return redirect(url_for('list_providers'))

@app.route('/provider/delete_provider_address?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_provider_address(body_id, form_to_display):
    if forms.delete_body_address(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="address"))
    return redirect(url_for('list_providers'))
 
@app.route('/provider/update_provider_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_provider_phone(body_id, form_to_display):
    if forms.update_body_phone(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_providers'))
 
@app.route('/provider/add_provider_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_provider_phone(body_id, form_to_display):
    if forms.add_body_phone(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_for('list_providers'))

@app.route('/provider/delete_provider_phone?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_provider_phone(body_id, form_to_display):
    if forms.delete_body_phone(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="phone"))
    return redirect(url_form('list_providers'))

@app.route('/provider/update_provider_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def update_provider_mail(body_id, form_to_display):
    if forms.update_body_mail(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_providers'))

@app.route('/provider/add_provider_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def add_provider_mail(body_id, form_to_display):
    if forms.add_body_mail(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_providers'))

@app.route('/provider/delete_provider_mail?id=<int:body_id>'
           '&form_to_display=<form_to_display>/', methods=['POST'])
def delete_provider_mail(body_id, form_to_display):
    if forms.delete_body_mail(body_id, "provider"):
        return redirect(url_for("update_provider", body_id=body_id,
                                 form_to_display="mail"))
    return redirect(url_for('list_providers'))

@app.route('/my_assets/')
def my_assets():
    checks.quit_patient_file()
    checks.quit_appointment()

    return render_template('my_assets.html')


@app.route('/list_assets?assets_type=<assets_type>/')
def list_assets(assets_type):
    checks.quit_patient_file()
    checks.quit_appointment()

    assets = meta.session.query(assets.Asset).all()
    return render_template('list_assets.html', assets=assets)


