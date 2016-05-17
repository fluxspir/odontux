# -*- coding: utf-8 -*-
# Franck Labadille
# 2016-02-02
# v0.6
# Licence BSD
#

import pdb
import datetime
import os
import cStringIO

from flask import ( session, render_template, request, redirect, url_for, 
                    jsonify, send_file, make_response )
import sqlalchemy
from sqlalchemy import and_, or_, desc
from gettext import gettext as _
from wtforms import (Form, IntegerField, TextField, PasswordField, HiddenField,
                    SelectField, BooleanField, TextAreaField, DecimalField,
                    DateField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, traceability, assets, users, act
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.assets import get_assets_in_superasset
from odontux.views.log import index

from reportlab.graphics.barcode import code128
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas


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
    cycle_type_id = SelectField(_('Cycle Type'), coerce=int)
    cycle_mode_id = SelectField(_('Cycle Mode'), coerce=int)
    cycle_complement_id = SelectField(_('Complement'), coerce=int)
    cycle_date = DateField(_('Date of sterilization cycle'), 
                            format='%Y-%m-%d',
                            validators=[validators.Required()] )
    reference = TextField(_('Reference'), [validators.Optional()])
    document = TextField(_('Path to document'), [validators.Optional()])

class AssetSterilizedForm(Form):
    item_id = HiddenField(_('id'))
    item_type = HiddenField(_('type'))
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                default=90)

class UncategorizedAssetSterilizedForm(Form):
    number = IntegerField(_('Number of uncategorized items'), 
                                                [validators.InputRequired()],
                                                    default=0)
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                default=90)

class StickerForm(Form):
    position = IntegerField(_('Position of the sticker ; Between 0 and 64'),
                                [validators.NumberRange(min=0, max=64, 
                                    message=_('Position between 0 and 64'))]
                                    )

def get_sterilization_cycle_mode_field_list():
    return [ "name", "heat_type", "temperature", "pressure", "comment" ]

