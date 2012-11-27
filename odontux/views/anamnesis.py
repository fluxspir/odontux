# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/28
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
from wtforms import (Form,
                     SelectField, TextField, BooleanField, 
                     HiddenField,
                     validators
                     )
from odontux.views.log import index
from odontux.views.forms import DateField
from odontux.models import meta, anamnesis
from odontux.odonweb import app
from odontux.views import forms, controls
from gettext import gettext as _

from odontux import constants



class GeneralInfoForm(Form):
    patient_id = HiddenField(_('patient_id'), [validators.Required()])
    dentist_id = HiddenField(_('dentist_id'), [validators.Required()])
    time_stamp = DateField(_('time_stamp'))

class MedicalHistoryForm(Form):
    mh_id = HiddenField('id')
    icd10 = TextField(_('icd10'), filters=[forms.upper_field])
    disease = TextField(_('disease'), filters=[forms.title_field])
    disorder = TextField(_("disorder"))
    habitus = TextField(_("habitus"))
    treatment = TextField(_('treatment'))

class PastSurgeriesForm(Form):
    surg_id = HiddenField('id')
    surgery_type = TextField(_("Type of surgery"))
    problem = TextField(_("Problems occuring while surgery"))
    complication = TextField(_("Complication after surgery"))

class AllergiesForm(Form):
    al_id = HiddenField('id')
    drug = TextField(_("drug"))
    metal = TextField(_("metal"))
    food = TextField(_("food"))
    other = TextField(_("other"))
    reaction = TextField(_("reaction"))

def _get_patient_anamnesis(body_id):
    medical_history = meta.session.query(anamnesis.MedicalHistory)\
                    .filter(anamnesis.MedicalHistory.patient_id == body_id)\
                    .all()
    past_surgeries = meta.session.query(anamnesis.PastSurgeries)\
                    .filter(anamnesis.PastSurgeries.patient_id == body_id)\
                    .all()
    allergies = meta.session.query(anamnesis.Allergies)\
                    .filter(anamnesis.Allergies.patient_id == body_id)\
                    .all()

    return (medical_history, past_surgeries, allergies)

def _get_forms():
    return (MedicalHistoryForm(request.form),
            PastSurgeriesForm(request.form),
            AllergiesForm(request.form),
            GeneralInfoForm(request.form)
           )

def _get_gen_info_fields():
    return [ "patient_id", "dentist_id" ]

def _get_med_hist_fields():
    return [ "icd10", "disease", "disorder", "habitus", "treatment" ]

def _get_past_surg_fields():
    return [ "surgery_type", "problem", "complication" ]

def _get_allergies_fields():
    return [ "drug", "metal", "food", "other", "reaction" ]

@app.route('/patient/anamnesis')
def list_anamnesis():
    if (session['role'] != constants.ROLE_DENTIST
    and session['role'] != constants.ROLE_NURSE
    and session['role'] != constants.ROLE_ASSISTANT):
        return redirect(url_for('index'))

    patient = controls.get_patient(session['patient_id'])
    medical_history, past_surgeries, allergies = \
        _get_patient_anamnesis(patient.id)
    return render_template("patient_anamnesis.html",
                            patient=patient,
                            medical_history=medical_history,
                            past_surgeries=past_surgeries,
                            allergies=allergies)

@app.route('/patient/modify_anamnesis/', methods=['GET', 'POST'])
def update_anamnesis(): 
    if not session['patient_id']:
        return redirect(url_for('list_patients'))
   
    # Get the patient, and verify if the user is his dentist.
    patient = controls.get_patient(session['patient_id'])
    if not patient.dentist_id == session['user_id']:
        return redirect(url_for('list_patients'))

    (med_form, surg_form, allergies_form, gen_info_form) = _get_forms()
    (medical_history, past_surgeries, allergies) =\
        _get_patient_anamnesis(patient.id)
    return render_template("update_anamnesis.html",
                            patient=patient,
                            medical_history=medical_history,
                            med_form=med_form,
                            past_surgeries=past_surgeries,
                            surg_form=surg_form,
                            allergies=allergies,
                            allergies_form=allergies_form,
                            gen_info_form=gen_info_form
                          )

@app.route('/patient/update_medical_history/', methods=['POST'])
def update_medical_history():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    med_form = MedicalHistoryForm(request.form)
    if (request.method == 'POST' and med_form.validate()
        and gen_info_form.validate()
        ):
        # get the right medical history we'd like to update
        medic_hist = meta.session.query(anamnesis.MedicalHistory)\
            .filter(anamnesis.MedicalHistory.id == med_form.mh_id.data)\
            .one()
        med_fields = _get_med_hist_fields()
        for f in med_fields:
            setattr(medic_hist, f, getattr(med_form, f).data)
        setattr(medic_hist, "time_stamp",
                getattr(gen_info_form, "time_stamp").data)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/delete_medical_history/', methods=['POST'])
def delete_medical_history():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))
    
    med_form = MedicalHistoryForm(request.form)
    if (request.method == 'POST' and med_form.validate() ):
        medic_hist = meta.session.query(anamnesis.MedicalHistory)\
            .filter(anamnesis.MedicalHistory.id == med_form.mh_id.data)\
            .one()
        meta.session.delete(medic_hist)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/add_medical_history/', methods=['POST'])
