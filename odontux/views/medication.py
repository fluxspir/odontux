# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

import pdb
from flask import session, redirect, url_for, request, render_template
from wtforms import (Form, HiddenField, TextField, TextAreaField, DateField,
                    BooleanField, SelectField, validators )

from odontux import constants, checks
from odontux.views import forms
from odontux.models import meta, medication
from odontux.odonweb import app
from odontux.views.log import index

from gettext import gettext as _

class DrugFamilyForm(Form):
    drug_family_id = HiddenField(_('id'))
    name = TextField(_('Name'), [validators.Required()] )

class DrugPrescribedForm(Form):
    drug_id = HiddenField(_('id'))
    family_id = SelectField(_('Family'), coerce=int)
    alias = TextField(_('alias'), render_kw={'size':'8'})
    molecule = TextField(_('molecule'), [validators.Required(_("Specify drug "
                                        "name please"))])
    packaging = TextField(_('packaging'), [validators.Required(_("Please tell "
                                        "how the drug in packaged"))])
    posologia = TextField(_('posologia'), [validators.Required(_("Please tell "
                            "the posologia the patient might take"))])
    dayssupply = TextField(_('daysupply'), [validators.Required(_("Please tell"
                            " for how long the patient need to be under "
                            "medication"))], render_kw={'size':'4'})
    comments = TextField(_('comments'))
    special = BooleanField(_('special'))

class PrescriptionForm(Form):
    dentist_id = HiddenField(_('dentist_id'), [validators.Required(_(
                                "Dentist_id must be provide to make a "
                                "prescription"))])
    patient_id = HiddenField(_('patient_id'), [validators.Required(_(
                                "Patient_id must be provide to make a "
                                "prescription"))])
    appointment_id = HiddenField(_("appointment_id"))
    time_stamp = DateField(_('time_stamp'), [validators.Optional()])

class PrescribedDrugReference(Form):
    prescription_id = HiddenField(_('prescription_id'), [validators.Required(_(
                                "Must precise which is the prescription"))])
    drug_id = HiddenField(_("drug_id"), [validators.Required(_("Must tell the "
                                        "drug prescribed"))])

def _get_drug_prescribed_fields():
    return [ "alias", "molecule", "packaging", "posologia", "dayssupply", 
             "comments", "special", "family_id" ]

@app.route('/list/drug_family')
def list_drug_family():
    drug_families = ( meta.session.query(medication.DrugFamily)
                        .order_by(medication.DrugFamily.name)
                        .all()
    )
    return render_template('list_drug_family.html', 
                                                drug_families=drug_families)

@app.route('/add/drug_family', methods=['GET', 'POST'])
def add_drug_family():
    drug_family_form = DrugFamilyForm(request.form)
    if request.method == 'POST' and drug_family_form.validate():
        values = {
            'name': drug_family_form.name.data
        }
        new_drug_family = medication.DrugFamily(**values)
        meta.session.add(new_drug_family)
        meta.session.commit()
        return redirect(url_for('list_drug_family'))

    return render_template('add_drug_family.html',
                                    drug_family_form=drug_family_form)

@app.route('/update_drug_family?dfid=<int:drug_family_id>', 
                                                    methods=['GET', 'POST'])
def update_drug_family(drug_family_id):
    drug_family = (meta.session.query(medication.DrugFamily)
                        .filter(medication.DrugFamily.id == drug_family_id)
                        .one()
    )
    drug_family_form = DrugFamilyForm(request.form)

    if request.method == 'POST' and drug_family_form.validate():
        drug_family.name = drug_family_form.name.data
        meta.session.commit()
        return redirect(url_for('list_drug_family'))

    drug_family_form.drug_family_id.data = drug_family.id
    drug_family_form.name.data = drug_family.name
    return render_template('update_drug_family.html', 
                                            drug_family_form=drug_family_form)

@app.route('/list/drugs/')
def list_drugs():
    # Administrator and secretaries shouldn't be allowed to sneak into
    # medications, as it isn't in their area of work.
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    drugs = meta.session.query(medication.DrugPrescribed).all()
    if 'patient_id' in session:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = None
    return render_template('list_drugs.html', drugs=drugs, patient=patient)

@app.route('/drugs/update/', methods=['GET', 'POST'])
def update_drug():
    # Only a dentist should be allowed to update drugs.
    if session['role'] != constants.ROLE_DENTIST:
        return redirect(url_for('list_drugs'))

    if 'patient_id' in session:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = None

    drug_fields = _get_drug_prescribed_fields()
    drug_form = DrugPrescribedForm(request.form)
    drug_form.family_id.choices = [ (family.id, family.name) for family in
                        meta.session.query(medication.Family).all() ]
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

    if 'patient_id' in session:
        patient = checks.get_patient(session['patient_id'])
    else:
        patient = None

    drug_fields = _get_drug_prescribed_fields()
    drug_form = DrugPrescribedForm(request.form)
    drug_form.family_id.choices = [ (family.id, family.name) for family in
                        meta.session.query(medication.Family).all() ]
    if (not request.method == 'POST' 
        or not drug_form.validate()):
        return redirect(url_for('update_form'))
    args = {f: getattr(drug_form, f).data for f in drug_fields}
    new_drug = medication.DrugPrescribed(**args)
    meta.session.add(new_drug)
    meta.session.commit()
    return redirect(url_for('update_drug', patient=patient))

@app.route('/patient/choose_drugs_to_prescribe/?pid=<int:patient_id>'
                        '&aid=<int:appointment_id>', methods=['GET', 'POST'])
def choose_drugs_to_prescribe(patient_id, appointment_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)

    drugs = ( meta.session.query(medication.DrugPrescribed)
                    .order_by(medication.DrugPrescribed.molecule)
                    .all()
    )
    return render_template('choose_drugs_to_prescribe.html', patient=patient,
                                                    appointment=appointment,
                                                    drugs=drugs)

