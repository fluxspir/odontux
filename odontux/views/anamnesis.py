# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/28
# v0.5
# licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for
from wtforms import (Form, SelectField, TextField, BooleanField, TextAreaField,
                     IntegerField, HiddenField, DateField, validators )
from sqlalchemy.orm import with_polymorphic

from odontux.views.log import index
from odontux.models import meta, anamnesis, md
from odontux.odonweb import app
from odontux.views import forms
from gettext import gettext as _

from odontux import constants, checks

class SurveyForm(Form):
    id = HiddenField(_('id'))
    name = TextField(_('Survey title'), [validators.Required()])

class QuestionForm(Form):
    id = HiddenField(_('id'))
    question = TextAreaField(_('Question'), [validators.Required()],
                        render_kw={'rows': '4', 'cols': '50'})

class PositionForm(Form):
    question_id = HiddenField(_('question_id'))
    old_position = HiddenField(_('old_position'))
    new_position = IntegerField(_('Position'),
                        render_kw={'size': '3'})

class AnamnesisForm(Form):
    id = HiddenField(_('id'))
    alert = BooleanField(_('Alert'))
    document = BooleanField(_('Document'))
    anamnesis_type = SelectField(_("Anamnesis type"), coerce=int,
                            description='ChangementAnamnesisType()')

class MedicalHistoryForm(Form):
    type = SelectField(_('Type'), coerce=int)
    disease = SelectField(_('Disease'), coerce=int)
    name = TextField(_('Name'), [validators.Required()])
    icd10 = TextField(_('ICD 10'))
    comment = TextAreaField(_('Comments'))

class AddictionForm(Form):
    type = SelectField(_('Type'), coerce=int)
    comment = TextAreaField(_('comment'))
    begin = DateField(_('Begin'), format='%Y-%m-%d', 
                    validators=[validators.Optional()])
    end = DateField(_('End'), format='%Y-%m-%d',
                    validators=[validators.Optional()])

class TreatmentForm(Form):
    name = TextField(_('Name'), [validators.Required()])
    posologia = TextAreaField(_('Posologia'))
    begin = DateField(_('Begin'), format='%Y-%m-%d', 
                    validators=[validators.Optional()])
    end = DateField(_('End'), format='%Y-%m-%d',
                    validators=[validators.Optional()])

class PastSurgeryForm(Form):
    surgery_type = TextField(_('Name'), [validators.Required()])
    problem = TextAreaField(_('Problem'))
    complication = TextAreaField(_('Complication'))

class AllergyForm(Form):
    type = SelectField(_('Type'), coerce=int)
    allergen = TextField(_('Allergen'), [validators.Required()])
    reaction = SelectField(_('Reaction'), coerce=int)

class MedecineDoctorForm(Form):
    md_id = SelectField(_('Medecine Doctor'), coerce=int)


@app.route('/add/medical_history_entry', methods=['POST'])
def add_medical_history_entry():
    pass

@app.route('/add/anamnesis_entry?pid=<int:patient_id>'
            '&aid=<int:appointment_id>', methods=['GET', 'POST'] )
@app.route('/add/anamnesis_entry?pid=<int:patient_id>'
            '&aid=<int:appointment_id>&sid=<int:survey_id>'
            '&sen=<int:survey_entry>', methods=['GET', 'POST'] )
