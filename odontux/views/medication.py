# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/23
# v0.5
# Licence BSD
#

import pdb
from flask import ( session, redirect, url_for, request, render_template, 
                    abort, make_response, send_from_directory )
from wtforms import (Form, HiddenField, TextField, TextAreaField, DateField,
                    BooleanField, SelectField, IntegerField,
                    FieldList, FormField, SubmitField, validators )

from odontux import constants, checks
from odontux.pdfhandler import make_prescription
from odontux.views import forms
from odontux.models import meta, medication, users, documents
from odontux.odonweb import app
from odontux.views.log import index

import os
import md5
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


from gettext import gettext as _


class DrugFamilyForm(Form):
    drug_family_id = HiddenField(_('id'))
    name = TextField(_('Name'), [validators.Required()] )

class DrugForm(Form):
    drug_id = HiddenField(_('id'))
    family_id = SelectField(_('Family'), coerce=int)
    alias = TextField(_('alias'), render_kw={'size':'8'})
    molecule = TextField(_('molecule'), [validators.Required(_("Specify drug "
                                        "name please"))])
    packaging = TextAreaField(_('packaging'), 
                            [validators.Required(_("Please tell "
                                        "how the drug in packaged"))])
    posologia = TextAreaField(_('posologia'), 
                            [validators.Required(_("Please tell "
                            "the posologia the patient might take"))])
    dayssupply = TextField(_('daysupply'), [validators.Required(_("Please tell"
                            " for how long the patient need to be under "
                            "medication"))], render_kw={'size':'4'})
    comments = TextAreaField(_('comments'))
    special = BooleanField(_('special'))

class DrugPrescribedForm(Form):
    drug_id = HiddenField(_('id'))
    position = HiddenField(_('position'))
    molecule = TextField(_('molecule'))
    packaging = TextAreaField(_('packaging'), [validators.Required(_("tell how"
                                                        "drug is packaged"))])
    posologia = TextAreaField(_('posologia'), [validators.Required()])
    dayssupply = TextField(_('day supply'), render_kw={'size':"4px"})
    comments = TextAreaField(_('comments'))
    special = BooleanField(_('Special'))

class PrescriptionForm(Form):
    drugs = FieldList(FormField(DrugPrescribedForm), min_entries=1)
    update = SubmitField(_('update'))
    save_print = SubmitField(_('Save and print'))
    preview = SubmitField(_('Preview'))

class DrugPositionInPrescriptionForm(Form):
    drug_id = HiddenField(_('Id'))
    old_position = HiddenField(_('Old position'))
    new_position = IntegerField(_('Position'), render_kw={'size': '4'})

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
    drug_form = DrugForm(request.form)
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

    drug_form = DrugForm(request.form)
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
    drug_form = DrugForm(request.form)
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

@app.route('/add/drug_to_prescription?pid=<int:patient_id>'
            '&aid=<int:appointment_id>'
            '&dida=<int:drug_id_to_add>')
@app.route('/add/drug_to_prescription?pid=<int:patient_id>'
            '&aid=<int:appointment_id>'
            '&dida=<int:drug_id_to_add>&dl=<drug_list>')
def add_drug_to_prescription(patient_id, appointment_id, drug_id_to_add, 
                                                                drug_list=""):

    drugs_prescribed = []
    if drug_list:
        drugs_prescribed = [ int(drug_id) for drug_id in drug_list.split(",") ]
    drugs_prescribed.append(drug_id_to_add)
    drug_list = ",".join( [ str(drug_id) for drug_id in drugs_prescribed ] )
    return redirect(url_for('choose_drugs_to_prescribe', 
                                                patient_id=patient_id,
                                                appointment_id=appointment_id,
                                                drug_list=drug_list))

@app.route('/remove/drug_from_prescription?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&dl=<drug_list>'
            '&didr=<int:drug_id_to_remove>')
def remove_drug_from_prescription(patient_id, appointment_id, drug_list, 
                                                            drug_id_to_remove):
    
    drugs_prescribed = [ int(drug_id) for drug_id in drug_list.split(",") ]
    drugs_prescribed.remove(drug_id_to_remove)
    if drugs_prescribed:
        drug_list = ",".join( [str(drug_id) for drug_id in drugs_prescribed ] )
        return redirect(url_for('choose_drugs_to_prescribe', 
                                                patient_id=patient_id,
                                                appointment_id=appointment_id,
                                                drug_list=drug_list))
    return redirect(url_for('choose_drugs_to_prescribe', 
                                                patient_id=patient_id,
                                                appointment_id=appointment_id))
    

@app.route('/patient/choose_drugs_to_prescribed&pid=<int:patient_id>'
            '&aid=<int:appointment_id>')
