# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/15
# v0.5
# Licence BSD
#

import pdb
from flask import session, render_template, request, redirect, url_for
from gettext import gettext as _
from wtforms import ( Form, TextField, HiddenField, SelectField, IntegerField,
                    DecimalField, BooleanField, validators )
import sqlalchemy
from sqlalchemy import or_, and_

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, act

class HealthCarePlanForm(Form):
    healthcare_plan_id = HiddenField(_('id'))
    name = TextField(_('Name of new Healthcare Plan'), [validators.Required()])

class CotationForm(Form):
    cotation_id = HiddenField(_('ID'))
    healthcare_plan_id = SelectField(_('healthcare_plan_name'), coerce=int)
    gesture_id = SelectField(_('Gesture'), coerce=int)
    price = DecimalField(_('price'), [validators.Optional()])
    active = BooleanField(_('active'))

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

    checks.quit_patient_file()
    checks.quit_appointment()
    healthcare_plan_form = HealthCarePlanForm(request.form)

    if request.method == 'POST' and healthcare_plan_form.validate():
        values = { 
            'name': healthcare_plan_form.name.data
        }
        new_healthcare_plan = act.HealthCarePlan(**values)
        meta.session.add(new_healthcare_plan)
        meta.session.commit()

        return redirect(url_for('list_healthcare_plan'))

    return render_template('add_healthcare_plan.html', 
                                healthcare_plan_form=healthcare_plan_form)

@app.route('/list/healthcare_plan')
def list_healthcare_plan():
    healthcare_plans = meta.session.query(act.HealthCarePlan).all()
    return render_template('list_healthcare_plan.html', 
                                            healthcare_plans=healthcare_plans)

@app.route('/update/healthcare_plan?id=<int:healthcare_plan_id>', 
                                                    methods=['GET', 'POST'])
def update_healthcare_plan(healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    healthcare_plan = ( meta.session.query(act.HealthCarePlan)
                        .filter(act.HealthCarePlan.id == healthcare_plan_id)
                        .one()
                )

    healthcare_plan_form = HealthCarePlanForm(request.form)

    if request.method == 'POST' and healthcare_plan_form.validate():
        healthcare_plan.name = healthcare_plan_form.name.data
        meta.session.commit()
        return redirect(url_for('view_healthcare_plan'))

    healthcare_plan_form.name.data = healthcare_plan.name

    return render_template('update_healthcare_plan.html',
                                healthcare_plan_form=healthcare_plan_form,
                                healthcare_plan=healthcare_plan)

@app.route('/view/healthcare_plan?id=<int:healthcare_plan_id>')
def view_healthcare_plan(healthcare_plan_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    healthcare_plan = ( meta.session.query(act.HealthCarePlan)
                        .filter(act.HealthCarePlan.id == healthcare_plan_id)
                        .one()
                    )
    return render_template('view_healthcare_plan.html', 
                                healthcare_plan=healthcare_plan)

@app.route('/add/cotation', methods=['GET','POST'])
def add_cotation():
    pass
