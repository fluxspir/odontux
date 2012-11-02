# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, administration
from odontux.secret import SECRET_KEY
from odontux.odonweb import app
from gettext import gettext as _

from odontux.views.log import index

@app.route('/patient/')
def allpatients():
    patients = meta.session.query(administration.Patient).all()
    return render_template('search.html', patients=patients)

@app.route('/patient/<int:patient_id>/')
def patient(patient_id):
    patient = meta.session.query(administration.Patient)\
              .filter(administration.Patient.id == patient_id)\
              .one()

    if patient:
        session['patient_id'] = patient_id
        age = patient.age()
        birthday = patient.is_birthday()
        return render_template('patient_file.html', session=session,
                               patient=patient, age=age, birthday=birthday)