def add_anamnesis_entry(patient_id, appointment_id, survey_id=None, 
                                                    survey_entry=None):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)
    appointment = checks.get_appointment(appointment_id)

    anamnesis_form = AnamnesisForm(request.form)
    anamnesis_form.anamnesis_type.choices = [ (id, info[0]) for id, info in
                                            constants.ANAMNESIS.items() ]
    medical_history_form = MedicalHistoryForm(request.form)
    medical_history_form.type.choices = constants.MEDICAL_HISTORIES.items()
    medical_history_form.disease.choices = constants.DISEASES.items()
    addiction_form = AddictionForm(request.form)
    addiction_form.type.choices = constants.ADDICTIONS.items()
    treatment_form = TreatmentForm(request.form)
    past_surgery_form = PastSurgeryForm(request.form)
    allergy_form = AllergyForm(request.form)
    allergy_form.type.choices = constants.ALLERGIES.items()
    allergy_form.reaction.choices = constants.ALLERGIC_REACTIONS.items()

    if survey_entry:
        question = (
            meta.session.query(anamnesis.Question)
                .filter(anamnesis.SurveyQuestionsOrder.survey_id == survey_id,
                    anamnesis.SurveyQuestionsOrder.position == survey_entry)
                .one_or_none()
            )
        if question:
            anamnesis_form.question_id.data = question.id
    else:
        question = None

    if request.method == 'POST' and anamnesis_form.validate():
        
        anamnesis_values = {
            'patient_id': patient_id,
            'appointment_id': appointment_id,
            'anamnesis_type': anamnesis_form.anamnesis_type.data,
            'alert': anamnesis_form.alert.data,
            'document': anamnesis_form.document.data,
            }
        if question: anamnesis_values['question_id'] = question.id
        if survey_entry: survey_entry += 1
        
        if ( anamnesis_form.anamnesis_type.data ==\
                                        constants.ANAMNESIS_MEDICAL_HISTORY
            and medical_history_form.validate() ):
            values = {
                'type': medical_history_form.type.data,
                'disease': medical_history_form.disease.data,
                'name': medical_history_form.name.data,
                'icd10': medical_history_form.icd10.data,
                'comment': medical_history_form.comment.data,
                }
            values.update(anamnesis_values)
            new_medical_history = anamnesis.MedicalHistory(**values)
            meta.session.add(new_medical_history)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==\
                                        constants.ANAMNESIS_ADDICTION
            and addiction_form.validate() ):
            values = {
                'type': addiction_form.type.data,
                'comment': addiction_form.comment_data,
                'begin': addiction_form.begin.data,
                'end': addiction_form.end.data
                }
            values.update(anamnesis_values)
            new_addiction = anamnesis.Addiction(**values)
            meta.session.add(new_addiction)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==\
                                        constants.ANAMNESIS_TREATMENT
            and treatment_form.validate() ):
            values = {
                'name': treatment_form.name.data,
                'posologia': treatment_form.posologia.data,
                'begin': treatment_form.begin.data,
                'end': treatment_form.end.data
                }
            values.update(anamnesis_values)
            new_treatment = anamnesis.Treatment(**values)
            meta.session.add(new_treatment)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==\
                                        constants.ANAMNESIS_PAST_SURGERY
            and past_surgery_form.validate() ):
            values = {
                'surgery_type': past_surgery.surgery_type.data,
                'problem': past_surgery.problem.data,
                'complication': past_surgery.complication.data,
                }
            values.update(anamnesis_values)
            new_past_surgery = anamnesis.PastSurgery(**values)
            meta.session.add(new_past_surgery)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==\
                                        constants.ANAMNESIS_ALLERGY
            and allergy_form.validate() ):
            values = {
                'type': allergy_form.type.data,
                'allergen': allergy_form.allergen.data,
                'reaction': allergy_form.reaction.data,
                }
            values.update(anamnesis_values)
            new_allergy = anamnesis.Allergy(**values)
            meta.session.add(new_allergy)
            meta.session.commit()

        else:
            if survey_entry: survey_entry -= 1
            clear_form = False
            render_template('add_anamnesis_entry.html', patient=patient,
                                    appointment=appointment,
                                    question=question,
                                    survey_id=survey_id,
                                    survey_entry=survey_entry,
                                    anamnesis_form=anamnesis_form,
                                    medical_history_form=medical_history_form,
                                    addiction_form=addiction_form,
                                    treatment_form=treatment_form,
                                    past_surgery_form=past_surgery_form,
                                    allergy_form=allergy_form,
                                    clear_form=clear_form)

        return redirect(url_for('add_anamnesis_entry', 
                                        patient_id=patient_id,
                                        appointment_id=appointment_id,
                                        survey_id=survey_id,
                                        survey_entry=survey_entry))
    clear_form = True
    
    return render_template('add_anamnesis_entry.html', patient=patient,
                                    appointment=appointment,
                                    question=question,
                                    survey_id=survey_id, 
                                    survey_entry=survey_entry,
                                    anamnesis_form=anamnesis_form,
                                    medical_history_form=medical_history_form,
                                    addiction_form=addiction_form,
                                    treatment_form=treatment_form,
                                    past_surgery_form=past_surgery_form,
                                    allergy_form=allergy_form,
                                    clear_form=clear_form)

