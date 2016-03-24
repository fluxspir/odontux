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
from odontux.models import meta, traceability, assets, users, act
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.log import index

class SterilizationCycleTypeForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Sterilization Cycle Type Name'), [validators.Required(
                            message=_('Sterilization cycle name required'))])

class SterilizationComplementForm(Form):
    complement = TextField(_('Test, conforme ou non ?'), [validators.Required(
                    message=_('Type de test utilisé, et conformité ou non'))])

class SterilizationCycleModeForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Sterilization Cycle Mode Name'), [validators.Required(
                        message=_('Sterilization cycle mode name required'))])
    heat_type = TextField(_('Heat Type'), [validators.Required(
                            message=_('Heat Type required'))])
    temperature = DecimalField(_('Temperature'), [validators.Required()])
    pressure = DecimalField(_('Pressure'))
    sterilization_duration = IntegerField(_('Sterilization duration in minutes'
                                            ), [validators.Required()])
    comment = TextAreaField(_('Comments'))

class SterilizationCycleForm(Form):
    id = HiddenField(_('id'))
    user_id = SelectField(_('Operator of sterilization cycle'), coerce=int)
    sterilizer_id = SelectField(_('Sterilizer'), coerce=int)
    cycle_type_id = SelectField(_('Cycle Type'), coerce = int)
    cycle_mode_id = SelectField(_('Cycle Mode'), coerce = int)
    cycle_complement_id = SelectField(_('Complement'), coerce = int)
    cycle_date = DateField(_('Date'), [validators.Required()])
    reference = TextField(_('Reference'), [validators.Optional()])
    document = TextField(_('Path to document'), [validators.Optional()])

class AssetSterilizedForm(Form):
    item_id = HiddenField(_('id'))
    item_type = HiddenField(_('type'))
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                default=90)

#class SimplifiedTraceabilityForm(Form):
#    id = HiddenField(_('id'))
#    number_of_items = IntegerField(_('Number of Items'),
#                                                    [validators.InputRequired()
#                                                    ])
#
#class CompleteTraceabilityForm(Form):
#    id = HiddenField(_('id'))
#    items_id = SelectMultipleField(_('items'), coerce=int)
#    validity = IntegerField(_('Validity in days'), [validators.Required()],
#                                                    default=90)
#
def get_sterilization_cycle_mode_field_list():
    return [ "name", "heat_type", "temperature", "pressure", "comment" ]

def get_sterilization_cycle_field_list():
    return [ "user_id", "sterilizer_id", "cycle_type_id", "cycle_mode_id",
                "cycle_complement_id", "reference", "document", "cycle_date" ]

def get_complete_traceability_field_list():
    return [ "item_id", "validity" ]

@app.route('/traceability/')
def traceability_portal():
    return render_template('traceability.html')

@app.route('/add/sterilization_cycle_type/', methods=["GET", "POST"])
def add_sterilization_cycle_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    ste_cycle_type_form = SterilizationCycleTypeForm(request.form)
    
    if request.method == "POST" and ste_cycle_type_form.validate():
        values = {
            'name': ste_cycle_type_form.name.data
            }
        new_ste_cycle_type = traceability.SterilizationCycleType(**values)
        meta.session.add(new_ste_cycle_type)
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle_type'))

    return render_template('add_sterilization_cycle_type.html',
                                    ste_cycle_type_form=ste_cycle_type_form)

@app.route('/update/sterilization_cycle_type?id=<int:ste_cycle_type_id>', 
                                                    methods=["GET", "POST"])