def add_medical_history():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    med_form = MedicalHistoryForm(request.form)

    if ( request.method == 'POST' and gen_info_form.validate()
    and med_form.validate() ):
        # Get the key for database
        med_fields = _get_med_hist_fields()
        gen_info_fields = _get_gen_info_fields()
        # Prepare the key-value to enter in database
        args = {}
        for f in med_fields:
            args[f] = getattr(med_form, f).data
        for f in gen_info_fields:
            args[f] = getattr(gen_info_form, f).data
#        args = {f: getattr(med_form, f).data for f in med_fields}
#        args = {f: getattr(gen_info_form, f).data for f in gen_info_fields}
        # Time stamp entered if precised.
        if gen_info_form.time_stamp.data:
            args['time_stamp'] = gen_info_form.time_stamp.data
        new_med_hist = anamnesis.MedicalHistory(**args)
        meta.session.add(new_med_hist)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/update_past_surgery/', methods=['POST'])
def update_past_surgery():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    surg_form = PastSurgeriesForm(request.form)
    if (request.method == 'POST' and surg_form.validate()
        and gen_info_form.validate()
        ):
        
        past_surgery = meta.session.query(anamnesis.PastSurgeries)\
            .filter(anamnesis.PastSurgeries.id == surg_form.surg_id.data)\
            .one()
        surg_fields = _get_past_surg_fields()
        for f in surg_fields:
            setattr(past_surgery, f, getattr(surg_form, f).data)
        setattr(past_surgery, "time_stamp",
                getattr(gen_info_form, "time_stamp").data)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/delete_past_surgery/', methods=['POST'])
def delete_past_surgery():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))
    
    surg_form = PastSurgeriesForm(request.form)
    if (request.method == 'POST' and surg_form.validate() ):
        past_surgery = meta.session.query(anamnesis.PastSurgeries)\
            .filter(anamnesis.PastSurgeries.id == surg_form.surg_id.data)\
            .one()
        meta.session.delete(past_surgery)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/add_past_surgery/', methods=['POST'])
def add_past_surgery():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    surg_form = PastSurgeriesForm(request.form)

    if ( request.method == 'POST' and gen_info_form.validate()
    and surg_form.validate() ):
        # Get the key for database
        surg_fields = _get_past_surg_fields()
        gen_info_fields = _get_gen_info_fields()
        # Prepare the key-value to enter in database
        args = {}
        for f in surg_fields:
            args[f] = getattr(surg_form, f).data
        for f in gen_info_fields:
            args[f] = getattr(gen_info_form, f).data
        # Time stamp entered if precised.
        if gen_info_form.time_stamp.data:
            args['time_stamp'] = gen_info_form.time_stamp.data
        new_past_surgery = anamnesis.PastSurgeries(**args)
        meta.session.add(new_past_surgery)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/update_allergies/', methods=['POST'])
def update_allergies():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    allergies_form = AllergiesForm(request.form)
    if (request.method == 'POST' and allergies_form.validate()
        and gen_info_form.validate()
        ):
        # get the right medical history we'd like to update
        allergy = meta.session.query(anamnesis.Allergies)\
            .filter(anamnesis.Allergies.id == allergies_form.al_id.data)\
            .one()
        allergies_fields = _get_allergies_fields()
        for f in allergies_fields:
            setattr(allergy, f, getattr(allergies_form, f).data)
        setattr(allergy, "time_stamp",
                getattr(gen_info_form, "time_stamp").data)
        meta.session.commit()
        return redirect(url_for('update_anamnesis'), patient=patient)

@app.route('/patient/delete_allergies/', methods=['POST'])
def delete_allergies():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))
    
    allergies_form = AllergiesForm(request.form)
    if (request.method == 'POST' and allergies_form.validate() ):
        allergy = meta.session.query(anamnesis.Allergies)\
            .filter(anamnesis.Allergies.id == allergies_form.al_id.data)\
            .one()
        meta.session.delete(allergy)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))

@app.route('/patient/add_allergies/', methods=['POST'])
def add_allergies():
    """ """
    patient = controls.get_patient(session['patient_id'])
    if patient.dentist_id != session['user_id']:
        return redirect(url_for('list_patients'))

    gen_info_form = GeneralInfoForm(request.form)
    allergies_form = AllergiesForm(request.form)

    if ( request.method == 'POST' and gen_info_form.validate()
    and allergies_form.validate() ):
        # Get the key for database
        allergies_fields = _get_allergies_fields()
        gen_info_fields = _get_gen_info_fields()
        # Prepare the key-value to enter in database
        args = {}
        for f in allergies_fields:
            args[f] = getattr(allergies_form, f).data
        for f in gen_info_fields:
            args[f] = getattr(gen_info_form, f).data
        # Time stamp entered if precised.
        if gen_info_form.time_stamp.data:
            args['time_stamp'] = gen_info_form.time_stamp.data
        new_allergy = anamnesis.Allergies(**args)
        meta.session.add(new_allergy)
        meta.session.commit()
        return redirect(url_for('update_anamnesis', patient=patient))
