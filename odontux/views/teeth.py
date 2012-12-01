# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/29
# v0.5
# Licence BSD
#

from flask import session, render_template, redirect, url_for, request

from odontux import constants, checks
from odontux.odonweb import app
from odontux.views import forms
from odontux.models import meta 
from odontux.views.log import index


@app.route('/patient/teeth/')
def list_teeth():
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('index'))

    patient = checks.get_patient(session['patient_id'])
    appointment = checks.get_appointment()

    return render_template('list_teeth.html', patient=patient, 
                            appointment=appointment)