def update_sterilization_cycle_type(ste_cycle_type_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    ste_cycle_type = meta.session.query(traceability.SterilizationCycleType
                            ).filter(traceability.SterilizationCycleType.id == 
                                                    ste_cycle_type_id).one()

    ste_cycle_type_form = SterilizationCycleTypeForm(request.form)

    if request.method == "POST" and ste_cycle_type_form.validate():
        ste_cycle_type.name = ste_cycle_type_form.name.data
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle_type'))
    
    return render_template('/update_sterilization_cycle_type.html',
                            ste_cycle_type=ste_cycle_type,
                            ste_cycle_type_form=ste_cycle_type_form)
                        

@app.route('/list/sterilization_cycle_type/', methods=["GET", "POST"])
def list_sterilization_cycle_type():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycle_types = meta.session.query(traceability.SterilizationCycleType
                                                                        ).all()
    return render_template('list_sterilization_cycle_type.html',
                                ste_cycle_types=ste_cycle_types)

@app.route('/add/sterilization_complement/', methods=["GET", "POST"])
def add_sterilization_complement():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    ste_complement_form = SterilizationComplementForm(request.form)
    
    if request.method == "POST" and ste_complement_form.validate():
        values = {
            'complement': ste_complement_form.complement.data
            }
        new_ste_complement = traceability.SterilizationComplement(**values)
        meta.session.add(new_ste_complement)
        meta.session.commit()
        return redirect(url_for('list_sterilization_complement'))

    return render_template('add_sterilization_complement.html',
                                    ste_complement_form=ste_complement_form)

@app.route('/update/sterilization_complement?id=<int:ste_complement_id>', 
                                                    methods=["GET", "POST"])
def update_sterilization_complement(ste_complement_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    ste_complement = meta.session.query(traceability.SterilizationComplement
                        ).filter(traceability.SterilizationComplement.id == 
                                                   ste_complement_id).one()

    ste_complement_form = SterilizationComplementForm(request.form)

    if request.method == "POST" and ste_complement_form.validate():
        ste_complement.complement = ste_complement_form.complement.data
        meta.session.commit()
        return redirect(url_for('list_sterilization_complement'))
    
    return render_template('/update_sterilization_complement.html',
                            ste_complement=ste_complement,
                            ste_complement_form=ste_complement_form)
 
@app.route('/list/sterilization_complement/', methods=["GET"])
def list_sterilization_complement():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_complements = meta.session.query(traceability.SterilizationComplement
                                                                        ).all()
    return render_template('list_sterilization_complement.html',
                                ste_complements=ste_complements)


@app.route('/add_sterilization_cycle_mode/', methods=["GET", "POST"])
def add_sterilization_cycle_mode():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()

    ste_cycle_mode_form = SterilizationCycleModeForm(request.form)

    if request.method == "POST" and ste_cycle_mode_form.validate():
        values = { f: getattr(ste_cycle_mode_form, f).data
                    for f in get_sterilization_cycle_mode_field_list() }
        values['sterilization_duration'] = \
            datetime.timedelta( 0, 
                    ste_cycle_mode_form.sterilization_duration.data * 60)
        new_ste_cycle_mode = traceability.SterilizationCycleMode(**values)
        meta.session.add(new_ste_cycle_mode)
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle_mode'))

    return render_template('add_sterilization_cycle_mode.html',
                            ste_cycle_mode_form=ste_cycle_mode_form)

@app.route('/update/sterilization_cycle_mode?id=<int:ste_cycle_mode_id>', 
                                                    methods=["GET", "POST"])
def update_sterilization_cycle_mode(ste_cycle_mode_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    ste_cycle_mode = meta.session.query(traceability.SterilizationCycleMode
                        ).filter(traceability.SterilizationCycleMode.id == 
                                                   ste_cycle_mode_id).one()

    ste_cycle_mode_form = SterilizationCycleModeForm(request.form)

    if request.method == "POST" and ste_cycle_mode_form.validate():
        for f in get_sterilization_cycle_mode_field_list():
            setattr(ste_cycle_mode, f, getattr(ste_cycle_mode_form, f).data)
        ste_cycle_mode.sterilization_duration = \
            datetime.timedelta(
                    ste_cycle_mode_form.sterilization_duration.data * 60)
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle_mode'))
    
    return render_template('/update_sterilization_cycle_mode.html',
                            ste_cycle_mode=ste_cycle_mode,
                            ste_cycle_mode_form=ste_cycle_mode_form)
 

@app.route('/list/sterilization_cycle_mode/', methods=["GET"])
def list_sterilization_cycle_mode():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycle_modes = meta.session.query(traceability.SterilizationCycleMode
                                                                        ).all()
    return render_template('list_sterilization_cycle_mode.html',
                                ste_cycle_modes=ste_cycle_modes)

def get_ste_cycle_form_user_id_choices():
    return meta.session.query(users.OdontuxUser.id, users.OdontuxUser.username
                                        ).filter(users.OdontuxUser.role.in_([
                                                constants.ROLE_DENTIST,
                                                constants.ROLE_ASSISTANT,
                                                constants.ROLE_NURSE ]) ).all()
                                                
def get_ste_cycle_form_sterilizer_id_choices():
    ste_cycle_form_list = []

    query = meta.session.query(assets.DeviceCategory).filter(
                            assets.DeviceCategory.sterilizer == True).all()
    for q in query:
        device_list = meta.session.query(assets.Device).filter(
                                assets.Device.asset_category_id == q.id).all()
        for dev in device_list:
            ste_cycle_form_list.append( (dev.id, q.commercial_name) )

    return ste_cycle_form_list
#        
#    return meta.session.query(assets.Device.id, 
#                            assets.DeviceCategory.commercial_name
#                    ).filter(assets.DeviceCategory.sterilizer == True
#                            ).all()
#


def get_ste_cycle_form_cycle_type_id_choices():
    return meta.session.query(traceability.SterilizationCycleType.id,
                                traceability.SterilizationCycleType.name).all()

def get_ste_cycle_form_cycle_mode_id_choices():
    return meta.session.query(traceability.SterilizationCycleMode.id,
                                traceability.SterilizationCycleMode.name).all()

def get_ste_cycle_form_cycle_complement_id_choices():
    return meta.session.query(traceability.SterilizationComplement.id,
                        traceability.SterilizationComplement.complement).all()

def get_assets_list_for_sterilization_cycle():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()

    assets_list = {
        "assets": [],
        "kits": []
        }

    query_kits = (
        meta.session.query(assets.AssetKit)
            .filter(assets.AssetKit.end_of_use.is_(None),
                    assets.AssetKit.end_use_reason ==
                                        constants.END_USE_REASON_IN_USE_STOCK,
                    assets.AssetKit.appointment_id.is_(None)
            ).join(assets.AssetKitStructure)
                .order_by(
                assets.AssetKitStructure.name,
                assets.AssetKit.id
                )
        )

    query_assets = (
        meta.session.query(assets.Asset)
            # the asset hasn't a thow_away date : it's probably in service
            # the asset is still marked : in use or in stock
            # Asset is in use, not in stock
            .filter(assets.Asset.end_of_use.is_(None),
                    assets.Asset.end_use_reason ==
                                        constants.END_USE_REASON_IN_USE_STOCK,
                    assets.Asset.start_of_use.isnot(None)
                )

            # Asset may be a "device"
            #.filter(assets.Asset.type == "device") # MAYBE UPDATE TO NOT SO DEVICE

            # the asset is something "sterilizable"
            #.filter(assets.Asset.is_sterilizable() == True)    # NOT WORKING
            .filter(assets.Asset.asset_category_id.in_(
                meta.session.query(assets.DeviceCategory.id)
                    .filter(assets.DeviceCategory.sterilizable == True)
                    )
                )

            # The asset isn't element of a kit.
            #.filter(assets.Asset.element_of_kit() == False)    # NOT WORKING
            # WILL BE DONE AFTER THE QUERY.

            # Below, we are eliminating assets already sterilized that don't 
            # need immediate sterilization
            .filter(or_(
                # The asset had been sterilized but wasn't use in an 
                # appointment and its sterilization expiration date is passed. 
                assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                        .filter(traceability.AssetSterilized.appointment_id.is_
                                                                        (None))
                        .filter(traceability.AssetSterilized.expiration_date <=
                                                        datetime.date.today()
                                )
                        ),
                # The asset never was Sterilized
                ~assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    ),
                # the asset doesn't exist in the sterilized environment without
                # an appointment_id correlation, which means it could be 
                # sterilized
                ~assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                        .filter(traceability.AssetSterilized.appointment_id.is_
                                                                        (None))
                        )
                    )
                ).join(assets.AssetCategory, act.Specialty)
                    .order_by(
                        act.Specialty.name,
                        assets.AssetCategory.brand,
                        assets.AssetCategory.commercial_name,
                        assets.Asset.id,
                        assets.Asset.acquisition_date,
                        assets.Asset.start_of_use
                        )
            )

    for kit in query_kits.all():
        assets_list['kits'].append(kit)
    for asset in query_assets.all():
        if not asset.element_of_kit():
            assets_list['assets'].append(asset)

    return assets_list

