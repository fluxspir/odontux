# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/15
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
from gettext import gettext as _
from wtforms import ( Form, TextField, HiddenField, SelectField, IntegerField,
                    DecimalField, validators )
import sqlalchemy
from sqlalchemy import or_, and_

from odontux import constants, checks
from odontux.odonweb import app
from odontux.models import meta, cotation, act

class PlanNameForm(Form):
    plan_name_id = HiddenField(_('id'))
    name = TextField(_('name'), [validators.Required()])

class CotationForm(Form):
    cotation_id = HiddenField(_('ID'))
    plan_name_id = SelectField(_('plan_name_id'), coerce=int)
    act_type_id = SelectField(_('act id'), coerce=int)
    code = TextField(_('code'), [validators.Required()])
    price = DecimalField(_('price'), [validators.Optional()])

@app.route('/cotation?keywords=<keywords>&ordering=<ordering>')
def list_cotations(keywords="", ordering=""):
    keywords = keywords.split()
    ordering = ordering.split()
    acttypes = meta.session.query(act.ActType)
    if keywords:
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            acttypes = acttypes.filter(or_(
                act.ActType.alias.ilike(keyword),
                act.ActType.name.ilike(keyword),
                act.ActType.code.ilike(keyword),
                (and_(
                    act.ActType.specialty_id == act.Specialty.id,
                    act.Specialty.name.ilike(keyword)
                    )
                )
            ))
    
    if ordering:
        for o in ordering:
            acttypes = acttypes.order_by(o)

    cotations = meta.session.query(cotation.Cotation).all()

    return render_template('list_cotations.html', cotations=cotations)

@app.route('/add/plan_name', methods=['GET', 'POST'])
def add_plan_name():
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    plan_name_form = PlanNameForm(request.form)

    if request.method == 'POST' and plan_name_form.validate():
        values = { 
            'name': plan_name_form.name.data
        }
        new_plan_name = cotation.PlanName(**values)
        meta.session.add(new_plan_name)
        meta.session.commit()

        return redirect(url_for('list_plan_name'))

    return render_template('add_plan_name.html', 
                                plan_name_form=plan_name_form)

@app.route('/list/plan_name')
def list_plan_name():
    plan_names = meta.session.query(cotation.PlanName).all()
    return render_template('list_plan_name.html', plan_names=plan_names)

@app.route('/update/plan_name?id=<int:plan_name_id>', methods=['GET', 'POST'])
def update_plan_name(plan_name_id):
    authorized_roles = [ constants.ROLE_DENTIST, constants.ROLE_NURSE, 
                        constants.ROLE_ASSISTANT, constants.ROLE_SECRETARY]
    if session['role'] not in authorized_roles:
        return redirect(url_for('index'))

    checks.quit_patient_file()
    checks.quit_appointment()
    
    plan_name = ( meta.session.query(cotation.PlanName)
                        .filter(cotation.PlanName.id == plan_name_id)
                        .one()
                )

    plan_name_form = PlanNameForm(request.form)

    if request.method == 'POST' and plan_name_form.validate():
        plan_name.name = plan_name_form.name.data
        meta.session.commit()
        return redirect(url_for('list_plan_name'))

    plan_name_form.name.data = plan_name.name

    return render_template('update_plan_name',
                                plan_name_form=plan_name_form,
                                plan_name=plan_name)

@app.route('/add/cotation', methods=['GET','POST'])
def add_cotation():
    pass
