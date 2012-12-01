# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

from flask import session, redirect, url_for, request, render_template
from wtforms import Form, HiddenField, TextField, TextAreaField, validators

from odontux import constants, checks
from odontux.views import forms
from odontux.models import meta, medication
from odontux.odonweb import app
from odontux.views.log import index
from odontux.views.forms import DateField

from gettext import gettext as _

class DrugPrescribedForm(Form):
    drug_id = HiddenField('id')
    alias = TextField(_('alias'))
    molecule = TextField(_('molecule'), [validators.Required(_("Specify drug "
                                        "name please"))])
    packaging = TextField(_('packaging'), [validators.Required(_("Please tell "
                                        "how the drug in packaged"))])
    posologia = TextField(_('posologia'), [validators.Required(_("Please tell "
                            "the posologia the patient might take"))])
    dayssupply = TextField(_('daysupply'), [validators.Required(_("Please tell"
                            " for how long the patient need to be under "
                            "medication"))])
    comments = TextField(_('comments'))

class PrescriptionForm(Form):
    dentist_id = HiddenField(_('dentist_id'), [validators.Required(_(
                                "Dentist_id must be provide to make a "
                                "prescription"))])
    patient_id = HiddenField(_('patient_id'), [validators.Required(_(
                                "Patient_id must be provide to make a "
                                "prescription"))])
    appointment_id = HiddenField(_("appointment_id"))
    time_stamp = DateField(_('time_stamp'))

class PrescribedDrugReference(Form):
    prescription_id = HiddenField(_('prescription_id'), [validators.Required(_(
                                "Must precise which is the prescription"))])
    drug_id = HiddenField(_("drug_id"), [validators.Required(_("Must tell the "
                                        "drug prescribed"))])

def _get_drug_prescribed_fields():
    return [ "alias", "molecule", "packaging", "posologia", "dayssupply", 
             "comments" ]

@app.route('/drugs/')
def list_drugs():
    # Administrator and secretaries shouldn't be allowed to sneak into
    # medications, as it isn't in their area of work.
    if (session['role'] == constants.ROLE_SECRETARY 
        or session['role'] == constants.ROLE_ADMIN):
        return redirect(url_for('index'))
    drugs = meta.session.query(medication.DrugPrescribed).all()
    if session['patient_id']:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = ""
    return render_template('list_drugs.html', drugs=drugs, patient=patient)

@app.route('/drugs/update/', methods=['GET', 'POST'])
def update_drug():
    # Only a dentist should be allowed to update drugs.
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('list_drugs'))

    if session['patient_id']:
        patient = checksls.get_patient(session['patient_id'])
    else:
        patient=""

    drug_fields = _get_drug_prescribed_fields()
    drug_form = DrugPrescribedForm(request.form)
    if request.method == 'POST' and drug_form.validate():
        # Get the drug to update
        drug = meta.session.query(medication.DrugPrescribed)\
            .filter(medication.DrugPrescribed.id == drug_form.drug_id.data)\
            .one()
        for f in drug_fields:
            setattr(drug, f, getattr(drug_form, f).data)
        meta.session.commit()
        return redirect(url_for('update_drug', patient=patient))

    drugs = meta.session.query(medication.DrugPrescribed).all()
    return render_template('update_drugs.html',
                            patient=patient,
                            drugs=drugs,
                            drug_form=drug_form
                           )

@app.route('/drugs/delete/', methods=['POST'])
def delete_drug():
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('list_drugs'))

    if session['patient_id']:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = ""

    drug_form = DrugPrescribedForm(request.form)
    drug = meta.session.query(medication.DrugPrescribed)\
        .filter(medication.DrugPrescribed.id == drug_form.drug_id.data)\
        .one()
    meta.session.delete(drug)
    meta.session.commit()
    return redirect(url_for('update_drug', patient=patient))

@app.route('/drugs/add/', methods=['POST'])
def add_drug():
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('list_drugs'))

    if session['patient_id']:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = ""

    drug_fields = _get_drug_prescribed_fields()
    drug_form = DrugPrescribedForm(request.form)
    if (not request.method == 'POST' 
        or not drug_form.validate()):
        return redirect(url_for('update_form'))
    args = {f: getattr(drug_form, f).data for f in drug_fields}
    new_drug = medication.DrugPrescribed(**args)
    meta.session.add(new_drug)
    meta.session.commit()
    return redirect(url_for('update_drug', patient=patient))

@app.route('/patient/make_prescription/', methods=['GET', 'POST'])
def make_prescription():
    if (not session['patient_id'] 
        or not session['role'] == constants.ROLE_DENTIST
       ):
        #or not session['appointment']
        return redirect(url_for('list_drugs'))
    pass 
    #TODO