@app.route('/remove/asset_from_sterilization', methods=["POST"])
def remove_asset_from_sterilization():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    form = AssetSterilizedForm(request.form)
    if form.validate():
        pdb.set_trace() 
        if form.item_type.data == "kit":
            session['assets_to_sterilize'] = [
                (t, a_id, v) for (t, a_id, v) in session['assets_to_sterilize']
                if t == "k" and not a_id == form.item_id.data ]
            pdb.set_trace() 
        if form.item_type.data == "asset":
            session['assets_to_sterilize'] = [
                (t, a_id, v) for (t, a_id, v) in session['assets_to_sterilize']
                if t == "a" and not a_id == form.item_id.data ]

    return redirect(url_for('create_sterilization_list'))

@app.route('/create/sterilization_list', methods=["GET", "POST"])
def create_sterilization_list():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()

    if not 'assets_to_sterilize' in session:
        return redirect(url_for('add_sterilization_cycle'))
    # create list of asset to sterilize with their own form,
    # and own datas
    sterilize_assets_list = { "kits": [], "assets": [] }
    for ( t, a_id, v) in session['assets_to_sterilize']:
        form = AssetSterilizedForm(request.form)
        form.item_id.data = a_id
        form.validity.data = v
        if t == "a":
            asset = ( meta.session.query(assets.Asset)
                        .filter(assets.Asset.id == a_id).one() )
            form.item_type.data = "asset"
            sterilize_assets_list['assets'].append( (asset, form) )
        if t == "k":
            kit = ( meta.session.query(assets.AssetKit)
                        .filter(assets.AssetKit.id == a_id).one() )
            form.item_type.data = "kit"
            sterilize_assets_list['kits'].append( (kit, form) )
    
    form = AssetSterilizedForm(request.form)

    if request.method == 'POST' and form.validate():
        if form.item_type.data == "kit":
            kit = ( meta.session.query(assets.AssetKit)
                        .filter(assets.AssetKit.id == form.item_id.data)
                        .one()
                    )
            session['assets_to_sterilize'].append(
                                        ("k", kit.id, form.validity.data))
            sterilize_assets_list['kits'].append( (kit, form) )
        if form.item_type.data == "asset":
            asset = ( meta.session.query(assets.Asset)
                        .filter(assets.Asset.id == form.item_id.data)
                        .one()
                    )
            session['assets_to_sterilize'].append(
                                        ("a", asset.id, form.validity.data))
            sterilize_assets_list['assets'].append( (asset, form) )

        return redirect(url_for('create_sterilization_list'))

    # get list of assets
    assets_list = get_assets_list_for_sterilization_cycle()
    # each asset has his own form, with own datas.
    # creation of a new  with asset and form.
    assets_form_list = { "kits": [], "assets": [] }

    # list des kit_id to sterilize and asset_id
    ste_kit_id_list = []
    ste_asset_id_list = []
    for item in sterilize_assets_list['kits']:
        ste_kit_id_list.append(item[0].id)
    for item in sterilize_assets_list['assets']:
        ste_asset_id_list.append(item[0].id)
    # creation of the kits' forms.
    for kit in assets_list['kits']:
        if kit.id not in ste_kit_id_list:
            form = AssetSterilizedForm(request.form)
            form.item_id.data = kit.id
            form.item_type.data = "kit"
            form.validity.data = int(
                    kit.asset_kit_structure.validity.total_seconds() / 86400)
            assets_form_list["kits"].append((kit, form))
    # creation of the assets' forms.
    for asset in assets_list['assets']:
        if asset.id not in ste_asset_id_list:
            form = AssetSterilizedForm(request.form)
            form.item_id.data = asset.id
            form.item_type.data = "asset"
            form.validity.data = int(
                    asset.asset_category.validity.total_seconds() / 86400)
            assets_form_list['assets'].append((asset, form))
    
    return render_template('select_assets_for_sterilization.html',
                                assets_list=assets_form_list,
                                sterilize_assets_list=sterilize_assets_list)

