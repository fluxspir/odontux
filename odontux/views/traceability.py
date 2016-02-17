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
from odontux.models import meta, assets, administration, users
from odontux.odonweb import app
from odontux.views import forms
from odontux.views.log import index

class SterilizationCycleTypeForm(Form):
    name = TextField(_('Sterilization Cycle Type Name'), [validators.Required(
                            message=_('Sterilization cycle name required'))])

class SterilizationComplementForm(Form):
    complement = TextField(_('Test, conforme ou non ?'), [validators.Required(
                    message=_('Type de test utilisé, et conformité ou non'))])

class SterilizationCycleModeForm(Form):
    name = TextField(_('Sterilization Cycle Mode Name'), [validators.Required(
                        message=_('Sterilization cycle mode name required'))])
    heat_type = TextField(_('Heat Type'), [validators.Required(
                            message=_('Heat Type required'))])
    temperature = DecimalField(_('Temperature'), [validators.Required()])
    pressure = DecimalField(_('Pressure'))
    sterilization_duration = IntegerField(_('Sterilization duration'), 
                                                [validators.Required()])
    comment = TextAreaField(_('Comments'))

class SterilizationCycle(Form):
    user_id = SelectField(_('Operator of sterilization cycle'), coerce=int)
    sterilizator_id = SelectField(_('Sterilizator'), coerce=int)
    cycle_type_id = SelectField(_('Cycle Type'), coerce = int)
    cycle_mode_id = SelectField(_('Cycle Mode'), coerce = int)
    complement_id = SelectField(_('Complement'), coerce = int)
    reference = TextField(_('Reference'), [validators.Optional()])
    document = TextField(_('Path to document'), [validators.Optional()])

class SimplifiedTraceabilityForm(Form):
    number_of_items = IntegerField(_('Number of Items'),
                                                    [validators.Required()])
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                default=90)

class CompleteTraceabilityForm(Form):
    item_id = SelectField(_('item'), coerce=int)
    validity = IntegerField(_('Validity in days'), [validators.Required()],
                                                    default=90)