def get_sterilization_cycle_field_list():
    return [ "user_id", "sterilizer_id", "cycle_type_id", "cycle_mode_id",
                "cycle_complement_id", "reference", "document", "cycle_date" ]

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
            datetime.timedelta(0,
                    ste_cycle_mode_form.sterilization_duration.data * 60)
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle_mode'))
    
    return render_template('/update_sterilization_cycle_mode.html',
                            ste_cycle_mode=ste_cycle_mode,
                            ste_cycle_mode_form=ste_cycle_mode_form,
                            int=int)
 

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
        "kits": [],
        "superassets": []
        }

    query_kits = (
        meta.session.query(assets.AssetKit)
            # The kit hasn't a throw away date : it's probably in service
            # The kit is still marked "in use or in stock"
            # The kit isn't linked to an appointment, which would mean it has
            # been use.
            .filter(assets.AssetKit.end_of_use.is_(None),
                    assets.AssetKit.end_use_reason ==
                                        constants.END_USE_REASON_IN_USE_STOCK,
                    assets.AssetKit.appointment_id.is_(None)
                )

            # Elimination of all kits that don't need sterilizations
            .filter(
                ~assets.AssetKit.id.in_(
                    meta.session.query(traceability.AssetSterilized.kit_id)
                    .filter(traceability.AssetSterilized.kit_id.isnot(None))
                    .filter(
                        traceability.AssetSterilized.expiration_date >
                                                        datetime.date.today()
                    )
                )
            )
            .join(assets.AssetKitStructure)
            .order_by(
                assets.AssetKitStructure.name,
                assets.AssetKit.id
                )
        )

    query_superassets = (
        meta.session.query(assets.SuperAsset)
            .filter(
                # The superasset wasn't already throw away
                assets.SuperAsset.end_of_use.is_(None),
                # the superasset still in use or stock
                assets.SuperAsset.end_use_reason ==
                    constants.END_USE_REASON_IN_USE_STOCK,
                # the superasset already in use
                assets.SuperAsset.start_of_use.isnot(None)
            )
            # SuperAsset isn't element of kit
            .filter(~assets.SuperAsset.id.in_(
                meta.session.query(assets.SuperAsset.id)
                .filter(assets.SuperAsset.kits.any(
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
            ))   
            # We are eliminating here all superassets that are ready to be use
            .filter(
                ~assets.SuperAsset.id.in_(
                    meta.session.query(
                                    traceability.AssetSterilized.superasset_id)
                    .filter(
                        traceability.AssetSterilized.superasset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date > 
                                                        datetime.date.today(),
                        traceability.AssetSterilized.sealed == True)
                        )
                    )
            # Here we're gonna eliminate superassets already sterilized
            .filter(or_(
                # expiration's date of sterilization expired :
                assets.SuperAsset.id.in_(
                    meta.session.query(
                                    traceability.AssetSterilized.superasset_id)
                    .filter(
                        traceability.AssetSterilized.superasset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date <=
                                                        datetime.date.today()
                            )
                        ),
                # The superasset has been used out of an appointment: broken seal
                assets.SuperAsset.id.in_(
                    meta.session.query(
                                    traceability.AssetSterilized.superasset_id)
                    .filter(
                        traceability.AssetSterilized.superasset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date >=
                                                        datetime.date.today(),
                        traceability.AssetSterilized.sealed == False)
                        ),
                # The superasset never was sterilized
                ~assets.SuperAsset.id.in_(
                    meta.session.query(
                                    traceability.AssetSterilized.superasset_id)
                    .filter(
                        traceability.AssetSterilized.superasset_id.isnot(None))
                    ),
                # The superasset doesn't exist in the sterilized environment 
                # without appointment_id correlation. It must be sterilized.
                ~assets.SuperAsset.id.in_(
                    meta.session.query(
                                    traceability.AssetSterilized.superasset_id)
                    .filter(
                        traceability.AssetSterilized.superasset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None)
                        )
                    )
                )
            )
            .join(assets.SuperAssetCategory)
            .order_by(
                assets.SuperAssetCategory.name,
                assets.SuperAsset.id
                )
        )
    
    assets_id_in_superasset = get_assets_in_superasset(return_id=True)
    assets_id_in_kit = (
        meta.session.query(assets.Asset.id)
            .filter(assets.Asset.kits.any(
                assets.AssetKit.id.in_(
                    meta.session.query(assets.AssetKit.id)
                        .filter(assets.AssetKit.end_of_use.is_(None),
                                assets.AssetKit.appointment_id.is_(None),
                                assets.AssetKit.end_use_reason ==
                                    constants.END_USE_REASON_IN_USE_STOCK
                                )
                            )
                        )
                    )
                .all()
                )
    
    query_assets = (
        meta.session.query(assets.Asset)
            # the asset hasn't a throw_away date : it's probably in service
            # the asset is still marked : in use or in stock
            # Asset is in use, not in stock
            .filter(assets.Asset.end_of_use.is_(None),
                    assets.Asset.end_use_reason ==
                                        constants.END_USE_REASON_IN_USE_STOCK,
                    assets.Asset.start_of_use.isnot(None)
                )
            # Asset may be a "device"
            #.filter(assets.Asset.type == "device") #MAYBE UPDATE TO ASSET

            # the asset is something "sterilizable"
            #.filter(assets.Asset.is_sterilizable() == True)    # NOT WORKING
            .filter(assets.Asset.asset_category_id.in_(
                meta.session.query(assets.DeviceCategory.id)
                    .filter(assets.DeviceCategory.sterilizable == True)
                    )
                )
            # The asset isn't element of a kit.
            .filter(~assets.Asset.id.in_(assets_id_in_kit))
            # We don't want assets in a superasset to appear.
            .filter(~assets.Asset.id.in_(assets_id_in_superasset))
            # SuperAsset are not considered assets this way
            .filter(~assets.Asset.id.in_(
                        meta.session.query(assets.SuperAsset.id).all()
                    )
                )

            # We are eliminating here all assets that are ready to be use
            .filter(
                ~assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    .filter(traceability.AssetSterilized.asset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date > 
                                                        datetime.date.today(),
                        traceability.AssetSterilized.sealed == True)
                        )
                    )
            # Below, we are eliminating assets already sterilized that don't 
            # need immediate sterilization
            .filter(or_(
                # The asset had been sterilized but wasn't use in an 
                # appointment and its sterilization expiration date is passed. 
                assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    .filter(traceability.AssetSterilized.asset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date <=
                                                        datetime.date.today()
                                )
                        ),
                # The asset has been used out of an appointment ; the seal is
                # broken.
                assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    .filter(traceability.AssetSterilized.asset_id.isnot(None),
                        traceability.AssetSterilized.appointment_id.is_(None),
                        traceability.AssetSterilized.expiration_date >=
                                                        datetime.date.today(),
                        traceability.AssetSterilized.sealed == False
                        )
                    ),
                # The asset never was Sterilized
                ~assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    .filter(traceability.AssetSterilized.asset_id.isnot(None))
                    ),
                # the asset doesn't exist in the sterilized environment without
                # an appointment_id correlation, which means it could be 
                # sterilized
                ~assets.Asset.id.in_(
                    meta.session.query(traceability.AssetSterilized.asset_id)
                    .filter(traceability.AssetSterilized.asset_id.isnot(None))
                    .filter(traceability.AssetSterilized.appointment_id.is_
                                                                        (None))
                        )
                    )
               )
                .join(assets.AssetCategory, act.Specialty)
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
        assets_list['assets'].append(asset)
    for superasset in query_superassets.all():
        assets_list['superassets'].append(superasset)
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
        if form.item_type.data == "kit":
            session['assets_to_sterilize'] = [
                (t, a_id, v) for (t, a_id, v) in session['assets_to_sterilize']
                if t == "k" and a_id != int(form.item_id.data)
                or t == "a" or t == "s" ]
        if form.item_type.data == "asset":
            session['assets_to_sterilize'] = [
                (t, a_id, v) for (t, a_id, v) in session['assets_to_sterilize']
                if t == "a" and not a_id == int(form.item_id.data) 
                or t == "k" or t == "s" ]
        if form.item_type.data == "superasset":
            session['assets_to_sterilize'] = [
                (t, a_id, v) for (t, a_id, v) in session['assets_to_sterilize']
                if t == "s" and not a_id == int(form.item_id.data)
                or t == "a" or t == "k" ]

    return redirect(url_for('create_sterilization_list'))

