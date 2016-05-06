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
                    DateField, SelectMultipleField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, assets, administration, users, act, schedule
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.log import index

def get_assets_in_superasset(return_id=False):
    """ this method is exported, for exemple in views.traceability """
    if return_id:
        query = meta.session.query(assets.Asset.id)
    else:
        query = meta.session.query(assets.Asset)

    query = (
        query.filter(assets.Asset.superassets.any(
                assets.SuperAsset.id.in_(
                    meta.session.query(assets.SuperAsset.id)
                        .filter(assets.SuperAsset.end_of_use.is_(None),
                                assets.SuperAsset.start_of_use.isnot(None),
                                assets.SuperAsset.end_use_reason == 
                                        constants.END_USE_REASON_IN_USE_STOCK
                        )
                    )
                )
            ).all()
        )
    return query

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
    id = HiddenField(_('id'))
    name = TextField(_('Asset provider name'), [validators.Required(
                                message=_("Provider's name required")),
                                validators.Length(max=30, 
                                message=_('Max : 30 characters'))],
                                filters=[forms.title_field])
    active = BooleanField(_('Active'))

class AssetCategoryForm(Form):
    id = HiddenField(_('id'))
    barcode = TextField(_('Barcode'), [validators.Optional()])
    brand = TextField(_('Brand'), [validators.Required(
                                        message=_("Brand's name required"))])
    commercial_name = TextField(_('Commercial name'), [validators.Required(
                                    message=_('Commercial name required'))])
    description = TextAreaField(_('Description'), [validators.Optional()])
    asset_specialty_id = SelectField(_('Specialty'), coerce=int, 
                                        validators=[validators.Optional()])
    type = SelectField(_('Type'), description='ChangementType()')

class DeviceCategoryForm(Form):
    id = HiddenField(_('id'))
    sterilizable = BooleanField(_('Sterilizable'))
    sterilizer = BooleanField(_('This device is an Autoclave/Sterilizer ?'))
    validity = IntegerField(_('Validity in days'), 
                                        validators=[validators.Optional()])

class MaterialCategoryForm(Form):
    id = HiddenField(_('id'))
    order_threshold = DecimalField(_("Order's threshold"), 
                                                    [validators.Optional()])
    unity = SelectField(_('Unity'), coerce=int)
    initial_quantity = DecimalField(_("Quantity of product"), 
                                                    [validators.Optional()])
    automatic_decrease = DecimalField(_('Automatic decrease'), 
                                                    [validators.Optional()])

class AssetForm(Form):
    id  = HiddenField(_('id'))
    provider_id = SelectField(_('Provider'), coerce=int)
    #asset_category_id = SelectField(_('Asset Category'), coerce=int)
    acquisition_date = DateField(_('Acquisition Date'), format='%Y-%m-%d')
    acquisition_price = DecimalField(_('Acquisition Price'))
    new = BooleanField(_('Asset new'))
    user_id = SelectField(_("Dentist owner"), coerce=int, 
                                                default=last_user_asset())
    office_id = SelectField(_("Office_where it is"), coerce=int,
                                                default=last_office_asset())
    #type = SelectField(_('Type'), description='ChangementType()')
    quantity = IntegerField(_('Quantity'), [validators.Optional()], default=1)
    service = BooleanField(_('In service since'), description='InService()')
    start_of_use = DateField(_('Start of Use'), 
                                    format='%Y-%m-%d',
                                    validators=[validators.Optional()])
    end_of_use = DateField(_('End of Use'), [validators.Optional()])
    end_use_reason = SelectField(_('Reason to end of use'), coerce=int, 
                                    validators=[validators.Optional()]) 

class DeviceForm(Form):
    device_id = HiddenField(_('id'))
    lifetime_expected = IntegerField(_('Lifetime expected in years'), 
                                                    [validators.Optional()])

class MaterialForm(Form):
    material_id = HiddenField(_('id'))
    used_in_traceability_of = HiddenField(_('Used in traceability of'))
    actual_quantity = DecimalField(_('Actual Quantity'),
                                                    [validators.Optional()])
    expiration_date = DateField(_('Expiration Date'), format='%Y-%m-%d',
                                        validators=[validators.Optional()])
    expiration_alert = IntegerField(_('Expiration Alert in days'),
                                                    [validators.Optional()])
    batch_number = TextField(_('Batch number'), [validators.Optional()])

class SuperAssetCategoryForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Name'), [validators.Required(
                                    message=_('Name of superasset required'))])
    sterilizable = BooleanField(_('Sterilizable'))
    assets_category_list = SelectMultipleField(_('Type of Assets'), coerce=int)

class SuperAssetForm(Form):
    id = HiddenField(_('id'))
    superasset_category_id = SelectField(_('Type of SuperAsset'), coerce=int)
    assets = SelectMultipleField(_('Assets elements of the Super Asset'), 
                                                                coerce=int)

class AssetKitStructureForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Name of new kind of Kit'), [validators.Required(
                        message=_("Give a name to the Kit")),
                        validators.Length(max=30, 
                        message=_('Max : 30 characters'))],
                        filters=[forms.title_field])
    active = BooleanField(_('active'))

class AssetKitForm(Form):
    id = HiddenField(_('id'))
    asset_kit_structure_id = SelectField(_('Type of kit'), coerce=int)
    creation_date = DateField(_('Creation Date of the Kit'), format='%Y-%m-%d')
    end_of_use = DateField(_('End of Use'), [validators.Optional()])
    end_use_reason = SelectField(_('Reason to end of use'), coerce=int ) 

