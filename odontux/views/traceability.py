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
from odontux.models import meta, traceability, assets, users
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

class SimplifiedTraceabilityForm(Form):
    id = HiddenField(_('id'))
    number_of_items = IntegerField(_('Number of Items'),
                                                    [validators.InputRequired()
                                                    ])
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                default=90)

class CompleteTraceabilityForm(Form):
    id = HiddenField(_('id'))
    items_id = SelectMultipleField(_('items'), coerce=int)
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                    default=90)

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

@app.route('/add/simplified_traceability/', methods=["GET", "POST"])
def add_simplified_traceability():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    ste_cycle_form = SterilizationCycleForm(request.form)
    ste_cycle_form.user_id.choices = get_ste_cycle_form_user_id_choices()
    ste_cycle_form.sterilizer_id.choices = \
                            get_ste_cycle_form_sterilizer_id_choices()
    ste_cycle_form.cycle_type_id.choices = \
                            get_ste_cycle_form_cycle_type_id_choices()
    ste_cycle_form.cycle_mode_id.choices = \
                            get_ste_cycle_form_cycle_mode_id_choices()
    ste_cycle_form.cycle_complement_id.choices = \
                            get_ste_cycle_form_cycle_complement_id_choices()

    simple_traceability_form = SimplifiedTraceabilityForm(request.form)

    if ( request.method == "POST" and ste_cycle_form.validate() 
                           and simple_traceability_form.validate() ):
        
        values = { f: getattr(ste_cycle_form, f).data 
                    for f in get_sterilization_cycle_field_list() }
        
        values['expiration_date'] = ( ste_cycle_form.cycle_date.data +
                    datetime.timedelta(simple_traceability_form.validity.data))
                                        
        values['number_of_items'] = \
                                simple_traceability_form.number_of_items.data

        new_simple_traceability = traceability.SimplifiedTraceability(**values)
        meta.session.add(new_simple_traceability)
        meta.session.commit()
        return redirect(url_for('list_sterilization_cycle'))

    return render_template('add_simplified_traceability.html',
                        ste_cycle_form=ste_cycle_form,
                        simple_traceability_form=simple_traceability_form)

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

@app.route('/update_assets_in_complete_traceability/')
def update_assets_in_complete_traceability():
    pass

@app.route('/select/assets_for_complete_traceability/', methods=['GET', 'POST'])
def select_assets_for_complete_traceability():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()

    if request.method == 'POST':
        pass

    assets_list = []

    query = (
        meta.session.query(assets.Asset).join(traceability.AssetSterilized)
            # the asset hasn't a thow_away date
            .filter(assets.Asset.end_of_use == None)
            # the asset is still in use or in stock
            .filter(assets.Asset.end_use_reason ==
                                        constants.END_USE_REASON_IN_USE_STOCK)
            # the asset is a device marked as sterilizable
            .filter(assets.DeviceCategory.sterilizable == True)

            .filter(or_(
                # the sterilized asset wasn't use on an appointment but its 
                # sterilization expiration date is passed.
                and_(
                    traceability.AssetSterilized.appointment_id.is_(None),
                    traceability.AssetSterilized.expiration_date <= 
                                                        datetime.date.today()
                    ),
                # the asset doesn't exist in the sterilized environment without
                # an appointment_id correlation, which means it could be 
                # sterilized
                traceability.AssetSterilized.appointment_id.isnot(None)
                )
            )
            # the asset can't be in a kit that...
            .filter(~assets.Asset.id.in_(
                meta.session.query(assets.AssetKit).join(
                                                        assets.AssetKit.assets)
                    # ... has not been use
                    .filter(assets.AssetKit.end_of_use.is_(None))
                    .filter(assets.AssetKit.end_use_reason !=
                                        constants.END_USE_REASON_IN_USE_STOCK)
                    .filter(assets.AssetKit.appointment_id.is_(None))
                    )
                )
    )
    pdb.set_trace()

#    kits = (
#        meta.session.query(assets.AssetKit)
#            .filter(assets.AssetKit.end_of_use == None)
#            .filter(assets.AssetKit.end_use_reason ==\
#                            constants.END_USE_REASON_IN_USE_STOCK)
#            all()
#    )
#    if kits:
#        for kit in kits:
#        query = query.filter(assets.Asset.id != kit.asset_id
#
    return render_template('select_assets_for_complete_traceability.html',
                                assets_list=assets_list)



@app.route('/add/complete_traceability/', methods=["GET", "POST"])
def add_complete_traceability():
    pass
#    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
#                        constants.ROLE_ASSISTANT ]
#    if session['role'] not in authorized_roles:
#        return redirect(url_for('index'))
#
#    checks.quit_patient_file()
#    checks.quit_appointment()
#    
#    ste_cycle_form = SterilizationCycleForm(request.form)
#    ste_cycle_form.user_id.choices = get_ste_cycle_form_user_id_choices()
#    ste_cycle_form.sterilizer_id.choices = \
#                            get_ste_cycle_form_sterilizer_id_choices()
#    ste_cycle_form.cycle_type_id.choices = \
#                            get_ste_cycle_form_cycle_type_id_choices()
#    ste_cycle_form.cycle_mode_id.choices = \
#                            get_ste_cycle_form_cycle_mode_id_choices()
#    ste_cycle_form.cycle_complement_id.choices = \
#                            get_ste_cycle_form_cycle_complement_id_choices()
#
#    complete_traceability_form = CompleteTraceabilityForm(request.form)
#
#
#    if ( request.method == "POST" and ste_cycle_form.validate() 
#                           and complete_traceability_form.validate() ):
#        
#        values = { f: getattr(ste_cycle_form, f).data 
#                    for f in get_sterilization_cycle_field_list() }
#        
#        values['expiration_date'] = ( ste_cycle_form.cycle_date.data +
#                    datetime.timedelta(simple_traceability_form.validity.data))
#                                        
#
#        new_complete_traceability = traceability.CompleteTraceability(**values)
#        meta.session.add(new_complete_traceability)
#        meta.session.commit()
#        return redirect(url_for('list_sterilization_cycle'))
#
#    return render_template('add_complete_traceability.html',
#                        ste_cycle_form=ste_cycle_form,
#                        complete_traceability_form=complete_traceability_form)
#
#