@app.route('/update/number_of_uncategorized', methods=['POST'])
def update_number_uncategorized():
    uncategorized_form = UncategorizedAssetSterilizedForm(request.form)
    if uncategorized_form.validate():
        session['uncategorized_assets_sterilization'] = (
                                        int(uncategorized_form.number.data),
                                        int(uncategorized_form.validity.data) )

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
    sterilize_assets_list = { "kits": [], "assets": [], "superassets": [] }
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
        if t == "s":
            superasset = (meta.session.query(assets.SuperAsset)
                        .filter(assets.SuperAsset.id == a_id).one() )
            form.item_type.data = "superasset"
            sterilize_assets_list['superassets'].append( (superasset, form) )

    form = AssetSterilizedForm(request.form)
    if request.method == 'POST' and form.validate(): 

        if form.item_type.data == "kit":
            kit = ( meta.session.query(assets.AssetKit)
                        .filter(assets.AssetKit.id == form.item_id.data)
                        .one()
                    )
            session['assets_to_sterilize'].append(
                                    ("k", kit.id, int(form.validity.data)))
            sterilize_assets_list['kits'].append( (kit, form) )
        if form.item_type.data == "asset":
            asset = ( meta.session.query(assets.Asset)
                        .filter(assets.Asset.id == form.item_id.data)
                        .one()
                    )
            session['assets_to_sterilize'].append(
                                    ("a", asset.id, int(form.validity.data)))
            sterilize_assets_list['assets'].append( (asset, form) )
        if form.item_type.data == "superasset":
            superasset = ( meta.session.query(assets.SuperAsset)
                        .filter(assets.SuperAsset.id == form.item_id.data)
                        .one()
                    )
            session['assets_to_sterilize'].append(
                                    ("s", superasset.id, 
                                        int(form.validity.data)))
            sterilize_assets_list['superassets'].append( (superasset, form) )

        return redirect(url_for('create_sterilization_list'))

    # get list of assets
    assets_list = get_assets_list_for_sterilization_cycle()
    # each asset has his own form, with own datas.
    # creation of a new  with asset and form.
    assets_form_list = { "kits": [], "assets": [], "superassets": [] }

    # list des kit_id to sterilize and asset_id
    ste_kit_id_list = []
    ste_asset_id_list = []
    ste_superasset_id_list = []
    for item in sterilize_assets_list['kits']:
        ste_kit_id_list.append(item[0].id)
    for item in sterilize_assets_list['assets']:
        ste_asset_id_list.append(item[0].id)
    for item in sterilize_assets_list['superassets']:
        ste_superasset_id_list.append(item[0].id)
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
    # creation of the superassets' forms.
    for superasset in assets_list['superassets']:
        if superasset.id not in ste_superasset_id_list:
            form = AssetSterilizedForm(request.form)
            form.item_id.data = superasset.id
            form.item_type.data = "superasset"
            form.validity.data = int(
                    superasset.superasset_category.validity.total_seconds() / 
                    86400)
            assets_form_list['superassets'].append((superasset, form))

    uncategorized_form = UncategorizedAssetSterilizedForm(request.form)
    if 'uncategorized_assets_sterilization' in session:
        uncategorized_form.number.data =\
                        int(session['uncategorized_assets_sterilization'][0])
        uncategorized_form.validity.data =\
                        int(session['uncategorized_assets_sterilization'][1])
    return render_template('select_assets_for_sterilization.html',
                                uncategorized_form=uncategorized_form,
                                assets_list=assets_form_list,
                                sterilize_assets_list=sterilize_assets_list)

