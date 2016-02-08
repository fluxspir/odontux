# -*- coding: utf-8 -*-
# Franck Labadille
# 2016-02-02
# v0.6
# Licence BSD
#

import pdb
import datetime
import os

from flask import session, render_template, request, redirect, url_for, jsonify
import sqlalchemy
from sqlalchemy import and_, or_
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField, HiddenField,
                    SelectField, BooleanField, TextAreaField, DecimalField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, assets, administration, users
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.forms import DateField
from odontux.views.log import index

def last_user_asset():
    try:
        return meta.session.query(assets.Asset).order_by(
                                    assets.Asset.id.desc()).first().user_id
    except AttributeError:
        return 1

def last_office_asset():
    try:
        return meta.session.query(assets.Asset).order_by(
                                    assets.Asset.id.desc()).first().office_id
    except AttributeError:
        return 1

def last_asset_provider():
    try:
        return meta.session.query(assets.Asset).order_by(
                                    assets.Asset.id.desc()).first().provider_id
    except AttributeError:
        return 1

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
    provider_id = SelectField(_('Provider'), coerce=int,
                                                default=last_asset_provider())
    #asset_category_id = SelectField(_('Asset Category'), coerce=int)
    acquisition_date = DateField(_('Acquisition Date'))
    acquisition_price = DecimalField(_('Acquisition Price'))
    new = BooleanField(_('Asset new'))
    user_id = SelectField(_("Dentist owner"), coerce=int, 
                                                default=last_user_asset())
    office_id = SelectField(_("Office_where it is"), coerce=int,
                                                default=last_office_asset())
    #type = SelectField(_('Type'), description='ChangementType()')
    quantity = IntegerField(_('Quantity'), [validators.Optional()], default=1)

class DeviceForm(Form):
    device_id = HiddenField(_('id'))
    lifetime_expected = IntegerField(_('Lifetime expected in years'), 
                                                    [validators.Optional()])

class MaterialForm(Form):
    material_id = HiddenField(_('id'))
    used_in_traceabily_of = HiddenField(_('Used in traceability of'))
    actual_quantity = DecimalField(_('Actual Quantity'),
                                                    [validators.Optional()])
    expiration_date = DateField(_('Expiration Date'),
                                                    [validators.Optional()])
    expiration_alert = DecimalField(_('Expiration Alert'),
                                                    [validators.Optional()])
    service = BooleanField(_('In service since'), description='InService()')
    start_of_use = DateField(_('Start of Use'), [validators.Optional()])
    end_of_use = DateField(_('End of Use'), [validators.Optional()])
    end_use_reason = SelectField(_('Reason to end of use'), coerce=int)
    batch_number = TextField(_('Batch number'), [validators.Optional()])

def get_asset_provider_field_list():
    return [ "name", "active" ]

def get_asset_type_choices():
    return [ ( "device", _("Device") ), 
            ( "material", _("Material") ) ]

def get_material_cat_unity_choices():
    return [ ( 0, _("pieces/items") ), ( 1, _("volume in mL") ), 
                (2, _("weight in gr") ) ]

def get_asset_cat_field_list():
    return [ "barcode", "brand", "commercial_name",
                "description", "type" ]

def get_device_cat_field_list():
    return [ "sterilizable" ]

def get_material_cat_field_list():
    return [ "material_type", "order_threshold", "unity", 
            "initial_quantity", "automatic_decrease" ]

def get_asset_provider_choices(active=True):    
    query = meta.session.query(assets.AssetProvider).filter(
                                assets.AssetProvider.active == active).all()
    return [( f.id, f.name) for f in query ]

def get_asset_category_choices(barcode="", brand="", commercial_name="", 
                                    description=""):
    query = meta.session.query(assets.AssetCategory)
    if barcode:
        # we want to return a list
        query = query.filter(assets.AssetCategory.barcode == barcode).one()
        return [ ( query.id, (query.brand, query.commercial_name)) ]
    if brand:
        brand = '%{}%'.format(brand)
        query = query.filter(assets.AssetCategory.brand.ilike(brand))
    if commercial_name:
        commercial_name = '%{}%'.format(commercial_name)
        query = query.filter(assets.AssetCategory.commercial_name.ilike(
                                                            commercial_name))
    if description:
        description = '%{}%'.format(description)
        query = query.filter(assets.AssetCategory.description.ilike(
                                                            description))
    query = query.all()
    return [ ( q.id, (q.brand, q.commercial_name) ) for q in query ]

def get_user_choices(active=True):
    query = meta.session.query(users.OdontuxUser).filter(
                    users.OdontuxUser.role == constants.ROLE_DENTIST).filter(
                    users.OdontuxUser.active == active).all()
    user_list = [ (q.id, q.username) for q in query ]
    user_list.append( (0, "") )
    return user_list

def get_office_choices(active=True):
    query = meta.session.query(users.DentalOffice).filter(
                    users.DentalOffice.active == active).all()
    office_list = [ (q.id, q.office_name) for q in query ]
    office_list.append( (0, "") )
    return office_list