@app.route('/patient/choose_drugs_to_prescribed&pid=<int:patient_id>'
            '&aid=<int:appointment_id>&dl=<drug_list>')
def choose_drugs_to_prescribe(patient_id, appointment_id, drug_list=''):
    """
        session['prescription'] = [ drug_id_1, drug_id_2 ]
    """
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)

    drugs_prescribed = []
    if drug_list:
        drugs_prescribed = [ drug_id for drug_id in drug_list.split(",") ]

    prescribed = (
        meta.session.query(medication.DrugPrescribed)
            .filter(medication.DrugPrescribed.id.in_(drugs_prescribed))
            .join(medication.DrugFamily)
            .order_by(
                medication.DrugFamily.name,
                medication.DrugPrescribed.molecule)
            .all()
    )

    other_drugs = (
        meta.session.query(medication.DrugPrescribed)
            .filter(~medication.DrugPrescribed.id.in_(drugs_prescribed))
            .join(medication.DrugFamily)
            .order_by(
                medication.DrugFamily.name,
                medication.DrugPrescribed.molecule)
            .all()
    )
   
    if drug_list:
        return render_template('choose_drugs_to_prescribe.html', 
                                        patient=patient,
                                        appointment=appointment,
                                        prescribed=prescribed,
                                        other_drugs=other_drugs,
                                        drug_list=drug_list)

    return render_template('choose_drugs_to_prescribe.html', 
                                        patient=patient,
                                        appointment=appointment,
                                        prescribed=prescribed,
                                        other_drugs=other_drugs)

@app.route('/choose/drugs_positions_on_prescription?pid=<int:patient_id>'
                    '&aid=<int:appointment_id>&dl=<drug_list>', 
                                                    methods=['GET', 'POST'] )
def choose_drugs_positions_on_prescription(patient_id, appointment_id, 
                                                                    drug_list):
    def _create_drug_list(drug_position):
        drug_list = ""
        for drug_pos in drug_position.items():
            if not drug_list:
                drug_list = str(drug_pos[0]) + "-" + str(drug_pos[1][0])
            else:
                drug_list = drug_list + "," + str(drug_pos[0]) + "-" +\
                                                        str(drug_pos[1][0])
        return drug_list
        
    def _new_position_superior(drug_position, position_form):
        for drug_data in drug_position.items():
            if drug_data[0] == int(position_form.drug_id.data):
                drug_position[drug_data[0]][0] =\
                                                position_form.new_position.data
                continue
            if ( drug_data[1][0] <= position_form.new_position.data
                and drug_data[1][0] > int(position_form.old_position.data) ):
                drug_position[drug_data[0]][0] -= 1
        return drug_position

    def _new_position_inferior(drug_position, position_form):
        for drug_data in drug_position.items():
            if drug_data[0] == int(position_form.drug_id.data):
                drug_position[drug_data[0]][0] =\
                                                position_form.new_position.data
                continue
            if ( drug_data[1][0] >= position_form.new_position.data
                and drug_data[1][0] < int(position_form.old_position.data) ):
                drug_position[drug_data[0]][0] += 1
        return drug_position

    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    
    # If we're here for the first time, or the dentist went back to change 
    # add / remove / change drugs in prescription
    drug_position = {}
    if len(drug_list.split("-")) == 1:
        position = 1
        for drug_id in drug_list.split(","):
            drug = ( meta.session.query(medication.DrugPrescribed)
                .filter(medication.DrugPrescribed.id == int(drug_id)).one() )
            drug_position[int(drug_id)] = [ position, drug.molecule ]
            position += 1
    else:
        drug_position_list = [ dp for dp in drug_list.split(",") ]
        for drug_pos in drug_position_list:
            drug_id, position  = drug_pos.split("-")
            drug = ( meta.session.query(medication.DrugPrescribed)
                .filter(medication.DrugPrescribed.id == int(drug_id))
                .one()
            )
            drug_position[int(drug_id)] = [ int(position), drug.molecule ]

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)

    drug_position_form = DrugPositionInPrescriptionForm(request.form)

    if request.method == 'POST' and drug_position_form.validate():
        if drug_position_form.new_position.data > len(drug_position):
            drug_position_form.new_position.data = len(drug_position)
        elif drug_position_form.new_position.data < 1:
            drug_position_form.new_position.data = 1

        if drug_position_form.new_position.data >\
                            int(drug_position_form.old_position.data):
            drug_position = _new_position_superior(drug_position, 
                                                            drug_position_form)
        else:
            drug_position = _new_position_inferior(drug_position, 
                                                            drug_position_form)
        drug_list = _create_drug_list(drug_position)
        return redirect(url_for('choose_drugs_positions_on_prescription',
                                                patient_id=patient_id,
                                                appointment_id=appointment_id,
                                                drug_list=drug_list))
    
    position_order_form = []
    # sort on position
    for drug_data in sorted(drug_position.items(), 
                                key=lambda drug_pos: drug_pos[1][0]):
        drug_position_form = DrugPositionInPrescriptionForm(request.form)
        drug_position_form.new_position.data =\
            drug_position_form.old_position.data = drug_data[1][0]
        drug_position_form.drug_id.data = drug_data[0]
        drug = ( meta.session.query(medication.DrugPrescribed)
                    .filter(medication.DrugPrescribed.id == drug_data[0]).one()
        )
        position_order_form.append((drug, drug_position_form))

    drug_list = _create_drug_list(drug_position)
    return render_template('choose_drugs_positions_on_prescription.html',
                                    patient=patient,
                                    appointment=appointment,
                                    drug_list=drug_list,
                                    position_order_form=position_order_form)