@app.route('/add/sterilization_cycle/', methods=["GET", "POST"])
def add_sterilization_cycle():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycle_form = SterilizationCycleForm(request.form)

    if not 'assets_to_sterilize' in session:
        # session['assets_to_sterilize'] = list of asset_to_sterilize
        # asset_to_sterilize = ( type, {asset,kit}_id, validity_in_days )
        # type = "a" ou "k" ou None
        # asset_id = id of the asset/kit ; or None
        # validity in days
        session['assets_to_sterilize'] = []

    if ( request.method == "POST" and ste_cycle_form.validate() 
                           and simple_traceability_form.validate() ):
        
        values = { f: getattr(ste_cycle_form, f).data 
                    for f in get_sterilization_cycle_field_list() }
        
        new_sterilization_cycle = traceability.SterilizationCycle(**values)
        meta.session.add(new_sterilization_cycle)
        meta.session.commit()
        
        for asset in session['assets_to_sterilize']:
            values = {}
            values['sterilization_cycle_id'] = new_sterilization_cycle.id
            values['expiration_date'] = datetime.date(
                                        new_sterilization_cycle.cycle_date + 
                                        datetime.timedelta(asset[3]))
            if asset[0] == "a":
                values['asset_id'] = asset[1]
            elif asset[0] == "k":
                values['kit_id'] = asset[1]
            else:
                pass
            new_asset_sterilized = traceability.AssetSterilized(**values)
            meta.session.add(new_asset_sterilized)
            meta.session.commit()
    
        session['assets_to_sterilize'].pop()
        return redirect(url_for('list_sterilization_cycle'))

    ste_cycle_form.user_id.choices = get_ste_cycle_form_user_id_choices()
    ste_cycle_form.sterilizer_id.choices = \
                            get_ste_cycle_form_sterilizer_id_choices()
    ste_cycle_form.cycle_type_id.choices = \
                            get_ste_cycle_form_cycle_type_id_choices()
    ste_cycle_form.cycle_mode_id.choices = \
                            get_ste_cycle_form_cycle_mode_id_choices()
    ste_cycle_form.cycle_complement_id.choices = \
                            get_ste_cycle_form_cycle_complement_id_choices()

    #assets_list = get_assets_list_for_sterilization_cycle()
    return render_template('add_sterilization_cycle.html',
                        ste_cycle_form=ste_cycle_form)

@app.route('/list/sterilization_cycle/', methods=['GET', 'POST'])
def list_sterilization_cycle():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycles = meta.session.query(traceability.SterilizationCycle).all()
    
    return render_template('list_sterilization_cycle.html',
                                            ste_cycles=ste_cycles)

@app.route('/update/sterilization_cycle?id=<int:ste_cycle_id>', 
                                                    methods=['GET', 'POST'])
def update_sterilization_cycle(ste_cycle_id):
    pass