def get_kit_structure_assets_choices():
    assets_category = meta.session.query(assets.DeviceCategory).filter(
                                    assets.DeviceCategory.sterilizable == True
                                    ).all()
    if not assets_category:
        return [ (0, "") ]
    return [ (r.id, r.brand + " || " + r.commercial_name) 
                                                    for r in assets_category ]

def get_kit_structure_superassets_choices():
    superassets_category = (
        meta.session.query(assets.SuperAssetCategory)
            .filter(assets.SuperAssetCategory.sterilizable == True)
            .all()
        )
    if not superassets_category:
        return[ (0, "") ]
    return [ (r.id, r.name) for r in superassets_category ]

def get_superasset_category_choices():
    assets_category = meta.session.query(assets.DeviceCategory).all()
    if not assets_category:
        return [ (0, "") ]
    return [ (r.id, r.brand + " " + r.commercial_name) for r in assets_category
            ]

def get_asset_provider_field_list():
    return [ "name", "active" ]

def get_asset_type_choices():
    return [ ( "device", _("Device") ), 
            ( "material", _("Material") ) ]

def get_material_cat_unity_choices():
    return constants.UNITY
#    return [ ( 0, _("pieces/items") ), ( 1, _("volume in mL") ), 
#                (2, _("weight in gr") ), (3, _('length in m') ) ]

def get_end_use_reason_choices():
    return constants.END_USE_REASON
    
def get_asset_cat_field_list():
    return [ "brand", "commercial_name",
                "description", "type"]

def get_device_cat_field_list():
    return [ "sterilizable", "sterilizer" ]