@app.route('/add/sterilization_cycle/', methods=["GET", "POST"])
def add_sterilization_cycle():
    """
    session['assets_to_sterilize'] = list of asset_to_sterilize
        asset_to_sterilize = ( type, {asset,kit}_id, validity_in_days )
        type = "a" ou "k" ou None
        asset_id = id of the asset/kit ; or None
        validity in days

    session['uncategorized_assets_sterilization'] = 
        tuple( number_of_assets, validity_in days)
    """
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycle_form = SterilizationCycleForm(request.form)
    if not 'assets_to_sterilize' in session:
        session['assets_to_sterilize'] = []
        session['uncategorized_assets_sterilization'] = ( 0, 90 )
        return redirect(url_for('create_sterilization_list'))

 
    ste_cycle_form.user_id.choices = get_ste_cycle_form_user_id_choices()
    ste_cycle_form.sterilizer_id.choices = \
                            get_ste_cycle_form_sterilizer_id_choices()
    ste_cycle_form.cycle_type_id.choices = \
                            get_ste_cycle_form_cycle_type_id_choices()
    ste_cycle_form.cycle_mode_id.choices = \
                            get_ste_cycle_form_cycle_mode_id_choices()
    ste_cycle_form.cycle_complement_id.choices = \
                            get_ste_cycle_form_cycle_complement_id_choices()
   
    if ( request.method == "POST" and ste_cycle_form.validate() ):
        
        values = { f: getattr(ste_cycle_form, f).data 
                    for f in get_sterilization_cycle_field_list() }
        
        new_sterilization_cycle = traceability.SterilizationCycle(**values)
        meta.session.add(new_sterilization_cycle)
        meta.session.commit()
        
        while session['assets_to_sterilize']:
            asset = session['assets_to_sterilize'].pop()
            values = {}
            values['sterilization_cycle_id'] = new_sterilization_cycle.id
            values['expiration_date'] = ( new_sterilization_cycle.cycle_date +
                                                datetime.timedelta(asset[2]) )
            if asset[0] == "a":
                values['asset_id'] = asset[1]
            elif asset[0] == "k":
                values['kit_id'] = asset[1]
            elif asset[0] == "s":
                values['superasset_id'] = asset[1]
            else:
                pass
            new_asset_sterilized = traceability.AssetSterilized(**values)
            meta.session.add(new_asset_sterilized)
            meta.session.commit()
        else:
            session.pop('assets_to_sterilize')
        
        i = session['uncategorized_assets_sterilization'][0]
        while i:
            values= {}
            values['sterilization_cycle_id'] = new_sterilization_cycle.id
            values['expiration_date'] = ( new_sterilization_cycle.cycle_date +
                datetime.timedelta(session['uncategorized_assets_sterilization'][1])
                )
            new_uncat_asset_sterilized = traceability.AssetSterilized(**values)
            meta.session.add(new_uncat_asset_sterilized)
            meta.session.commit()
            i -= 1
        else:
            session.pop('uncategorized_assets_sterilization')
    
        return redirect(url_for('list_sterilization_cycle'))

    # {assets,kits}_to_sterilize are lists of tuple( asset_instance, form )
    # that we will send to the html_template in order it to be able to display
    # those informations.
    assets_to_sterilize = []
    kits_to_sterilize = []
    superassets_to_sterilize = []
    for (t, a_id, v) in session['assets_to_sterilize']:
        if t == "k":
            kits_to_sterilize.append( meta.session.query(assets.AssetKit)
                                .filter(assets.AssetKit.id == a_id).one() )
        if t == "a":
            assets_to_sterilize.append( meta.session.query(assets.Asset)
                                .filter(assets.Asset.id == a_id).one() )
        if t == "s":
            superassets_to_sterilize.append( 
                        meta.session.query(assets.SuperAsset)
                            .filter(assets.SuperAsset.id == a_id).one() )
           
    ste_cycle_form.cycle_date.data = datetime.date.today()
    return render_template('add_sterilization_cycle.html',
                        ste_cycle_form=ste_cycle_form,
                        assets_to_sterilize=assets_to_sterilize,
                        kits_to_sterilize=kits_to_sterilize,
                        superassets_to_sterilize=superassets_to_sterilize)

