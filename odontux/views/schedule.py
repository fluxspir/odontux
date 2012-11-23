# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#


from flask import render_template, request 
from wtforms import (Form, HiddenField, BooleanField, TextAreaField, TextField,
                    validators)
from gettext import gettext as _

from odontux.odonweb import app
from odontux.models import meta, schedule
from odontux.views.forms import DateField, TimeField

class AppointmentForm(Form):
    patient_id = HiddenField('patient_id')
    dentist_id = HiddenField('dentist_id')
    emergency = BooleanField(_('emergency'))
    reason = TextAreaField(_('reason'))
    diagnostic = TextAreaField(_('diagnostic'))
    treatment = TextAreaField(_('treatment'))
    prognostic = TextAreaField(_('prognostic'))
    advise = TextAreaField(_('advise'))
    next_appointment = TextAreaField(_('next_appointment'))

class AgendaForm(Form):
    """ """
    #TODO : validators for time, either duration or endtime must be provided...
    appointment_id = HiddenField('appointment_id')
    day = DateField(_('day'), [validators.Required(_('Please specify '
                                'which day the appointment occurs'))])
    starttime = TimeField(_('starttime'), [validators.Required(_('Please '
                                'tell which time it started'))])
    duration = TimeField(_('duration'))
    endtime = TimeField(_('endtime'))

@app.route('/agenda/')
def agenda():
    return render_template('agenda.html', agenda_form=AgendaForm(request.form))
