# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/28
# v0.5
# licence BSD
#

import pdb
import datetime
from flask import session, render_template, request, redirect, url_for, jsonify
from wtforms import (Form, SelectField, TextField, BooleanField, TextAreaField,
                     IntegerField, HiddenField, DateField, DecimalField, 
                    validators )
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
    question_id = HiddenField(_('question_id'))
    alert = BooleanField(_('Alert'))
    document = BooleanField(_('Document'))
    anamnesis_type = SelectField(_("Anamnesis type"), coerce=int,
                            description='ChangementAnamnesisType()')

class MedicalHistoryForm(Form):
    medical_type = SelectField(_('Type'), coerce=int)
    disease = SelectField(_('Disease'), coerce=int)
    denomination = TextField(_('Name'), [validators.Required()])
    icd10 = TextField(_('ICD 10'))
    medical_comment = TextAreaField(_('Comments'))

class AddictionForm(Form):
    addiction_type = SelectField(_('Type'), coerce=int)
    addiction_comment = TextAreaField(_('comment'))
    begin_addiction = DateField(_('Begin'), format='%Y-%m-%d', 
                    validators=[validators.Optional()])
    end_addiction = DateField(_('End'), format='%Y-%m-%d',
                    validators=[validators.Optional()])

class TreatmentForm(Form):
    molecule = TextField(_('Name'), [validators.Required()])
    posologia = TextAreaField(_('Posologia'))
    begin_treatment = DateField(_('Begin'), format='%Y-%m-%d', 
                    validators=[validators.Optional()])
    end_treatment = DateField(_('End'), format='%Y-%m-%d',
                    validators=[validators.Optional()])

class PastSurgeryForm(Form):
    surgery_type = TextField(_('Name'), [validators.Required()])
    problem = TextAreaField(_('Problem'))
    complication = TextAreaField(_('Complication'))

class AllergyForm(Form):
    allergy_type = SelectField(_('Type'), coerce=int)
    allergen = TextField(_('Allergen'), [validators.Required()])
    reaction = SelectField(_('Reaction'), coerce=int)

class OralHygieneForm(Form):
    oral_type = SelectField(_('Type'), coerce=int)
    frequency = DecimalField(_('Frequency per day (per years for dentist)'), 
                                                    [validators.Optional()])
    oral_comment = TextAreaField(_('Comment'), 
                                    render_kw={'rows': '2', 'cols': '30'})

class MedecineDoctorForm(Form):
    md_id = SelectField(_('Medecine Doctor'), coerce=int)

class ChooseSurveyForm(Form):
    survey_id = SelectField(_('Choose Survey'), coerce=int)

@app.route('/enter_in_survey?pid=<int:patient_id>'
            'aid=<int:appointment_id>' , methods=['POST'])
