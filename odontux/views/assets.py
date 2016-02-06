# -*- coding: utf-8 -*-
# Franck Labadille
# 2016-02-02
# v0.6
# Licence BSD
#

import pdb
import os

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import and_, or_
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField, HiddenField,
                    SelectField, BooleanField, TextAreaField, DecimalField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, assets, administration
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.forms import DateField
from odontux.views.log import index

class AssetProviderForm(Form):
    asset_provider_id = HiddenField(_('id'))
    name = TextField(_('Asset provider name'), [validators.Required(
                                message=_("Provider's name required")),
                                validators.Length(max=30, 
                                message=_('Max : 30 characters'))],
                                filters=[forms.title_field])
    active = BooleanField(_('Active'))

class AssetCategoryForm(Form):
    asset_category_id = HiddenField(_('id'))
    barcode = TextField(_('Barcode'), [validators.Optional()])
    brand = TextField(_('Brand'), [validators.Required(
                                        message=_("Brand's name required"))])
    commercial_name = TextField(_('Commercial name'), [validators.required(
                                    message=_('Commercial name required'))])
    description = TextAreaField(_('Description'), [validators.Optional()])
    #type = SelectField(_('Type'))
    type = SelectField(_('Type'), description='ChangementType()')

class DeviceCategoryForm(Form):
    device_category_id = HiddenField(_('id'))
    sterilizable = BooleanField(_('Sterilizable'))

class MaterialCategoryForm(Form):
    material_category_id = HiddenField(_('id'))
    material_type = TextField(_("Utilization's family"), 
                                                    [validators.Optional()])
    order_threshold = DecimalField(_("Order's threshold"), 
                                                    [validators.Optional()])
    unity = SelectField(_('Unity'), coerce=int)
    initial_quantity = DecimalField(_("Quantity of product"), 
                                                    [validators.Optional()])
    automatic_decrease = DecimalField(_('Automatic decrease'), 
                                                    [validators.Optional()])

class AssetForm(Form):
    asset_id  = HiddenField(_('id'))
    provider_id = SelectField(_('Provider'), coerce=int)
    asset_category_id = SelectField(_('Asset Category'), coerce=int)
    acquisition_date = DateField(_('Acquisition Date'))
    new = BooleanField(_('Asset new'))
    user = SelectField(_("Dentist owner"), coerce=int)
    office = SelectField(_("Office_where it is"), coerce=int)
    type = SelectField(_('Type'), description='ChangementType()')

class DeviceForm(Form):
    device_id = HiddenField(_('id'))
    lifetime_expected = DecimalField(_('Lifetime in years'), 
                                                    [validators.Optional()])

class MaterialForm(Form):
    material_id = HiddenField(_('id'))
    used_in_traceabily_of = HiddenField(_('Use in traceability of'))
    actual_quantity = DecimalField(_('Actual Quantity'),
                                                    [validators.Optional()])
    expiration_date = DateField(_('Expiration Date'),
                                                    [validators.Optional()])
    expiration_alert = DecimalField(_('Expiration Alert'),
                                                    [validators.Optional()])
    start_of_use = DateField(_('Start of Use'), [validators.Optional()])
    end_of_use = DateField(_('End of Use'), [validators.Optional()])
    end_use_reason = SelectField(_('Reason to end of use'), coerce=int)


@app.route('/provider/add/', methods=['GET', 'POST'])
@app.route('/add/provider/', methods=['GET', 'POST'])
def add_provider():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    general_form = AssetProviderForm(request.form)
    address_form = forms.AddressForm(request.form)
    phone_form = forms.PhoneForm(request.form)
    mail_form = forms.MailForm(request.form)
    general_form.active.data = True  # we want that a new provider that we 
                                        # add to be active by default.

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
        for f in [ "name", "active" ]:
            setattr(provider, f, getattr(general_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_provider', body_id=provider.id,
                                    form_to_display="general_form"))
            

    for f in [ "name", "active" ]:
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

    assets_list = meta.session.query(assets.Asset).all()
    return render_template('list_assets.html', assets_list=assets_list)

@app.route('/list_asset_category?assets_type=<assets_type>/')
def list_asset_category(assets_type):
    checks.quit_patient_file()
    checks.quit_appointment()
    
    if assets_type == "all":
        asset_categories = meta.session.query(assets.AssetCategory).all()
    return render_template('list_assets.html', assets_type=assets_type)

@app.route('/add/asset_category/', methods=['POST', 'GET'])
def add_asset_category():

    def get_asset_category_type_choices():
        return [ ( "device_category", _("Device") ), 
                ( "material_category", _("Material") ) ]
    def get_material_cat_unity_choices():
        return [ ( 0, _("pieces") ), ( 1, _("volume") ), (2, _("weight") ) ]

    def get_asset_cat_field_list():
        return [ "barcode", "brand", "commercial_name",
                    "description", "type" ]

    def get_device_cat_field_list():
        return [ "sterilizable" ]

    def get_material_cat_field_list():
        return [ "material_type", "order_threshold", "unity", 
                "initial_quantity", "automatic_decrease" ]

    def verify_asset_cat_already_in_db(new_asset):
        asset_cat_in_db = meta.session.query(assets.AssetCategory).filter(
                    assets.AssetCategory.barcode == new_asset.barcode.data
                                                            ).one_or_none()
        if not asset_cat_in_db:
            asset_cat_in_db = meta.session.query(assets.AssetCategory
                    ).filter(and_(
                    assets.AssetCategory.brand == new_asset.brand.data,
                    assets.AssetCategory.commercial_name == 
                    new_asset.brand.data
                    )).one_or_none()
        return asset_cat_in_db

    def add_device_category(asset_form, device_form):
        if asset_form.validate() and device_form.validate():
            values = {f: getattr(asset_form, f).data
                    for f in get_asset_cat_field_list()}
            for f in get_device_cat_field_list():
                values[f] = getattr(device_form, f).data
            new_asset_cat = assets.DeviceCategory(**values)
            meta.session.add(new_asset_cat)
            meta.session.commit()
            return redirect(url_for('list_asset_category'))

    def add_material_category(asset_form, material_form):
        if asset_form.validate() and material_form.validate(): 
            values = {f: getattr(asset_form, f).data
                    for f in get_asset_cat_field_list()}
            for f in get_material_cat_field_list():
                values[f] = getattr(material_form, f).data
            new_material_cat = assets.MaterialCategory(**values)
            meta.session.add(new_material_cat)
            meta.session.commit()
            return redirect(url_for('list_asset_category'))

    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    asset_category_form = AssetCategoryForm(request.form)
    asset_category_form.type.choices = get_asset_category_type_choices()
    device_category_form = DeviceCategoryForm(request.form)
    material_category_form = MaterialCategoryForm(request.form)
    material_category_form.unity.choices = get_material_cat_unity_choices()
 
    asset_cat_in_db = verify_asset_cat_already_in_db(asset_category_form)
    if asset_cat_in_db:
        return redirect(url_for('index'))
        #return redirect(url_for('add_asset', asset_cat_in_db ))
    
    if ( request.method == 'POST' 
                    and asset_category_form.type.data == "device_category"):
        add_device_category(asset_category_form, device_category_form)

    if ( request.method == 'POST' 
                    and asset_category_form.type.data == "material_category"):
        add_material_category(asset_category_form, material_category_form)

    return render_template('add_asset_category.html',
                            asset_form=asset_category_form,
                            device_form=device_category_form,
                            material_form=material_category_form)


@app.route('/add/asset/')
def add_asset():
    pass
