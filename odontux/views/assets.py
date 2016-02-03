# -*- coding: utf-8 -*-
# Franck Labadille
# 2016-02-02
# v1.0
# Licence BSD
#

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

def get_name_form_field_list():
    return [ "name" ]


@app.route('/provider/add/', methods=['GET', 'POST'])
@app.route('/add/provider/', methods=['GET', 'POST'])
def add_provider():
    if (session['role'] == 0
        or session['role'] == 1
        or session['role'] == 2
        or session['role'] == 3):

        checks.quit_patient_file()
        name_form = AssetProviderForm(request.form)
        address_form = forms.AddressForm(request.form)
        phone_form = forms.PhoneForm(request.form)
        mail_form = forms.MailForm(request.form)

        if (request.method == 'POST' 
            and name_form.validate()
            and address_form.validate()
            and phone_form.validate()
            and mail_form.validate()):

            provider = checks.is_body_already_in_database(name_form, 
                                                            "provider")
            if provider:
                return redirect(url_for('update_provider'))
            values = {f: getattr(name_form, f).data
                        for f in get_name_form_field_list()}
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
            return redirect(url_for('add_provider'))

        return render_template('add_provider.html',
                                name_form=name_form,
                                address_form=address_form,
                                phone_form=phone_form,
                                mail_form=mail_form)

@app.route('/update/provider?provider_id=<provider_id>/', 
                                    methods=['GET', 'POST'])
def update_provider(provider_id):
    pass

@app.route('/my_assets/')
def my_assets():
    checks.quit_patient_file()
    checks.quit_appointment()

    return render_template('my_assets.html')

@app.route('/list_providers/')
def list_providers():
    checks.quit_patient_file()
    checks.quit_appointment()
    
    providers = meta.session.query(assets.AssetProvider).all()
    return render_template('list_providers.html', providers=providers)

@app.route('/list_assets?assets_type=<assets_type>/')
def list_assets(assets_type):
    pass