def verify_asset_cat_already_in_db(new_asset):
    """ test if barcode in db ; 
        if not, test if both brand and commercial_name are in it.
    """
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
                    for f in get_asset_provider_field_list()}
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
def list_assets(assets_type="all"):
    checks.quit_patient_file()
    checks.quit_appointment()

    assets_list = meta.session.query(assets.Asset)
    if assets_type == "device":
        assets_list = assets_list.filter(assets.Asset.type == "device").all()
    elif assets_type == "material":
        assets_list = assets_list.filter(assets.Asset.type == "material").all()
    else:
        assets_list = assets_list.all()
    return render_template('list_assets.html', assets_list=assets_list)

@app.route('/add/asset/', methods=['POST', 'GET'])
def add_asset():
    def _add_device_category(asset_cat_form, device_cat_form):
        values = {f: getattr(asset_cat_form, f).data
                for f in get_asset_cat_field_list()}
        for f in get_device_cat_field_list():
            values[f] = getattr(device_cat_form, f).data
        new_device_cat = assets.DeviceCategory(**values)
        meta.session.add(new_device_cat)
        meta.session.commit()
        return new_device_cat

    def _add_material_category(asset_cat_form, material_cat_form):
        values = {f: getattr(asset_cat_form, f).data
                for f in get_asset_cat_field_list()}
        for f in get_material_cat_field_list():
            values[f] = getattr(material_cat_form, f).data
        new_material_cat = assets.MaterialCategory(**values)
        meta.session.add(new_material_cat)
        meta.session.commit()
        return new_material_cat

    def _add_device(asset_form, device_form):
        values = {f: getattr(asset_form, f).data
                for f in add_asset_field_list }
        if asset_form.user_id.data:
            values['user_id'] = asset_form.user_id.data
        if asset_form.office_id.data:
            values['office_id'] = asset_form.office_id.data
        values['asset_category_id'] = asset_cat.id
            
        values['lifetime_expected'] = datetime.timedelta(
                                    365 * device_form.lifetime_expected.data)
        new_device = assets.Device(**values)
        meta.session.add(new_device)
        meta.session.commit()


    def _add_material(asset_form, material_form):
        values = {f: getattr(asset_form, f).data
                for f in add_asset_field_list }
        if asset_form.user_id.data:
            values['user_id'] = asset_form.user_id.data
        if asset_form.office_id.data:
            values['office_id'] = asset_form.office_id.data
        values['asset_category_id'] = asset_cat.id
        for f in add_material_field_list:
            values[f] = getattr(material_form, f).data
        if material_form.service.data:
            values['start_of_use'] = material_form.start_of.use.data
        values['actual_quantity'] = asset_cat.initial_quantity
        new_material = assets.Material(**values)
        meta.session.add(new_material)
        meta.session.commit()

    
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    asset_category_form = AssetCategoryForm(request.form)
    asset_category_form.type.choices = get_asset_type_choices()
    device_category_form = DeviceCategoryForm(request.form)
    material_category_form = MaterialCategoryForm(request.form)
    material_category_form.unity.choices = get_material_cat_unity_choices()
    asset_form = AssetForm(request.form)
    asset_form.provider_id.choices = get_asset_provider_choices()
    if not asset_form.provider_id.choices:
        return redirect(url_for('add_provider'))
    asset_form.type.choices = get_asset_type_choices()
    asset_form.user_id.choices = get_user_choices()
    asset_form.office_id.choices = get_office_choices()
    device_form = DeviceForm(request.form)
    material_form = MaterialForm(request.form)
    
    # POSTING and adding the data :
    asset_cat = verify_asset_cat_already_in_db(asset_category_form)
    if not asset_cat:
        """ Create a new AssetCategory """
        if ( request.method == 'POST'
            and asset_category_form.type.data == "device"
            and asset_category_form.validate() 
            and device_category_form.validate() ):
            asset_cat = _add_device_category(asset_category_form, 
                                            device_category_form)

        if ( request.method == 'POST'
            and asset_category_form.type.data == "material"
            and asset_category_form.validate() 
            and material_category_form.validate() ):
            asset_cat = _add_material_category(asset_category_form, 
                                            material_category_form)

    add_asset_field_list = [ "provider_id", "acquisition_date", 
                        "acquisition_price", "new" ]

    add_material_field_list = [ "used_in_traceability", "expiration_date", 
                                "expiration_alert", "batch_number" ]
   
    if ( request.method == 'POST' and asset_form.type.data == "device" 
        and asset_form.validate() and device_form.validate() ):
        i = 0
        while asset_form.quantity.data > i:
            _add_device(asset_form, device_form)
            i += 1

    if ( request.method == 'POST' and asset_form.type.data == "material"
        and asset_form.validate() and material_form.validate() ):
        i = 0
        while asset_form.quantity.data > i:
            _add_material(asset_form, material_form)
            i += 1
 
    return render_template('add_asset.html',
                            asset_category_form=asset_category_form,
                            asset_form=asset_form,
                            device_category_form=device_category_form,
                            device_form=device_form,
                            material_category_form=material_category_form,
                            material_form=material_form)


@app.route('/test_barcode/')
def test_barcode():
    barcode = request.args.get('barcode', None)
    if barcode:
        asset_category = meta.session.query(assets.AssetCategory).filter(
                    assets.AssetCategory.barcode == barcode).one_or_none()
        if asset_category:
            return jsonify(success=True,
                            brand=asset_category.brand, 
                            commercial_name=asset_category.commercial_name)
    return jsonify(success=False)
 
   