@app.route('/manual_adjustment_in_prescription?pid=<int:patient_id>'
                '&aid=<int:appointment_id>&dl=<drug_list>', 
                                                    methods=['GET', 'POST'])
def manual_adjustment_in_prescription(patient_id, appointment_id, drug_list):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)
    def _populate_prescription_form(drug_list):
        prescription_form = PrescriptionForm(request.form)
        drug_prescribed = {}
        for drug_pos in drug_list.split(','):
            drug_prescribed_form = DrugPrescribedForm(request.form)
            drug_id, position = drug_pos.split('-')
            drug = ( meta.session.query(medication.DrugPrescribed)
                .filter(medication.DrugPrescribed.id == drug_id).one() )
            drug_prescribed[drug_id] = ( position, drug )
            drug_prescribed_form.drug_id = drug_id
            drug_prescribed_form.position = position
            drug_prescribed_form.molecule = drug.molecule
            drug_prescribed_form.packaging = drug.packaging
            drug_prescribed_form.posologia = drug.posologia
            drug_prescribed_form.dayssupply = drug.dayssupply
            drug_prescribed_form.comments = drug.comments
            drug_prescribed_form.special = drug.special

            prescription_form.drugs.append_entry(drug_prescribed_form)
        return prescription_form

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)

    prescription_form = PrescriptionForm(request.form)
#    if ( request.method == 'POST' and prescription_form.validate()
#        and 'update' in request.form ):
#
    if ( request.method == 'POST' and prescription_form.validate()
        and 'save_print' in request.form ):
        pdf_out = make_prescription(patient_id, appointment_id, 
                                                            prescription_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        filename = md5.new(pdf_out).hexdigest()
        # Save file in odontux folder
        with open(os.path.join(
                        app.config['DOCUMENT_FOLDER'], filename), 'w') as f:
            f.write(pdf_out)
        # Keep trace in database
        file_values = {
            'md5': filename,
            'file_type': constants.FILE_PRESCRIPTION,
            'mimetype': 'application/pdf',
        }
        new_file = documents.Files(**file_values)
        meta.session.add(new_file)
        meta.session.commit()

        prescription_values = {
            'dentist_id': appointment.dentist_id,
            'patient_id': patient_id,
            'appointment_id': appointment_id,
            'file_id': new_file.id,
        }
        new_prescription = medication.Prescription(**prescription_values)
        meta.session.add(new_prescription)
        meta.session.commit()

        for drug_pos in drug_list.split(','):
            drug_id, position = drug_pos.split('-')
            prescribed_drug_values = {
                'prescription_id': new_prescription.id,
                'drug_id': drug_id,
                'position': position,
            }
            new_drug_in_prescription = medication.PrescribedDrugReference(
                                                    **prescribed_drug_values)
            meta.session.add(new_drug_in_prescription)
            meta.session.commit()
                
        return response

    if ( request.method == 'POST' and prescription_form.validate()
        and 'preview' in request.form ):
        pdf_out = make_prescription(patient_id, appointment_id, 
                                                            prescription_form)
        response = make_response(pdf_out)
        response.mimetype = 'application/pdf'
        return response

    if request.method == 'GET':
        prescription_form = _populate_prescription_form(drug_list)

    return render_template('manual_adjustment_in_prescription.html',
                                        patient=patient,
                                        appointment=appointment,
                                        drug_list=drug_list,
                                        prescription_form=prescription_form)

@app.route('/display/prescription?pfid=<int:prescription_file_id>')
def display_prescription(prescription_file_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                    constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY ]
    if session['role'] not in authorized_roles:
        return abort(403)

    prescription_file = ( meta.session.query(documents.Files)
            .filter(documents.Files.id == prescription_file_id)
            .one()
    )
    return send_from_directory(app.config['DOCUMENT_FOLDER'], 
                                prescription_file.md5,
                                mimetype=prescription_file.mimetype)
