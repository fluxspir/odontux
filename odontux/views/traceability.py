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
                    DateField,
                    validators)

from odontux import constants, checks
from odontux.models import meta, traceability
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

class SterilizationCycle(Form):
    id = HiddenField(_('id'))
    user_id = SelectField(_('Operator of sterilization cycle'), coerce=int)
    sterilizator_id = SelectField(_('Sterilizator'), coerce=int)
    cycle_type_id = SelectField(_('Cycle Type'), coerce = int)
    cycle_mode_id = SelectField(_('Cycle Mode'), coerce = int)
    complement_id = SelectField(_('Complement'), coerce = int)
    reference = TextField(_('Reference'), [validators.Optional()])
    document = TextField(_('Path to document'), [validators.Optional()])

class SimplifiedTraceabilityForm(Form):
    id = HiddenField(_('id'))
    number_of_items = IntegerField(_('Number of Items'),
                                                    [validators.Required()])
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                default=90)

class CompleteTraceabilityForm(Form):
    id = HiddenField(_('id'))
    item_id = SelectField(_('item'), coerce=int)
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                    default=90)

def get_sterilization_cycle_mode_field_list():
    return [ "name", "heat_type", "temperature", "pressure", "comment" ]

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
                                ste_cycle_modess=ste_cycle_modes)



@app.route('/add/sterilization_cycle/', methods=["GET", "POST"])
def add_sterilization_cycle():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    pass