@app.route('/list/sterilization_cycle/', methods=['GET', 'POST'])
def list_sterilization_cycle():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycles = (
        meta.session.query(traceability.SterilizationCycle)
        .order_by(traceability.SterilizationCycle.cycle_date.desc())
        .order_by(traceability.SterilizationCycle.id.desc())
        .all()
        )
    
    return render_template('list_sterilization_cycle.html',
                                            ste_cycles=ste_cycles)

@app.route('/view/sterilization/cycle?id=<int:ste_cycle_id>')
def view_sterilization_cycle(ste_cycle_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
 
    ste_cycle = (
        meta.session.query(traceability.SterilizationCycle)
            .filter(traceability.SterilizationCycle.id == ste_cycle_id)
            .one()
        )

    query = (
        meta.session.query(traceability.AssetSterilized)
            .filter(traceability.AssetSterilized.sterilization_cycle_id == 
                                                                ste_cycle.id)
        )
    kits = query.filter(traceability.AssetSterilized.kit_id.isnot(None)).all()
    assets = query.filter(
                    traceability.AssetSterilized.asset_id.isnot(None)).all()
    superassets = query.filter(
                traceability.AssetSterilized.superasset_id.isnot(None)).all()
    unmarked = (
            query.filter(traceability.AssetSterilized.asset_id.is_(None),
                        traceability.AssetSterilized.kit_id.is_(None),
                        traceability.AssetSterilized.superasset_id.is_(None)
                        ).all()
        )
    sticker_position = (
        meta.session.query(users.Settings)
            .filter(users.Settings.key == "sticker_position")
            .one()
            .value
        )
    return render_template('view_sterilization_cycle.html', 
                                            ste_cycle=ste_cycle,
                                            kits=kits,
                                            superassets=superassets,
                                            assets=assets,
                                            unmarked=unmarked,
                                            sticker_position=sticker_position)

@app.route('/update/sticker_position?id=<int:ste_cycle_id>', 
                                                    methods=['GET', 'POST'])
def update_sticker_position(ste_cycle_id):
    """ ste_cycle_id to go back from where we came """
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    sticker_position = ( meta.session.query(users.Settings)
            .filter(users.Settings.key == "sticker_position")
            .one() )
    sticker_form = StickerForm(request.form)
    
    if request.method == 'POST' and sticker_form.validate():
        sticker_position.value = sticker_form.position.data
        meta.session.commit()
        return redirect(url_for('view_sterilization_cycle', 
                                                    ste_cycle_id=ste_cycle_id))

    sticker_form.position.data = sticker_position.value
    return render_template('update_sticker_position.html', 
                                                    sticker_form=sticker_form,
                                                    ste_cycle_id=ste_cycle_id)

def create_barcodes_a4_65(items, actual_position, draw=False):
    """
        items = list of assets
    """
    LAST = 64
    def _draw_table(draw=False):
        # For verification purpose ; won't appear in final
        if draw:
            c.setLineWidth(.3)
            cell_width = 38.2 * mm
            cell_height = 21 * mm
            h_s_b_c = 2.5 * mm  # Horizontal Space Between Cells

            c.line( hori_start, vert_start, hori_stop, vert_start) 
            c.line( hori_start, vert_stop, hori_stop, vert_stop)
            c.line( hori_start, vert_start, hori_start, vert_stop)
            c.line( hori_stop, vert_start, hori_stop, vert_stop)
            i = 1
            while i < 5:
                c.line( 
                    (hori_start + (i * cell_width) + ((i - 1) * h_s_b_c)), 
                    vert_start, 
                    (hori_start + i * cell_width + ( (i - 1) * h_s_b_c)), 
                    vert_stop 
                    )
                c.line( 
                    (hori_start + (i * cell_width) + ((i - 1 + 1) * h_s_b_c)),
                    vert_start, 
                    (hori_start + (i * cell_width) + ((i - 1 + 1 ) * h_s_b_c)),
                    vert_stop )
                i += 1

            i = 1
            while i < 13:
                c.line( 
                    hori_start, 
                    (vert_start + (i * cell_height)), 
                    hori_stop, 
                    (vert_start + i * (cell_height) ) 
                    )
                i += 1

    def _get_cell_coordonate(actual_loc):
        if actual_loc < 0:
            raise ValueError("Actual Location can't be negative")
        while actual_loc > LAST:
            actual_loc -= (LAST +1)
        return ( (actual_loc / 5), (actual_loc % 5) )

    output = cStringIO.StringIO()

    c = canvas.Canvas(output)
    #c = canvas.Canvas("odontux/static/barcode.pdf")
    c.setPageSize(A4)
   
    lmarg = rmarg = 4.5 * mm
    tmarg = bmarg = 10.5 * mm
    width_paper = 210 * mm
    height_paper = 297 * mm
    cell_width = 38.2 * mm
    cell_height = 21.2 * mm
    space_between_cell_horizontal = 2.5 * mm

    hori_start = lmarg
    hori_stop = width_paper - rmarg
    vert_start = bmarg
    vert_stop = height_paper - tmarg
    _draw_table(draw)


    for item in items:
        if item.asset:
            item_id = str(item.asset.id)
            item_name = item.asset.asset_category.commercial_name[:40]
        elif item.kit:
            item_id = str(item.kit.id)
            item_name = item.kit.asset_kit_structure.name[:40]
        elif item.superasset:
            item_id = str(item.superasset.id)
            item_name = item.superasset.superasset_category.name[:40]
        else:
            item_name = "Item without a name"

        ( row, col) = _get_cell_coordonate(actual_position)
        cell_x = ( (col * cell_width) + 
                    lmarg + 
                    ( (col - 1) * ( space_between_cell_horizontal) )
                )
        cell_y = ( (row * cell_height) + bmarg )
        
        barcode = code128.Code128(str(item.id).zfill(10), barWidth=(mm*0.33))  
        barcode.drawOn( c,
                        cell_x ,
                        (cell_y + (11 * mm) )
                    )
        c.setFont('Helvetica', 8)
        c.drawString ( (cell_x + (8 * mm)),
                        (cell_y + (8 * mm)),
                        str(item.id).zfill(10) + "  /  " + item_id )
        c.setFont('Helvetica', 10)
        c.drawString ( cell_x + (10 * mm),
                        cell_y + (4 * mm),
                        str(item.expiration_date)
                    )
        c.setFont('Helvetica', 6)
        
        c.drawString (cell_x + (5 * mm),
                        cell_y + (1.5 * mm),
                        item_name
                    )

        actual_position += 1
        if actual_position == (LAST + 1): 
            actual_position = 0
            c.showPage()

    c.showPage()
    c.save()
    pdf_out = output.getvalue()
    output.close()

    return (pdf_out, actual_position)

@app.route('/print/sterilization_stickers?id=int<ste_cycle_id>')
def print_sterilization_stickers(ste_cycle_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
 
    assets = (
        meta.session.query(traceability.AssetSterilized)
            .filter(traceability.AssetSterilized.sterilization_cycle_id.in_(
                meta.session.query(traceability.SterilizationCycle.id)
                    .filter(traceability.SterilizationCycle.id == ste_cycle_id)
                )
            ).all()
        )

    sticker_setting = (
        meta.session.query(users.Settings)
            .filter(users.Settings.key == "sticker_position")
            .one()
        )
    actual_position = int(sticker_setting.value)
    (pdf, new_position) = create_barcodes_a4_65(assets, actual_position, False)
    sticker_setting.value = str(new_position)
    meta.session.commit()

    response = make_response(pdf)
    #response.headers['Content-Disposition'] =\
    #                                   "attachment; filename='barcode.pdf"
    response.mimetype = 'application/pdf'
    return response


@app.route('/update/sterilization_cycle?id=<int:ste_cycle_id>', 
                                                    methods=['GET', 'POST'])
def update_sterilization_cycle(ste_cycle_id):
    """ 
    This method is not implemented really for normally not being used
    """
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('list_sterilization_cycle'))
    return redirect(url_for('list_sterilization_cycle'))
    ste_cycle = (
        meta.session.query(traceability.SterilizationCycle)
            .filter(traceability.SterilizationCycle.id == ste_cycle_id)
            .one()
        )


@app.route('/unseal/asset?id=<int:asset_sterilized_id>')
@app.route('/unseal/asset?id=<int:asset_sterilized_id>&aid=<int:appointment_id>')
def unseal_asset(asset_sterilized_id, appointment_id=None):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    asset_sterilized = (
        meta.session.query(traceability.AssetSterilized)
            .filter(traceability.AssetSterilized.id == asset_sterilized_id)
            .one()
        )
    if appointment_id:
        asset_sterilized.appointment_id = appointment_id
    asset_sterilized.sealed = False
    meta.session.commit()
    if asset_sterilized.asset_id:
        return redirect(url_for('view_asset',
                                asset_id=asset_sterilized.asset_id))
    elif asset_sterilized.superasset_id:
        return redirect(url_for('view_asset',
                                asset_id=asset_sterilized.superasset_id))
    elif asset_sterilized.kit_id:
        return redirect(url_for('view_kit',
                                kit_id=asset_sterilized.kit_id))
    else:
        return redirect(url_for('view_sterilization_cycle',
                        ste_cycle_id=asset_sterilized.sterilization_cycle_id))
