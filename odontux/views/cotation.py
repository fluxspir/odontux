# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/15
# v0.5
# Licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for, abort
from gettext import gettext as _
from wtforms import ( Form, TextField, HiddenField, SelectField, IntegerField,
                    DecimalField, BooleanField, SubmitField, validators )
import sqlalchemy
from sqlalchemy import or_, and_

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, act, compta

class HealthCarePlanForm(Form):
    healthcare_plan_id = HiddenField(_('id'))
    name = TextField(_('Name of new Healthcare Plan'), [validators.Required()])
    fees = DecimalField(_("Dentist hour's fees"))
    submit = SubmitField(_('Update'))

class CotationForm(Form):
    cotation_id = HiddenField(_('ID'))
    healthcare_plan_id = SelectField(_('healthcare_plan_name'), coerce=int)
    gesture_id = SelectField(_('Gesture'), coerce=int)
    price = DecimalField(_('price'), [validators.Optional()])
    active = BooleanField(_('active'))

class MajorationForm(Form):
    majoration_id = HiddenField(_('id'))
    reason = TextField(_('Majoration reason'), [validators.Required()] )
    percentage = DecimalField(_('Percentage'), [validators.Required()] )

@app.route('/cotation?keywords=<keywords>&ordering=<ordering>')
def list_cotations(keywords="", ordering=""):
    keywords = keywords.split()
    ordering = ordering.split()
    gestures = meta.session.query(act.Gesture)
    if keywords:
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            gestures = gestures.filter(or_(
                act.Gesture.alias.ilike(keyword),
                act.Gesture.name.ilike(keyword),
                act.Gesture.code.ilike(keyword),
                (and_(
                    act.Gesture.specialty_id == act.Specialty.id,
                    act.Specialty.name.ilike(keyword)
                    )
                )
            ))
    
    if ordering:
        for o in ordering:
            gestures = gestures.order_by(o)

    cotations = meta.session.query(act.Cotation).all()

    return render_template('list_cotations.html', cotations=cotations)

@app.route('/add/healthcare_plan', methods=['GET', 'POST'])
def add_healthcare_plan():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    healthcare_plan_form = HealthCarePlanForm(request.form)

    if request.method == 'POST' and healthcare_plan_form.validate():
        values = { 
            'name': healthcare_plan_form.name.data
        }
        new_healthcare_plan = act.HealthCarePlan(**values)
        meta.session.add(new_healthcare_plan)
        try:
            meta.session.commit()
        except sqlalchemy.exc.IntegrityError:
            meta.session.rollback()

        return redirect(url_for('list_healthcare_plan'))

    return render_template('add_healthcare_plan.html', 
                                healthcare_plan_form=healthcare_plan_form)

@app.route('/add/majoration', methods=['GET', 'POST'])
def add_majoration():
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    majoration_form = MajorationForm(request.form)
    if request.method == 'POST' and majoration_form.validate():
        values = {
            'reason': majoration_form.reason.data,
            'percentage': majoration_form.percentage.data,
        }
        new_majoration = compta.Majoration(**values)
        meta.session.add(new_majoration)
        meta.session.commit()
        return redirect(url_for('list_healthcare_plan') )

    return render_template('add_majoration.html',
                                    majoration_form=majoration_form)

@app.route('/list/healthcare_plan')
def list_healthcare_plan():
    healthcare_plans = meta.session.query(act.HealthCarePlan).all()
    majorations = meta.session.query(compta.Majoration).all()
    return render_template('list_healthcare_plan.html', 
                                            majorations=majorations,
                                            healthcare_plans=healthcare_plans)

@app.route('/update/healthcare_plan?id=<int:healthcare_plan_id>', 
                                                    methods=['GET', 'POST'])
def update_healthcare_plan(healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return abort(403)

    healthcare_plan = ( meta.session.query(act.HealthCarePlan)
                        .filter(act.HealthCarePlan.id == healthcare_plan_id)
                        .one()
                )

    healthcare_plan_form = HealthCarePlanForm(request.form)
    hcp_user_ref = ( 
        meta.session.query(act.HealthCarePlanUserReference)
            .filter(
                act.HealthCarePlanUserReference.healthcare_plan_id ==
                                                        healthcare_plan_id,
                act.HealthCarePlanUserReference.user_id == 
                                                        session['user_id']
            )
            .one_or_none()
    )

    if request.method == 'POST' and healthcare_plan_form.validate():
        if hcp_user_ref:
            hcp_user_ref.hour_fees = healthcare_plan_form.fees.data
        else:
            values = {
                'hour_fees': healthcare_plan_form.fees.data,
                'user_id': session['user_id'],
                'healthcare_plan_id': healthcare_plan_id
            }
            new_hcp_user_fee = act.HealthCarePlanUserReference(**values)
            meta.session.add(new_hcp_user_fee)

        healthcare_plan.name = healthcare_plan_form.name.data
        meta.session.commit()
        return redirect(url_for('view_healthcare_plan', 
                                    healthcare_plan_id=healthcare_plan_id))

    healthcare_plan_form.name.data = healthcare_plan.name
    if hcp_user_ref:
        healthcare_plan_form.fees.data = hcp_user_ref.hour_fees

    return render_template('update_healthcare_plan.html',
                                healthcare_plan_form=healthcare_plan_form,
                                healthcare_plan=healthcare_plan)

@app.route('/update/majoration?mid=<int:majoration_id>', methods=['GET', 'POST'])
def update_majoration(majoration_id):
    authorized_roles = [ constants.ROLE_DENTIST ]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    majoration = ( meta.session.query(compta.Majoration)
                        .filter(compta.Majoration.id == majoration_id)
                        .one()
    )
    majoration_form = MajorationForm(request.Form)
    
    if request.method == 'POST' and majoration_form.validate():
        majoration.reason = majoration_form.reason.data
        majoration.percentage = majoration_form.percentage.data
        meta.session.commit()
        return redirect(url_for('view_majoration'))

    majoration_form.reason.data = majoration.reason
    majoration_form.percentage.data = majoration.percentage
    majoration_form.majoration_id.data = majoration.id
    return render_template('update_majoration.html',
                                    majoration_form=majoration_form)


@app.route('/view/healthcare_plan?id=<int:healthcare_plan_id>')
def view_healthcare_plan(healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    healthcare_plan = ( meta.session.query(act.HealthCarePlan)
                        .filter(act.HealthCarePlan.id == healthcare_plan_id)
                        .one()
                    )
    cotations = [ cotation for cotation in 
                    sorted(healthcare_plan.cotations, 
                            key=lambda cotation: (cotation.gesture.specialty.name,
                                                cotation.gesture.name) ) 
    ]
#    for cg_cot_ref in sorted(cotation.clinic_gestures,
#                            key=lambda cg_cot_ref: ( cg_cot_ref.appointment_number,
#                                                cg_cot_ref.appointment_sequence)):
#
    
    return render_template('view_healthcare_plan.html', 
                                healthcare_plan=healthcare_plan,
                                cotations=cotations)

@app.route('/list_majoration')
def list_majoration():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    majorations = meta.session.query(compta.Majoration).all()
    return render_template('list_majoration.html', majorations=majorations)
   

@app.route('/view/majoration?id=<int:majoration_id>')
def view_majoration(majoration_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    majoration = ( meta.session.query(compta.Majoration)
                        .filter(compta.Majoration.id == majoration_id)
                        .one()
    )
    return render_template('view_majoration.html', majoration=majoration)