@app.route('/patient/anamnesis?pid=<int:patient_id>')
def list_anamnesis(patient_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    patient = checks.get_patient(patient_id)

    global_anamnesis = with_polymorphic(anamnesis.Anamnesis, '*')
    patient_anamnesis = (
        meta.session.query(global_anamnesis)
            .filter(anamnesis.Anamnesis.patient_id == patient_id)
            .all()
        )
    doctor = meta.session.query(md.MedecineDoctor).filter(
        md.MedecineDoctor.id == patient.gen_doc_id).one_or_none()
    return render_template("patient_anamnesis.html",
                            patient=patient,
                            patient_anamnesis=patient_anamnesis,
                            doctor=doctor)

@app.route('/update/anamnesis?pid=<int:patient_id>')
def update_anamnesis(patient_id):
    pass






@app.route('/anamnesis')
def anamnesis_portal():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    return render_template('anamnesis_portal.html')

@app.route('/add/survey', methods=['GET', 'POST'])
def add_survey():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    survey_form = SurveyForm(request.form)
    if request.method == 'POST' and survey_form.validate():
        meta.session.add(anamnesis.Survey(**{'name': survey_form.name.data }))
        meta.session.commit()
        return redirect(url_for('list_survey'))

    return render_template('add_survey.html', survey_form=survey_form)

@app.route('/add/question', methods=['GET', 'POST'])
def add_question():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    question_form = QuestionForm(request.form)
    if request.method == 'POST' and question_form.validate():
        values = {'question': question_form.question.data }
        new_question = anamnesis.Question(**values)
        meta.session.add(new_question)
        meta.session.commit()
        return redirect(url_for('list_question'))

    return render_template('add_question.html', question_form=question_form)

@app.route('/list/survey')
def list_survey():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    surveys = meta.session.query(anamnesis.Survey).all()
    return render_template('list_survey.html', surveys=surveys)

@app.route('/list/question')
def list_question():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    questions = meta.session.query(anamnesis.Question).all()
    return render_template('list_question.html', questions=questions)


@app.route('/view/survey?sid=<int:survey_id>', methods=['GET', 'POST'])
def view_survey(survey_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    def _new_position_higher(position_form, questions_in_survey):
        for question in questions_in_survey:
            if question.question_id == int(position_form.question_id.data):
                question.position = position_form.new_position.data
                meta.session.commit()
                continue
            if ( question.position <= position_form.new_position.data
                and question.position > int(position_form.old_position.data) ):
                question.position -= 1
                meta.session.commit()

    def _new_position_lower(position_form, questions_in_survey):
        for question in questions_in_survey:
            if question.question_id == int(position_form.question_id.data):
                question.position = position_form.new_position.data
                meta.session.commit()
                continue
            if ( question.position < int(position_form.old_position.data)
                and question.position >= position_form.new_position.data ):
                question.position += 1
                meta.session.commit()

    position_form = PositionForm(request.form)
    questions_in_survey = (
        meta.session.query(anamnesis.SurveyQuestionsOrder)
            .filter(anamnesis.SurveyQuestionsOrder.survey_id == survey_id)
            .order_by(anamnesis.SurveyQuestionsOrder.position)
            .all()
        )

    if request.method == 'POST' and position_form.validate():
        if position_form.new_position.data > len(questions_in_survey):
            position_form.new_position.data = len(questions_in_survey)
        elif position_form.new_position.data < 1:
            position_form.new_position.data = 1
        else:
            position_form.new_position.data = len(questions_in_survey)

        if position_form.new_position.data >\
                                        int(position_form.old_position.data):
            _new_position_higher(position_form, questions_in_survey)
        else:
            _new_position_lower(position_form, questions_in_survey) 
        
        return redirect(url_for('view_survey', survey_id=survey_id))

    survey = ( meta.session.query(anamnesis.Survey)
                .filter(anamnesis.Survey.id == survey_id)
                .one() )

    question_form_list = []
    for question in sorted(survey.quests, 
                                key=lambda question: question.position):
        position_form = PositionForm(request.form)
        position_form.question_id.data = question.question_id
        position_form.old_position.data =\
            position_form.new_position.data = question.position
        question_form_list.append( ( question, position_form ) )
    
    new_questions = (
        meta.session.query(anamnesis.Question)
            .filter(~anamnesis.Question.id.in_(
                meta.session.query(anamnesis.Question.id)
                    .join(anamnesis.SurveyQuestionsOrder)
                    .join(anamnesis.Survey)
                    .filter(anamnesis.Survey.quests.any(
                        anamnesis.SurveyQuestionsOrder.survey_id == survey_id)
                        )
                    )
                )
            .all()
        )
    return render_template('view_survey.html', survey=survey,
                                        question_form_list=question_form_list,
                                        new_questions=new_questions)
 
@app.route('/view/question?sid=<int:question_id>')
def view_question(question_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    question = ( meta.session.query(anamnesis.Question)
                .filter(anamnesis.Question.id == question_id)
                .one() )
                        
    return render_template('view_question.html', question=question) 
    
@app.route('/add/question_to_survey?sid=<int:survey_id>'
            '&qid=<int:question_id>')
def add_question_to_survey(survey_id, question_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    number_of_questions = (
        meta.session.query(anamnesis.SurveyQuestionsOrder)
            .filter(anamnesis.SurveyQuestionsOrder.survey_id == survey_id)
            .count()
        )
    values = {
        'survey_id': survey_id,
        'question_id': question_id,
        'position': number_of_questions + 1
    }
    new_survey_question = anamnesis.SurveyQuestionsOrder(**values)
    meta.session.add(new_survey_question)
    meta.session.commit()
    return redirect(url_for('view_survey', survey_id=survey_id))
 
@app.route('/remove/question_from_survey?sid=<int:survey_id>'
            '&qid=<int:question_id>')
def remove_question_from_survey(survey_id, question_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    survey = (
        meta.session.query(anamnesis.Survey)
            .filter(anamnesis.Survey.id == survey_id)
            .one()
        )

    question_to_remove = (
        meta.session.query(anamnesis.SurveyQuestionsOrder)
            .filter(anamnesis.SurveyQuestionsOrder.survey_id == survey_id,
                    anamnesis.SurveyQuestionsOrder.question_id == question_id)
            .one()
        )
    
    old_position = question_to_remove.position
    meta.session.delete(question_to_remove)
    meta.session.commit()
    others_questions_in_survey = (
        meta.session.query(anamnesis.SurveyQuestionsOrder)
            .filter(anamnesis.SurveyQuestionsOrder.survey_id == survey_id)
            .all()
        )
    for question in others_questions_in_survey:
        if question.position > old_position:
            question.position = question.position - 1
    meta.session.commit()
    return redirect(url_for('view_survey', survey_id=survey_id))
   
@app.route('/update/survey_name&sid=<int:survey_id>', methods=['GET', 'POST'])
def update_survey_name(survey_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    survey = ( meta.session.query(anamnesis.Survey)
                .filter(anamnesis.Survey.id == survey_id)
                .one() )
    survey_form = SurveyForm(request.form)
    if request.method == 'POST' and survey_form.validate():
        survey.name = survey_form.name.data
        meta.session.commit()
        return redirect(url_for('view_survey', survey_id=survey_id))

    survey_form.name.data = survey.name
    return render_template('update_survey_name.html', survey=survey,
                                                    survey_form=survey_form)

@app.route('/update/question&sid=<int:question_id>', methods=['GET', 'POST'])
def update_question(question_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    question = ( meta.session.query(anamnesis.Question)
                .filter(anamnesis.Question.id == question_id)
                .one() )
    question_form = QuestionForm(request.form)
    if request.method == 'POST' and question_form.validate():
        question.question = question_form.question.data
        meta.session.commit()
        return redirect(url_for('view_question', question_id=question_id))

    question_form.question.data = question.question
    return render_template('update_question_name.html', question=question,
                                                question_form=question_form)


@app.route('/delete/survey?sid=<int:survey_id>')
def delete_survey(survey_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))
    survey = ( meta.session.query(anamnesis.Survey)
                .filter(anamnesis.Survey.id == survey_id)
                .one() )
    for question in survey.quests:
        meta.session.delete(question)
    meta.session.delete(survey)
    meta.session.commit()
    return redirect(url_for('list_survey'))

###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
###############################################################################
#class GeneralInfoForm(Form):
#    patient_id = HiddenField(_('patient_id'), [validators.Required()])
#    dentist_id = HiddenField(_('dentist_id'), [validators.Required()])
#    time_stamp = DateField(_('time_stamp'), [validators.Optional()])
#

#class MedicalHistoryForm(Form):
#    mh_id = HiddenField('id')
#    icd10 = TextField(_('icd10'), filters=[forms.upper_field])
#    disease = TextField(_('disease'), filters=[forms.title_field])
#    disorder = TextField(_("disorder"))
#    habitus = TextField(_("habitus"))
#    treatment = TextField(_('treatment'))
#
#class PastSurgeriesForm(Form):
#    surg_id = HiddenField('id')
#    surgery_type = TextField(_("Type of surgery"))
#    problem = TextField(_("Problems occuring while surgery"))
#    complication = TextField(_("Complication after surgery"))
#
#class AllergiesForm(Form):
#    al_id = HiddenField('id')
#    drug = TextField(_("drug"))
#    metal = TextField(_("metal"))
#    food = TextField(_("food"))
#    other = TextField(_("other"))
#    reaction = TextField(_("reaction"))
#
#def _get_patient_anamnesis(body_id):
#    medical_history = meta.session.query(anamnesis.MedicalHistory)\
#                    .filter(anamnesis.MedicalHistory.patient_id == body_id)\
#                    .all()
#    past_surgeries = meta.session.query(anamnesis.PastSurgeries)\
#                    .filter(anamnesis.PastSurgeries.patient_id == body_id)\
#                    .all()
#    allergies = meta.session.query(anamnesis.Allergies)\
#                    .filter(anamnesis.Allergies.patient_id == body_id)\
#                    .all()
#
#    return (medical_history, past_surgeries, allergies)
#
#def _get_forms():
#    return (MedicalHistoryForm(request.form),
#            PastSurgeriesForm(request.form),
#            AllergiesForm(request.form),
#            GeneralInfoForm(request.form),
#            MedecineDoctorForm(request.form)
#           )
#
#def _get_gen_info_fields():
#    return [ "patient_id", "dentist_id", "time_stamp" ]
#
#def _get_med_hist_fields():
#    return [ "icd10", "disease", "disorder", "habitus", "treatment" ]
#
#def _get_past_surg_fields():
#    return [ "surgery_type", "problem", "complication" ]
#
#def _get_allergies_fields():
#    return [ "drug", "metal", "food", "other", "reaction" ]
#

#@app.route('/patient/modify_anamnesis/', methods=['GET', 'POST'])
#def update_anamnesis(): 
#    if not session['patient_id']:
#        return redirect(url_for('list_patients'))
#   
#    # Get the patient, and verify if the user is his dentist.
#    patient = checks.get_patient(session['patient_id'])
#    if not patient.dentist_id == session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    (med_form, surg_form, allergies_form, gen_info_form, 
#    medecine_doctor_form) = _get_forms()
#
#    medecine_doctor_form.md_id.choices = [ (doc.id, doc.lastname + " " + 
#                                                    doc.firstname) 
#                                    for doc in meta.session.query(
#                                    md.MedecineDoctor).order_by(
#                                    md.MedecineDoctor.lastname).order_by(
#                                    md.MedecineDoctor.firstname).all()
#                                  ]
#    medecine_doctor_form.md_id.data = patient.gen_doc_id
#
#    (medical_history, past_surgeries, allergies) =\
#        _get_patient_anamnesis(patient.id)
#    
#    return render_template("update_anamnesis.html",
#                            patient=patient,
#                            medical_history=medical_history,
#                            med_form=med_form,
#                            past_surgeries=past_surgeries,
#                            surg_form=surg_form,
#                            allergies=allergies,
#                            allergies_form=allergies_form,
#                            gen_info_form=gen_info_form,
#                            medecine_doctor_form=medecine_doctor_form
#                          )
#
#@app.route('/patient/update_patient_md/', methods=['POST'])
#def update_patient_md():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#
#    medecine_doctor_form = MedecineDoctorForm(request.form)
#    patient.gen_doc_id = medecine_doctor_form.md_id.data
#    meta.session.commit()
#    return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/update_medical_history/', methods=['POST'])
#def update_medical_history():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    med_form = MedicalHistoryForm(request.form)
#    if (request.method == 'POST' and med_form.validate()
#        and gen_info_form.validate()
#        ):
#        # get the right medical history we'd like to update
#        medic_hist = meta.session.query(anamnesis.MedicalHistory)\
#            .filter(anamnesis.MedicalHistory.id == med_form.mh_id.data)\
#            .one()
#        med_fields = _get_med_hist_fields()
#        gen_info_fields = _get_gen_info_fields()
#        medic_hist.id = med_form.mh_id.data
#        for f in med_fields:
#            setattr(medic_hist, f, getattr(med_form, f).data)
#        for f in gen_info_fields:
#            setattr(medic_hist, "time_stamp", getattr(gen_info_form, 
#                                                      "time_stamp").data)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/delete_medical_history/', methods=['POST'])
#def delete_medical_history():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#    
#    med_form = MedicalHistoryForm(request.form)
#    if (request.method == 'POST' and med_form.validate() ):
#        medic_hist = meta.session.query(anamnesis.MedicalHistory)\
#            .filter(anamnesis.MedicalHistory.id == med_form.mh_id.data)\
#            .one()
#        meta.session.delete(medic_hist)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/add_medical_history/', methods=['POST'])
#def add_medical_history():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    med_form = MedicalHistoryForm(request.form)
#
#    if ( request.method == 'POST' and gen_info_form.validate()
#    and med_form.validate() ):
#        # Get the key for database
#        med_fields = _get_med_hist_fields()
#        gen_info_fields = _get_gen_info_fields()
#        # Prepare the key-value to enter in database
#        args = {}
#        for f in med_fields:
#            args[f] = getattr(med_form, f).data
#        for f in gen_info_fields:
#            args[f] = getattr(gen_info_form, f).data
##        args = {f: getattr(med_form, f).data for f in med_fields}
##        args = {f: getattr(gen_info_form, f).data for f in gen_info_fields}
#        # Time stamp entered if precised.
#        if gen_info_form.time_stamp.data:
#            args['time_stamp'] = gen_info_form.time_stamp.data
#        new_med_hist = anamnesis.MedicalHistory(**args)
#        meta.session.add(new_med_hist)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/update_past_surgery/', methods=['POST'])
#def update_past_surgery():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    surg_form = PastSurgeriesForm(request.form)
#    if (request.method == 'POST' and surg_form.validate()
#        and gen_info_form.validate()
#        ):
#        
#        past_surgery = meta.session.query(anamnesis.PastSurgeries)\
#            .filter(anamnesis.PastSurgeries.id == surg_form.surg_id.data)\
#            .one()
#        surg_fields = _get_past_surg_fields()
#        past_surgery.id = surg_form.surg_id.data
#        for f in surg_fields:
#            setattr(past_surgery, f, getattr(surg_form, f).data)
#        setattr(past_surgery, "time_stamp",
#                getattr(gen_info_form, "time_stamp").data)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/delete_past_surgery/', methods=['POST'])
#def delete_past_surgery():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#    
#    surg_form = PastSurgeriesForm(request.form)
#    if (request.method == 'POST' and surg_form.validate() ):
#        past_surgery = meta.session.query(anamnesis.PastSurgeries)\
#            .filter(anamnesis.PastSurgeries.id == surg_form.surg_id.data)\
#            .one()
#        meta.session.delete(past_surgery)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/add_past_surgery/', methods=['POST'])
#def add_past_surgery():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    surg_form = PastSurgeriesForm(request.form)
#
#    if ( request.method == 'POST' and gen_info_form.validate()
#    and surg_form.validate() ):
#        # Get the key for database
#        surg_fields = _get_past_surg_fields()
#        gen_info_fields = _get_gen_info_fields()
#        # Prepare the key-value to enter in database
#        args = {}
#        for f in surg_fields:
#            args[f] = getattr(surg_form, f).data
#        for f in gen_info_fields:
#            args[f] = getattr(gen_info_form, f).data
#        # Time stamp entered if precised.
#        if gen_info_form.time_stamp.data:
#            args['time_stamp'] = gen_info_form.time_stamp.data
#        new_past_surgery = anamnesis.PastSurgeries(**args)
#        meta.session.add(new_past_surgery)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/update_allergies/', methods=['POST'])
#def update_allergies():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    allergies_form = AllergiesForm(request.form)
#    if (request.method == 'POST' and allergies_form.validate()
#        and gen_info_form.validate()
#        ):
#        # get the right medical history we'd like to update
#        allergy = meta.session.query(anamnesis.Allergies)\
#            .filter(anamnesis.Allergies.id == allergies_form.al_id.data)\
#            .one()
#        allergies_fields = _get_allergies_fields()
#        allergy.id = allergies_form.al_id.data
#        for f in allergies_fields:
#            setattr(allergy, f, getattr(allergies_form, f).data)
#        setattr(allergy, "time_stamp",
#                getattr(gen_info_form, "time_stamp").data)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis'), patient=patient)
#
#@app.route('/patient/delete_allergies/', methods=['POST'])
#def delete_allergies():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#    
#    allergies_form = AllergiesForm(request.form)
#    if (request.method == 'POST' and allergies_form.validate() ):
#        allergy = meta.session.query(anamnesis.Allergies)\
#            .filter(anamnesis.Allergies.id == allergies_form.al_id.data)\
#            .one()
#        meta.session.delete(allergy)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
#
#@app.route('/patient/add_allergies/', methods=['POST'])
#def add_allergies():
#    """ """
#    patient = checks.get_patient(session['patient_id'])
#    if patient.dentist_id != session['user_id']:
#        return redirect(url_for('list_patients'))
#
#    gen_info_form = GeneralInfoForm(request.form)
#    allergies_form = AllergiesForm(request.form)
#
#    if ( request.method == 'POST' and gen_info_form.validate()
#    and allergies_form.validate() ):
#        # Get the key for database
#        allergies_fields = _get_allergies_fields()
#        gen_info_fields = _get_gen_info_fields()
#        # Prepare the key-value to enter in database
#        args = {}
#        for f in allergies_fields:
#            args[f] = getattr(allergies_form, f).data
#        for f in gen_info_fields:
#            args[f] = getattr(gen_info_form, f).data
#        # Time stamp entered if precised.
#        if gen_info_form.time_stamp.data:
#            args['time_stamp'] = gen_info_form.time_stamp.data
#        new_allergy = anamnesis.Allergies(**args)
#        meta.session.add(new_allergy)
#        meta.session.commit()
#        return redirect(url_for('update_anamnesis', patient=patient))