def enter_in_survey(patient_id, appointment_id):
    survey_form = ChooseSurveyForm(request.form)
    survey_form.survey_id.choices =\
        meta.session.query(anamnesis.Survey.id, anamnesis.Survey.name).all()

    if survey_form.validate():
        return redirect(url_for('add_anamnesis_entry', patient_id=patient_id,
                                appointment_id=appointment_id,
                                survey_id=survey_form.survey_id.data,
                                survey_entry=1
                                ))

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

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    anamnesis_form = AnamnesisForm(request.form)
    anamnesis_form.anamnesis_type.choices = [ (id, info[0]) for id, info in
                                            constants.ANAMNESIS.items() ]
    medical_history_form = MedicalHistoryForm(request.form)
    medical_history_form.medical_type.choices =\
                                            constants.MEDICAL_HISTORIES.items()
    medical_history_form.disease.choices = constants.DISEASES.items()
    addiction_form = AddictionForm(request.form)
    addiction_form.addiction_type.choices = constants.ADDICTIONS.items()
    treatment_form = TreatmentForm(request.form)
    past_surgery_form = PastSurgeryForm(request.form)
    allergy_form = AllergyForm(request.form)
    allergy_form.allergy_type.choices = constants.ALLERGIES.items()
    allergy_form.reaction.choices = constants.ALLERGIC_REACTIONS.items()
    oral_hygiene_form = OralHygieneForm(request.form)
    oral_hygiene_form.oral_type.choices = constants.ORAL_HYGIENE.items()

    if survey_entry:
        question = (
            meta.session.query(anamnesis.Question)
                .join(anamnesis.SurveyQuestionsOrder)
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
        if question: 
            anamnesis_values['question_id'] = question.id
        if survey_entry: 
            survey_entry += 1
        
        if ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_MEDICAL_HISTORY
            and medical_history_form.validate() ):
            values = {
                'type': medical_history_form.medical_type.data,
                'disease': medical_history_form.disease.data,
                'name': medical_history_form.denomination.data,
                'icd10': medical_history_form.icd10.data,
                'comment': medical_history_form.medical_comment.data,
                }
            values.update(anamnesis_values)
            new_medical_history = anamnesis.MedicalHistory(**values)
            meta.session.add(new_medical_history)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_ADDICTION
            and addiction_form.validate() ):
            values = {
                'type': addiction_form.addiction_type.data,
                'comment': addiction_form.addiction_comment.data,
                'begin': addiction_form.begin_addiction.data,
                'end': addiction_form.end_addiction.data
                }
            values.update(anamnesis_values)
            new_addiction = anamnesis.Addiction(**values)
            meta.session.add(new_addiction)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_TREATMENT
            and treatment_form.validate() ):
            values = {
                'name': treatment_form.molecule.data,
                'posologia': treatment_form.posologia.data,
                'begin': treatment_form.begin_treatment.data,
                'end': treatment_form.end_treatment.data
                }
            values.update(anamnesis_values)
            new_treatment = anamnesis.Treatment(**values)
            meta.session.add(new_treatment)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_PAST_SURGERY
            and past_surgery_form.validate() ):
            values = {
                'surgery_type': past_surgery_form.surgery_type.data,
                'problem': past_surgery_form.problem.data,
                'complication': past_surgery_form.complication.data,
                }
            values.update(anamnesis_values)
            new_past_surgery = anamnesis.PastSurgery(**values)
            meta.session.add(new_past_surgery)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_ALLERGY
            and allergy_form.validate() ):
            values = {
                'type': allergy_form.allergy_type.data,
                'allergen': allergy_form.allergen.data,
                'reaction': allergy_form.reaction.data,
                }
            values.update(anamnesis_values)
            new_allergy = anamnesis.Allergy(**values)
            meta.session.add(new_allergy)
            meta.session.commit()

        elif ( anamnesis_form.anamnesis_type.data ==
                                        constants.ANAMNESIS_ORAL_HYGIENE
            and oral_hygiene_form.validate() ):
            values = {
                'type': oral_hygiene_form.oral_type.data,
                'frequency': oral_hygiene_form.frequency.data,
                'comment': oral_hygiene_form.oral_comment.data
                }
            values.update(anamnesis_values)
            new_oral_hygiene = anamnesis.OralHygiene(**values)
            meta.session.add(new_oral_hygiene)
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
                                    oral_hygiene_form=oral_hygiene_form,
                                    constants=constants,
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
                                    oral_hygiene_form=oral_hygiene_form,
                                    constants=constants,
                                    clear_form=clear_form)

@app.route('/patient/anamnesis?pid=<int:patient_id>')
@app.route('/patient/anamnesis?pid=<int:patient_id>&aid=<int:appointment_id>')
def list_anamnesis(patient_id, appointment_id=None):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE,
                        constants.ROLE_ASSISTANT ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    survey_form = ChooseSurveyForm(request.form)
    survey_form.survey_id.choices =\
        meta.session.query(anamnesis.Survey.id, anamnesis.Survey.name).all()

    patient, appointment = checks.get_patient_appointment(patient_id, 
                                                                appointment_id)
    global_anamnesis = with_polymorphic(anamnesis.Anamnesis, '*')
    patient_anamnesis = (
        meta.session.query(global_anamnesis)
            .filter(anamnesis.Anamnesis.patient_id == patient_id)
            .order_by(anamnesis.Anamnesis.anamnesis_type,
                        anamnesis.Anamnesis.alert.desc(),
                        anamnesis.MedicalHistory.type,
                        anamnesis.MedicalHistory.disease,
                        anamnesis.Anamnesis.time_stamp)
            .all()
        )
  
    doctor = meta.session.query(md.MedecineDoctor).filter(
        md.MedecineDoctor.id == patient.gen_doc_id).one_or_none()
    return render_template("patient_anamnesis.html",
                            patient=patient,
                            appointment=appointment,
                            patient_anamnesis=patient_anamnesis,
                            doctor=doctor,
                            survey_form=survey_form,
                            constants=constants)

@app.route('/update/anamnesis?pid=<int:patient_id>')
def update_anamnesis(patient_id):
    pass


@app.route('/portal/anamnesis')
def portal_anamnesis():
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
    def _new_position_superior(position_form, questions_in_survey):
        for question in questions_in_survey:
            if question.question_id == int(position_form.question_id.data):
                question.position = position_form.new_position.data
                meta.session.commit()
                continue
            if ( question.position <= position_form.new_position.data
                and question.position > int(position_form.old_position.data) ):
                question.position -= 1
                meta.session.commit()
                continue

    def _new_position_inferior(position_form, questions_in_survey):
        for question in questions_in_survey:
            if question.question_id == int(position_form.question_id.data):
                question.position = position_form.new_position.data
                meta.session.commit()
                continue
            if ( question.position < int(position_form.old_position.data)
                and question.position >= position_form.new_position.data ):
                question.position += 1
                meta.session.commit()
                continue

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

        if position_form.new_position.data >\
                                        int(position_form.old_position.data):
            _new_position_superior(position_form, questions_in_survey)
        else:
            _new_position_inferior(position_form, questions_in_survey) 
        
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

