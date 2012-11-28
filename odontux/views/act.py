# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from sqlalchemy import or_, and_
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants
from odontux.models import meta, act, cotation
from odontux.views.log import index

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     validators)
from odontux.views.forms import ColorField

cotationlocale = "Cotation" + constants.LOCALE.title()
CotationLocale = getattr(cotation, cotationlocale)

class ActTypeForm(Form):
    # Create the list of specialties that exist
    specialty_choices = meta.session.query(act.Specialty).all()
    choice_list = [ (choice.id, choice.name) 
                    for choice in specialty_choices ]
    # Begin Form
    specialty_id = SelectField('specialty', choices=choice_list, coerce=int)
    cotationfr_id = TextField('cotationfr_id')
    code = TextField('code')
    alias = TextAreaField('alias')
    name = TextAreaField('name')
    color = ColorField('color')

@app.route('/acttype?keywords=<keywords>&ordering=<ordering>')
def list_acttype(keywords="", ordering=""):
    """ The target is too display dentist's gesture, describing it, its value..
    """
    keywords = keywords.split()
    ordering = ordering.split()
    # Get the acts list, named as "gesture", because it is the gesture
    # the dentist make in the patient mouth.
    query = meta.session.query(act.ActType)
    # If we only need ones of a specialty : 
    if request.form and request.form['specialty']:
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == request.form['specialty'].one())
            query = query.filter(act.ActType.specialty_id == specialty.id)
        except sqlalchemy.orm.exc.NoResultFound:
            pass
    # Filter by keywords
    if keywords:
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                act.ActType.alias.ilike(keyword),
                act.ActType.name.ilike(keyword),
                act.ActType.code.ilike(keyword),
                (and_(
                    act.ActType.specialty_id == act.Specialty.id,
                    act.Specialty.name.ilike(keyword)
                    )
                )
            ))
    # We want to order the result to find what we are looking for more easily
    if not ordering:
        ordering = [ act.ActType.specialty_id, act.ActType.alias ]
    for o in ordering:
        query = query.order_by(o)
    gestures = query.all()

    gestures_list = []
    # We now need to know what the "cotationfr_id" correspond to
    # TODO : "cotation_locale_id" 
    for gesture in gestures:
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == gesture.specialty_id)\
                .one()
        except sqlalchemy.orm.exc.NoResultFound:
            specialty = ""
        cotat = meta.session.query(CotationLocale)\
            .filter(CotationLocale.id == gesture.cotationfr_id)\
            .one()
        ngap = meta.session.query(cotation.NgapKeyFr)\
            .filter(cotation.NgapKeyFr.id == cotat.key_id).one()

        gestures_list.append( (gesture, specialty, cotat, ngap) )
    return render_template('list_act.html', 
                            gestures_list=gestures_list)

@app.route('/act/add/', methods=['GET', 'POST'])
@app.route('/add/act/', methods=['GET', 'POST'])
def add_acttype():
    """ """
    # TODO  BECAUSE DIFFICULT TO MAKE IT "PERFECT"
    form = ActTypeForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}
        values['specialty_id'] = form.specialty_id.data
        values['cotationfr_id'] = form.cotationfr_id.data
        values['code'] = form.code.data
        values['alias'] = form.alias.data
        values['name'] = form.name.data
        values['color'] = form.color.data
        new_acttype = act.ActType(**values)
        meta.session.add(new_acttype)
        meta.session.commit()
        return redirect(url_for('list_acttype'))
    return render_template('/add_act.html', form=form)

@app.route('/act/update_acttype=<int:acttype_id>/', methods=['GET', 'POST'])
def update_acttype(acttype_id):
    acttype = meta.session.query(act.ActType).filter\
              (act.ActType.id == acttype_id).one()
    specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == acttype.specialty_id).one()
    if not acttype:
        return redirect(url_for('list_acttype'))
    form = ActTypeForm(request.form)

    if request.method == 'POST' and form.validate():
        acttype.specialty_id = form.specialty_id.data
        acttype.cotationfr_id = form.cotationfr_id.data
        acttype.code = form.code.data
        if form.alias.data:
            acttype.alias = form.alias.data
        if form.name.data:
            acttype.name = form.name.data
        acttype.color = form.color.data
        meta.session.commit()
        return redirect(url_for('list_acttype'))
    return render_template('/update_act.html', 
                            form=form, 
                            acttype=acttype, 
                            specialty=specialty
                            )