def get_material_cat_field_list():
    return [ "order_threshold", "unity", 
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

def get_asset_specialty_choices():
    query = meta.session.query(act.Specialty).all()
    specialty_list = [ (s.id, s.name) for s in query ]
    specialty_list.append( (0, "") )
    return specialty_list

def get_kit_structure_id_choices():
    return meta.session.query(assets.AssetKitStructure.id, 
                                assets.AssetKitStructure.name).all()

def verify_asset_cat_already_in_db(new_asset):
    """ test if barcode in db ; 
        if not, test if both brand and commercial_name are in it.
        return instance of asset_category if exist
    """
    asset_cat_in_db = None
    if new_asset.barcode.data:
        asset_cat_in_db = meta.session.query(assets.AssetCategory).filter(
                        assets.AssetCategory.barcode == new_asset.barcode.data
                                                                ).one_or_none()
    if not asset_cat_in_db:
        asset_cat_in_db = meta.session.query(assets.AssetCategory).filter(and_(
                            assets.AssetCategory.brand == new_asset.brand.data,
                            assets.AssetCategory.commercial_name == 
                            new_asset.commercial_name.data
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

    if session['role'] != constants.ROLE_DENTIST:
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

@app.route('/list_assets?asset_type=<asset_type>/')
def list_assets(asset_type="all"):
    checks.quit_patient_file()
    checks.quit_appointment()
    
    if asset_type == "device":
        query = meta.session.query(assets.Device)
    elif asset_type == "material":
        query = meta.session.query(assets.Material)
    elif asset_type == "superasset":
        query = meta.session.query(assets.SuperAsset)
    else:
        query = meta.session.query(assets.Asset)
        
    query = ( query.order_by(assets.Asset.acquisition_date.desc())
                    .limit(100)
                    .all()
            )

    return render_template('list_assets.html', 
                            assets_list=query)

@app.route('/add/asset/', methods=['POST', 'GET'])
def add_asset():
    def _add_device_category(asset_cat_form, device_cat_form):
        values = {f: getattr(asset_cat_form, f).data
                for f in get_asset_cat_field_list()}
        if asset_cat_form.barcode.data:
            values["barcode"] = asset_cat_form.barcode.data
        else:
            values['barcode'] = None
        if asset_cat_form.asset_specialty_id.data:
            values['asset_specialty_id'] =\
                                        asset_cat_form.asset_specialty_id.data
        for f in get_device_cat_field_list():
            values[f] = getattr(device_cat_form, f).data
        new_device_cat = assets.DeviceCategory(**values)
        meta.session.add(new_device_cat)
        meta.session.commit()
        return new_device_cat

    def _add_material_category(asset_cat_form, material_cat_form):
        values = {f: getattr(asset_cat_form, f).data
                for f in get_asset_cat_field_list()}
        if asset_cat_form.barcode.data:
            values["barcode"] = asset_cat_form.barcode.data
        else:
            values['barcode'] = None
        if asset_cat_form.asset_specialty_id.data:
            values['asset_specialty_id'] =\
                                        asset_cat_form.asset_specialty_id.data
        for f in get_material_cat_field_list():
            values[f] = getattr(material_cat_form, f).data
        new_material_cat = assets.MaterialCategory(**values)
        meta.session.add(new_material_cat)
        meta.session.commit()
        return new_material_cat

    def _add_device(asset_form, device_form, asset_cat):
        values = {f: getattr(asset_form, f).data
                for f in add_asset_field_list }
        if asset_form.user_id.data:
            values['user_id'] = asset_form.user_id.data
        if asset_form.office_id.data:
            values['office_id'] = asset_form.office_id.data
        if asset_form.service.data:
            values['start_of_use'] = asset_form.start_of_use.data
        values['asset_category_id'] = asset_cat.id
        
        if device_form.lifetime_expected.data:
            values['lifetime_expected'] = datetime.timedelta(
                                    365 * device_form.lifetime_expected.data)
        new_device = assets.Device(**values)
        meta.session.add(new_device)
        meta.session.commit()


    def _add_material(asset_form, material_form, asset_cat):
        values = {f: getattr(asset_form, f).data
                for f in add_asset_field_list }
        if asset_form.user_id.data:
            values['user_id'] = asset_form.user_id.data
        if asset_form.office_id.data:
            values['office_id'] = asset_form.office_id.data
        values['asset_category_id'] = asset_cat.id
        if asset_form.service.data:
            values['start_of_use'] = asset_form.start_of_use.data
        for f in add_material_field_list:
            values[f] = getattr(material_form, f).data
        if material_form.expiration_alert.data:
            values['expiration_alert'] = datetime.timedelta(
                                        material_form.expiration_alert.data)
        values['actual_quantity'] = asset_cat.initial_quantity
        new_material = assets.Material(**values)
        meta.session.add(new_material)
        meta.session.commit()

    
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    asset_category_form = AssetCategoryForm(request.form)
    asset_category_form.asset_specialty_id.choices =\
                                                get_asset_specialty_choices()
    asset_category_form.type.choices = get_asset_type_choices()
    device_category_form = DeviceCategoryForm(request.form)
    material_category_form = MaterialCategoryForm(request.form)
    material_category_form.unity.choices = get_material_cat_unity_choices()
    asset_form = AssetForm(request.form)
    asset_form.provider_id.choices = get_asset_provider_choices()
    if not asset_form.provider_id.choices:
        return redirect(url_for('add_provider'))
    asset_form.user_id.choices = get_user_choices()
    asset_form.office_id.choices = get_office_choices()
    asset_form.end_use_reason.choices = get_end_use_reason_choices()
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

    add_material_field_list = [ "used_in_traceability_of", "expiration_date", 
                                "expiration_alert", "batch_number" ]
   
    if ( request.method == 'POST' 
        and asset_category_form.type.data == "device" 
        and asset_form.validate() and device_form.validate() ):
        i = 0
        while asset_form.quantity.data > i:
            _add_device(asset_form, device_form, asset_cat)
            i += 1
        return redirect(url_for('list_assets', asset_type="device"))
    
    if ( request.method == 'POST' 
        and asset_category_form.type.data == "material"
        and asset_form.validate() and material_form.validate() ):
        i = 0
        while asset_form.quantity.data > i:
            _add_material(asset_form, material_form, asset_cat)
            i += 1
        return redirect(url_for('list_assets', asset_type="material"))

    if request.method == 'POST':
        clear_form = False
    else:
        clear_form = True
    asset_form.provider_id.data = last_asset_provider()
    return render_template('add_asset.html',
                            asset_category_form=asset_category_form,
                            asset_form=asset_form,
                            device_category_form=device_category_form,
                            device_form=device_form,
                            material_category_form=material_category_form,
                            material_form=material_form,
                            clear_form=clear_form)

@app.route('/update/asset_category?id=<int:asset_category_id>')
def update_asset_category(asset_category_id):
    asset_cat = (
        meta.session.query(assets.AssetCategory)
            .filter(assets.AssetCategory.id == asset_category_id)
            .one()
        )
    if asset_cat.type == "device":
        return redirect(url_for('update_device_category', 
                                device_category_id=asset_category_id))
    elif asset_cat.type == "material":
        return redirect(url_for('update_material_category',
                                material_category_id=asset_category_id))
    else:
        pass

@app.route('/update/device_category?id=<int:device_category_id>',
                                            methods=['GET', 'POST'])
def update_device_category(device_category_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    asset_category = (
        meta.session.query(assets.DeviceCategory)
            .filter(assets.DeviceCategory.id == device_category_id)
            .one()
        )
    asset_category_form = AssetCategoryForm(request.form)
    device_category_form = DeviceCategoryForm(request.form)
    asset_category_form.asset_specialty_id.choices =\
                                                get_asset_specialty_choices()
    asset_category_form.type.choices = get_asset_type_choices()
    asset_category_form.type.data = asset_category.type
    if ( request.method == 'POST' and asset_category_form.validate()
                                and device_category_form.validate() ):
        for f in get_asset_cat_field_list():
            setattr(asset_category, f, getattr(asset_category_form, f).data)
        if not asset_category_form.barcode.data:
            asset_category_form.barcode.data = None
        asset_category.barcode = asset_category_form.barcode.data
        asset_category.asset_specialty_id =\
                                    asset_category_form.asset_specialty_id.data
        for f in get_device_cat_field_list():
            setattr(asset_category, f, getattr(device_category_form, f).data)
        asset_category.validity = datetime.timedelta(
                                            device_category_form.validity.data)
        meta.session.commit()
        return redirect(url_for('view_asset_category', 
                                        asset_category_id=device_category_id))
    for f in get_asset_cat_field_list():
        getattr(asset_category_form, f).data = getattr(asset_category, f)
    asset_category_form.asset_specialty_id.data =\
                                            asset_category.asset_specialty_id
    asset_category_form.barcode.data = asset_category.barcode
    for f in get_device_cat_field_list():
        getattr(device_category_form, f).data = getattr(asset_category, f)
    device_category_form.validity.data =\
                        int(asset_category.validity.total_seconds() / 86400)
    return render_template('update_device_category.html',
                                asset_category=asset_category,
                                asset_category_form=asset_category_form,
                                device_category_form=device_category_form)

@app.route('/update/material_category?id=<int:material_category_id>',
                                            methods=['GET', 'POST'])
def update_material_category(material_category_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    asset_category = (
        meta.session.query(assets.MaterialCategory)
            .filter(assets.MaterialCategory.id == material_category_id)
            .one()
        )
    asset_category_form = AssetCategoryForm(request.form)
    material_category_form = MaterialCategoryForm(request.form)
    asset_category_form.asset_specialty_id.choices =\
                                                get_asset_specialty_choices()
    asset_category_form.type.choices = get_asset_type_choices()
    asset_category_form.type.data = asset_category.type
    material_category_form.unity.choices = get_material_cat_unity_choices()
    if ( request.method == 'POST' and asset_category_form.validate()
                                and material_category_form.validate() ):
        for f in get_asset_cat_field_list():
            setattr(asset_category, f, getattr(asset_category_form, f).data)
        if not asset_category_form.barcode.data:
            asset_category_form.barcode.data = None
        asset_category.barcode = asset_category_form.barcode.data
        asset_category.asset_specialty_id =\
                                    asset_category_form.asset_specialty_id.data
        for f in get_material_cat_field_list():
            setattr(asset_category, f, getattr(material_category_form, f).data)
        meta.session.commit() 
        return redirect(url_for('view_asset_category', 
                                    asset_category_id=material_category_id))
    for f in get_asset_cat_field_list():
        getattr(asset_category_form, f).data = getattr(asset_category, f)
    asset_category_form.asset_specialty_id.data =\
                                            asset_category.asset_specialty_id
    asset_category_form.barcode.data = asset_category.barcode

    for f in get_material_cat_field_list():
        getattr(material_category_form, f).data = getattr(asset_category, f)
 
    return render_template('update_material_category.html',
                                asset_category=asset_category,
                                asset_category_form=asset_category_form,
                                material_category_form=material_category_form)

@app.route('/view/asset_category?id=<int:asset_category_id>')
def view_asset_category(asset_category_id):
    asset_category = (
        meta.session.query(assets.AssetCategory)
            .filter(assets.AssetCategory.id == asset_category_id)
            .one_or_none()
        )
    if not asset_category:
        asset_category = (
            meta.session.query(assets.MaterialCategory)
                .filter(assets.MaterialCategory.id == asset_category_id)
                .one_or_none()
            )
     
    if asset_category.type == "device":
#        return redirect(url_for('view_device_category',
#                                    device_category_id=asset_category_id))
        return render_template('view_device_category.html',
                                        asset_category=asset_category)
    elif asset_category.type == "material":
#        return redirect(url_for('view_material_category',
#                                    material_category_id=asset_category_id))
        return render_template('view_material_category.html',
                                        asset_category=asset_category)
    else:
        return redirect(url_for('index'))

@app.route('/update/asset?id=<int:asset_id>', methods=['GET', 'POST'])
def update_asset(asset_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    asset = meta.session.query(assets.Asset).filter(
                            assets.Asset.id == asset_id).one()

    asset_form = AssetForm(request.form)
    asset_form.provider_id.choices = get_asset_provider_choices()
    asset_form.user_id.choices = get_user_choices()
    asset_form.office_id.choices = get_office_choices()
    asset_form.end_use_reason.choices = get_end_use_reason_choices()
    device_form = DeviceForm(request.form)
    material_form = MaterialForm(request.form)

    update_asset_field_list = [ "id", "provider_id", "acquisition_date", 
                        "acquisition_price", "new", "user_id", "office_id",
                        "start_of_use", "end_of_use", "end_use_reason"]

    update_device_field_list = [ "lifetime_expected" ]

    update_material_field_list = [ "used_in_traceability_of", 
                    "expiration_date", "actual_quantity", "expiration_alert", 
                    "batch_number" ]
 
    if (request.method == 'POST' and asset.type == "device"
        and asset_form.validate() and device_form.validate() ):
        for f in update_asset_field_list:
            setattr(asset, f, getattr(asset_form, f).data)
        for f in update_device_field_list:
            if f == "lifetime_expected" and getattr(device_form, f).data:
                setattr(asset, f, datetime.timedelta(getattr(
                                                device_form, f).data * 365))
        meta.session.commit()
        return redirect(url_for('view_device', asset_id=asset.id))
        
    if (request.method == "POST" and asset.type == "material"
        and asset_form.validate() and material_form.validate() ):
        for f in update_asset_field_list:
            setattr(asset, f, getattr(asset_form, f).data)
        for f in update_material_field_list:
            if f == "expiration_alert":
                setattr(asset, f, datetime.timedelta(getattr(
                                                    material_form, f).data))
            else:
                setattr(asset, f, getattr(material_form, f).data)
        meta.session.commit()
        return redirect(url_for('view_material', asset_id=asset.id))

   
    if request.method == 'POST':
        clear_form = False
    else:
        clear_form = True

    if asset.type == "device":
        for f in update_asset_field_list:
            getattr(asset_form, f).data = getattr(asset, f)
        for f in update_device_field_list:
            if f == "lifetime_expected" and getattr(asset, f):
                getattr(device_form, f).data = int(
                            getattr(asset, f).total_seconds() / (86400*365))
            else:
                getattr(device_form, f).data = getattr(asset, f)
        return render_template('update_device.html',
                            asset_form=asset_form,
                            device_form=device_form,
                            asset=asset,
                            clear_form=clear_form)

    elif asset.type == "material":
        for f in update_asset_field_list:
            getattr(asset_form, f).data = getattr(asset, f)
        for f in update_material_field_list:
            if f == "expiration_alert":
                getattr(material_form, f).data = int(
                                    getattr(asset, f).total_seconds() / 86400)
            else:
                getattr(material_form, f).data = getattr(asset, f)
        return render_template('update_material.html',
                            asset_form=asset_form,
                            material_form=material_form,
                            asset=asset,
                            clear_form=clear_form)
    else:
        pass

@app.route('/view/asset&id=<int:asset_id>')
def view_asset(asset_id):
    asset = meta.session.query(assets.Asset).filter(
                                    assets.Asset.id == asset_id).one()
    if asset.type == "device":
        return redirect(url_for('view_device', asset_id=asset_id))
    elif asset.type == "material":
        return redirect(url_for('view_material', asset_id=asset_id))
    elif asset.type == "superasset":
        return redirect(url_for('view_superasset', asset_id=asset_id))
    else:
        return redirect(url_for('index'))

@app.route('/view/device&id=<int:asset_id>')
def view_device(asset_id):
    asset = meta.session.query(assets.Asset).filter(
                                assets.Asset.id == asset_id).one()
    return render_template('view_device.html', asset=asset, 
                                                today=datetime.date.today())

@app.route('/view/material&id=<int:asset_id>')
def view_material(asset_id):
    asset = meta.session.query(assets.Asset).filter(
                                assets.Asset.id == asset_id).one()
    return render_template('view_material.html', asset=asset)

@app.route('/view/superasset&id=<int:asset_id>')
def view_superasset(asset_id):
    asset = meta.session.query(assets.Asset).filter(
                                assets.Asset.id == asset_id).one()
    return render_template('view_superasset.html', asset=asset)

@app.route('/test_barcode/')
def test_barcode():
    barcode = request.args.get('barcode', None)
    if barcode:
        asset_category = meta.session.query(assets.AssetCategory).filter(
                    assets.AssetCategory.barcode == barcode).one_or_none()
        if not asset_category:
            return jsonify(success=False)

        if asset_category.type == "device":
            asset = meta.session.query(assets.DeviceCategory).filter(
                            assets.DeviceCategory.barcode == barcode).one()
            return jsonify(success=True, type="device",
                                brand=asset.brand,
                                barcode=asset.barcode,
                                commercial_name=asset.commercial_name,
                                description=asset.description,
                                asset_specialty_id=asset.asset_specialty_id,
                                sterilizable=asset.sterilizable,
                                )

        if asset_category.type == "material":
            asset = meta.session.query(assets.MaterialCategory).filter(
                            assets.MaterialCategory.barcode == barcode).one()
            return jsonify(success=True, type="material",
                            brand=asset.brand,
                            barcode=asset.barcode,
                            commercial_name=asset.commercial_name,
                            description=asset.description,
                            asset_specialty_id=asset.asset_specialty_id,
                            order_threshold=float(asset.order_threshold),
                            unity=asset.unity,
                            initial_quantity=float(asset.initial_quantity),
                            automatic_decrease=float(asset.automatic_decrease),
                            )
                            

        raise ValueError('The asset type in database neither is "device" nor "material"')
    return jsonify(success=False)

@app.route('/add/superasset_category/', methods=['GET', 'POST'])
def add_superasset_category():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    superasset_category_form = SuperAssetCategoryForm(request.form)  
    superasset_category_form.assets_category_list.choices = \
                                    get_superasset_category_choices()

    if request.method == 'POST' and superasset_category_form.validate():
        values = {
            'name': superasset_category_form.name.data,
            'sterilizable': superasset_category_form.sterilizable.data,
        }
        new_superasset_category = assets.SuperAssetCategory(**values)
        meta.session.add(new_superasset_category)

        for val in superasset_category_form.assets_category_list.data:
            asset = ( meta.session.query(assets.AssetCategory)
                        .filter(assets.AssetCategory.id == val).one()
                    )
            new_superasset_category.type_of_assets.append(asset)
        meta.session.commit()
        return redirect(url_for('add_superasset', 
                            superasset_category_id=new_superasset_category.id))

    return render_template('add_superasset_category.html',
                            superasset_category_form=superasset_category_form)

@app.route('/list/superasset_category/')
def list_superasset_category():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    superasset_categories = (
        meta.session.query(assets.SuperAssetCategory).all()
        )
    return render_template('list_superasset_category.html',
                        superasset_categories=superasset_categories)

@app.route('/add/asset_category_in_superasset_category&sac=<int:superasset_category_id>&ac=<int:asset_category_id>')
def add_asset_category_in_superasset_category(superasset_category_id,
                                                        asset_category_id):
    superasset_category = ( 
        meta.session.query(assets.SuperAssetCategory)
            .filter(assets.SuperAssetCategory.id == superasset_category_id)
            .one()
        )
    asset_category = (
        meta.session.query(assets.AssetCategory)
            .filter(assets.AssetCategory.id == asset_category_id).one()
        )
    superasset_category.type_of_assets.append(asset_category)
    meta.session.commit()
    return redirect(url_for('update_assets_in_superasset_category',
                            superasset_category_id=superasset_category_id))

@app.route('/remove/asset_category_in_superasset_category&sac=<int:superasset_category_id>&ac=<int:asset_category_id>')
def remove_asset_category_in_superasset_category(superasset_category_id,
                                                        asset_category_id):
    superasset_category = ( 
        meta.session.query(assets.SuperAssetCategory)
            .filter(assets.SuperAssetCategory.id == superasset_category_id)
            .one()
        )
    asset_category = (
        meta.session.query(assets.AssetCategory)
            .filter(assets.AssetCategory.id == asset_category_id).one()
        )
    superasset_category.type_of_assets.remove(asset_category)
    meta.session.commit()
    return redirect(url_for('update_assets_in_superasset_category',
                            superasset_category_id=superasset_category_id))

   
@app.route('/update/superasset_category&id=<int:superasset_category_id>')
def update_assets_in_superasset_category(superasset_category_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    superasset_category = (
        meta.session.query(assets.SuperAssetCategory)
            .filter(assets.SuperAssetCategory.id == superasset_category_id)
            .one()
        )
    assets_in_superasset = [ asset_category.id 
                    for asset_category in superasset_category.type_of_assets ]
    assets_categories = (
        meta.session.query(assets.AssetCategory)
            .filter(~assets.AssetCategory.id.in_(assets_in_superasset))
            .all()
        )

    return render_template('update_superasset_category.html',
                                    superasset_category=superasset_category,
                                    assets_categories=assets_categories)

@app.route('/add/superasset/', methods=['GET', 'POST'])
@app.route('/add/superasset&id=<int:superasset_category_id>/', 
                                                    methods=['GET', 'POST'])
def add_superasset(superasset_category_id=None):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    superasset_form = SuperAssetForm(request.form)
    superasset_form.superasset_category_id.choices = [ (asset.id, asset.name) 
        for asset in meta.session.query(assets.SuperAssetCategory).all() ]
    if superasset_category_id:
        superasset_category = (
                meta.session.query(assets.SuperAssetCategory)
                    .filter(assets.SuperAssetCategory.id == 
                            superasset_category_id)
                    .one()
                )
        assets_categories = []
        for asset_category in superasset_category.type_of_assets:
            asset_cat = ( meta.session.query(assets.AssetCategory.id)
                        .filter(assets.AssetCategory.id == asset_category.id)
                        .one()
                    )
            assets_categories.append(asset_cat)
            # assets in superasset actif
            assets_id_in_superasset = get_assets_in_superasset(return_id=True)
            assets_to_display = (
                meta.session.query(assets.Asset)
                    .filter(assets.Asset.asset_category_id.in_(assets_categories))
                    .filter(assets.Asset.type != "superasset")
                    .filter(~assets.Asset.id.in_(assets_id_in_superasset))
                    .all()
                    )
        superasset_form.assets.choices = [ 
                        (asset.id, str(asset.id) + " " + asset.asset_category.brand
                        + " " + asset.asset_category.commercial_name)
                        for asset in assets_to_display ]
    else:
        superasset_form.assets.choices = [
                                (asset.id,
                                str(asset.id) + " " +
                                asset.asset_category.brand + " " +
                                asset.asset_category.commercial_name)
            for asset in ( meta.session.query(assets.Asset)
                                .filter(assets.Asset.type != "superasset")
                                .all() ) ]

    if request.method == 'POST' and superasset_form.validate():
        values = {
            "superasset_category_id": superasset_form.superasset_category_id.data,
            "start_of_use": datetime.date.today()
        }
        new_superasset = assets.SuperAsset(**values)
        meta.session.add(new_superasset)
        for val in superasset_form.assets.data:
            asset = ( meta.session.query(assets.Asset)
                        .filter(assets.Asset.id == val).one() )
            new_superasset.assets.append(asset)
        meta.session.commit()

    if superasset_category_id:
        superasset_form.superasset_category_id.data = superasset_category_id

    return render_template('add_superasset.html',
                            superasset_form=superasset_form)

@app.route('/add/kit_type/', methods=['GET', 'POST'])
def add_kit_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    kit_structure_form = AssetKitStructureForm(request.form)
#    kit_structure_form.assets_category_list.choices = \
#                                        get_kit_structure_assets_choices()
#
    if request.method == 'POST' and kit_structure_form.validate():
        new_asset_kit = assets.AssetKitStructure(
                                        name=kit_structure_form.name.data)
        meta.session.add(new_asset_kit)
#        for val in kit_structure_form.assets_category_list.data:
#            asset = meta.session.query(assets.AssetCategory).filter(
#                                assets.AssetCategory.id == val).one()
#            new_asset_kit.type_of_assets.append(asset)
#
        meta.session.commit()
        return redirect(url_for('update_kit_type', 
                                kit_type_id=new_asset_kit.id))

    return render_template('add_kit_type.html',
                                kit_structure_form=kit_structure_form)

@app.route('/update/kit_type?id=<kit_type_id>', methods=['GET', 'POST'])
def update_kit_type(kit_type_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    kit_structure_form = AssetKitStructureForm(request.form)
#    kit_structure_form.assets_category_list.choices = \
#                                        get_kit_structure_assets_choices()
    kit_structure = meta.session.query(assets.AssetKitStructure).filter(
                assets.AssetKitStructure.id == kit_type_id).one_or_none()
    if not kit_structure:
        return render_template('list_kit_type')
#    asset_list = [ asset.id for asset in kit_structure.type_of_assets ]

    if request.method == 'POST' and kit_structure_form.validate():
        for f in [ "name", "active" ]:
            setattr(kit_structure, f, getattr(kit_structure_form, f).data)

#        for val in set(kit_structure_form.assets_category_list.data) \
#                                                            - set(asset_list):
#            asset = meta.session.query(assets.AssetCategory).filter(
#                                assets.AssetCategory.id == val).one()
#            kit_structure.type_of_assets.append(asset)
#        for val in set(asset_list) - \
#                        set(kit_structure_form.assets_category_list.data):
#            asset = meta.session.query(assets.AssetCategory).filter(
#                                assets.AssetCategory.id == val).one()
#            kit_structure.type_of_assets.remove(asset)
        meta.session.commit()
        return redirect(url_for('update_assets_categories_in_kit_structure',
                                    kit_structure_id=kit_structure.id))

#    kit_structure_form.assets_category_list.data = asset_list
    kit_structure_form.active.data = kit_structure.active
    return render_template('update_kit_type.html',
                                kit_structure_form=kit_structure_form,
                                kit_structure=kit_structure)

@app.route('/add/asset_category_in_kit_structure&kit_structure=<int:kit_structure_id>&asset_cat=<int:asset_cat_id>&asset_type=<asset_type>')
def add_asset_category_in_kit_structure(kit_structure_id, asset_cat_id, 
                                                                asset_type):
    kit_structure = ( 
        meta.session.query(assets.AssetKitStructure)
            .filter(assets.AssetKitStructure.id == kit_structure_id)
            .one()
        )
    if asset_type == "asset":
        asset_cat = (
            meta.session.query(assets.AssetCategory)
                .filter(assets.AssetCategory.id == asset_cat_id).one()
            )
        kit_structure.type_of_assets.append(asset_cat)
    elif asset_type == "superasset":
        superasset_cat = (
            meta.session.query(assets.SuperAssetCategory)
                .filter(assets.SuperAssetCategory.id == asset_cat_id).one()
            )
        kit_structure.type_of_superassets.append(superasset_cat)
    else:
        pass
    meta.session.commit()
    return redirect(url_for('update_assets_categories_in_kit_structure', 
                                            kit_structure_id=kit_structure_id))

@app.route('/remove/asset_category_from_kit_structure&kit_structure=<int:kit_structure_id>&asset_cat=<int:asset_cat_id>&asset_type=<asset_type>')
def remove_asset_category_from_kit_structure(kit_structure_id, asset_cat_id,
                                                                asset_type):
    kit_structure = ( 
        meta.session.query(assets.AssetKitStructure)
            .filter(assets.AssetKitStructure.id == kit_structure_id)
            .one()
        )
    if asset_type == "asset":
        asset_cat = (
            meta.session.query(assets.AssetCategory)
                .filter(assets.AssetCategory.id == asset_cat_id).one()
            )
        kit_structure.type_of_assets.remove(asset_cat)
    elif asset_type == "superasset":
        superasset_cat = (
            meta.session.query(assets.SuperAssetCategory)
                .filter(assets.SuperAssetCategory.id == asset_cat_id).one()
            )
        kit_structure.type_of_superassets.remove(superasset_cat)
    else:
        pass
    meta.session.commit()
    return redirect(url_for('update_assets_categories_in_kit_structure', 
                                            kit_structure_id=kit_structure_id))

@app.route('/update/assets_categories_in_kit_structure?id=<int:kit_structure_id>')
def update_assets_categories_in_kit_structure(kit_structure_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    kit_structure = (
        meta.session.query(assets.AssetKitStructure)
            .filter(assets.AssetKitStructure.id == kit_structure_id)
            .one()
        )
    assets_categories_in_this_kit = [ asset_cat.id 
                        for asset_cat in kit_structure.type_of_assets ]
    superassets_categories_in_this_kit = [superasset_cat.id
                    for superasset_cat in kit_structure.type_of_superassets ]
    assets_categories_to_display = (
        meta.session.query(assets.AssetCategory)
            .filter(
                # Asset category not already in this kit
                ~assets.AssetCategory.id.in_(assets_categories_in_this_kit)
            )
            .all()
        )
    superassets_categories_to_display = (
        meta.session.query(assets.SuperAssetCategory)
            .filter(
                ~assets.SuperAssetCategory.id.in_(
                                superassets_categories_in_this_kit)
            )
            .all()
        )
    
    return render_template('update_assets_categories_in_kit_structure.html',
                    kit_structure=kit_structure,
                    assets_categories=assets_categories_to_display,
                    superassets_categories=superassets_categories_to_display)

@app.route('/list/kit_type/')
def list_kit_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    kit_types = (
        meta.session.query(assets.AssetKitStructure)
            .filter(assets.AssetKitStructure.active == True)
            .all()
        )
    unactive_kit_types = (
        meta.session.query(assets.AssetKitStructure)
            .filter(assets.AssetKitStructure.active == False)
            .all()
        )
    return render_template('list_kit_type.html', kit_types=kit_types)
   

@app.route('/list/kits/', methods=['GET'])
@app.route('/list/kits?kit_type=<int:kit_types>', methods=['GET'])
def list_kits(kit_types=0):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    checks.quit_patient_file()
    checks.quit_appointment()
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    if not kit_types:
        kits_list = meta.session.query(assets.AssetKit).filter(
                                assets.AssetKit.appointment_id == None).all()
    else:
        kits_list = []
        query = meta.session.query(assets.AssetKit).filter(
                                assets.AssetKit.appointment_id == None)
        for kit_type in kit_types.split(","):
            q = query.filter(
                    assets.AssetKit.asset_kit_structure_id == kit_type).all()
            for kit in q:
                kits_list.append(kit)
    
    return render_template('list_kits.html',
                            kits_list=kits_list)

@app.route('/view/kit?id=<kit_id>')
def view_kit(kit_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    checks.quit_patient_file()
    checks.quit_appointment()
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    kit = meta.session.query(assets.AssetKit).filter(
                                assets.AssetKit.id == kit_id).one()

    return render_template("view_kit.html", kit=kit)

@app.route('/add/kit/', methods=['GET', 'POST'])
@app.route('/add/kit?kit_type=<int:kit_type_id>', methods=['GET', 'POST'])
def add_kit(kit_type_id=0):
    def _get_asset_kit_field_list():
        return [ "asset_kit_structure_id", "creation_date" ]
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    
    kit_form = AssetKitForm(request.form)
    kit_form.asset_kit_structure_id.choices = get_kit_structure_id_choices()
    if kit_type_id:
        kit_form.asset_kit_structure_id.data = kit_type_id
    kit_form.end_use_reason.choices = get_end_use_reason_choices()
    
    if request.method == "POST" and kit_form.validate():
        values = { f: getattr(kit_form, f).data
            for f in _get_asset_kit_field_list() }
        new_kit = assets.AssetKit(**values)
        meta.session.add(new_kit)
        meta.session.commit()
        return redirect(url_for('update_kit', kit_id=new_kit.id))

    kit_form.creation_date.data = datetime.date.today()
    return render_template('add_kit.html',
                            kit_form=kit_form)

@app.route('/add/asset_in_kit&kit=<int:kit_id>&asset=<int:asset_id>')
def add_asset_in_kit(kit_id, asset_id):
    kit = ( 
        meta.session.query(assets.AssetKit)
            .filter(assets.AssetKit.id == kit_id)
            .one()
        )
    asset = (
        meta.session.query(assets.Asset)
            .filter(assets.Asset.id == asset_id).one()
        )
    kit.assets.append(asset)
    meta.session.commit()
    return redirect(url_for('update_kit', kit_id=kit_id))

@app.route('/remove/asset_from_kit&kit=<int:kit_id>&asset=<int:asset_id>')
def remove_asset_from_kit(kit_id, asset_id):
    kit = ( 
        meta.session.query(assets.AssetKit)
            .filter(assets.AssetKit.id == kit_id)
            .one()
        )
    asset = (
        meta.session.query(assets.Asset)
            .filter(assets.Asset.id == asset_id).one()
        )
    kit.assets.remove(asset)
    meta.session.commit()
    return redirect(url_for('update_kit', kit_id=kit_id))

@app.route('/update/kit&id=<int:kit_id>')
def update_kit(kit_id):

    kit = ( meta.session.query(assets.AssetKit)
                .filter(assets.AssetKit.id == kit_id)
                .one()
        )
    assets_already_in_this_kit = [ asset.id for asset in kit.assets ]
    assets_id_in_others_kits = (
        meta.session.query(assets.Asset.id)
            .filter(assets.Asset.kits.any(
                assets.AssetKit.id.in_(
                    meta.session.query(assets.AssetKit.id)
                        .filter(
                            assets.AssetKit.end_of_use.is_(None),
                            assets.AssetKit.appointment_id.is_(None),
                            assets.AssetKit.end_use_reason ==
                                constants.END_USE_REASON_IN_USE_STOCK
                            )
                        )
                    )
                )
            )
    assets_categories_in_kit_structure = []
    for asset_category in kit.asset_kit_structure.type_of_assets:
        asset_cat = (
            meta.session.query(assets.AssetCategory.id)
                .filter(assets.AssetCategory.id == asset_category.id)
                .one()
            )
        assets_categories_in_kit_structure.append(asset_cat)
    
    assets_to_display = (
        meta.session.query(assets.Asset)
            .filter(
                # Asset is in use
                assets.Asset.end_of_use.is_(None),
                assets.Asset.end_use_reason ==
                        constants.END_USE_REASON_IN_USE_STOCK,
#                # Asset is sterilizable
#                assets.DeviceCategory.sterilizable == True,
                # Asset element of asset_categories listed by kit_structure
                assets.Asset.asset_category_id.in_(
                    assets_categories_in_kit_structure),
                # Asset not element of an active kit
                ~assets.Asset.id.in_(assets_id_in_others_kits),
                # Asset not marked in this kit ; not necessary.
                #~assets.Asset.id.in_(assets_already_in_this_kit)
            )
            .all()
        )
    superassets_categories_in_kit_structure = []
    for superasset_category in kit.asset_kit_structure.type_of_superassets:
        superasset_cat = (
            meta.session.query(assets.SuperAssetCategory.id)
                .filter(assets.SuperAssetCategory.id == superasset_category.id)
                .one()
            )
        superassets_categories_in_kit_structure.append(superasset_cat)

    superassets_to_display = (
        meta.session.query(assets.SuperAsset)
            .filter(
                # SuperAsset already in use
                assets.SuperAsset.end_of_use.is_(None),
                assets.SuperAsset.end_use_reason ==
                    constants.END_USE_REASON_IN_USE_STOCK,
                # SuperAsset element of superasset_categories listed by 
                # kit_structure
                assets.SuperAsset.superasset_category_id.in_(
                    superassets_categories_in_kit_structure),
                # not element of active kit
                ~assets.SuperAsset.id.in_(assets_id_in_others_kits)
               )
            .all()
        )

    return render_template('update_kit.html', assets=assets_to_display, 
                    superassets=superassets_to_display, kit=kit)
