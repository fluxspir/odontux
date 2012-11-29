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
from odontux.views import cotation as views_cotation
from odontux.views.log import index

from wtforms import (Form, BooleanField, TextField, TextAreaField, SelectField,
                     validators)
from odontux.views.forms import ColorField

cotationlocale = "Cotation" + constants.LOCALE.title()
CotationLocale = getattr(cotation, cotationlocale)

class SpecialtyForm(Form):
    name = TextField('name', [validators.Required(), 
                     validators.Length(min=1, max=20, 
                     message=_("Must be less than 20 characters"))])
    color = ColorField('color')

class ActTypeForm(Form):
    specialty_id = SelectField('specialty', coerce=int)
    cotationfr_id = SelectField('cotationfr_id', coerce=int)
    code = TextField('code')
    alias = TextAreaField('alias')
    name = TextAreaField('name')
    color = ColorField('color')


def get_specialty_field_list():
    return [ "name", "color" ]

def get_acttype_field_list():
    return [ "specialty_id", "cotationfr_id", "code", "alias", 
             "name", "color" ]


def get_specialty_choice_list():
    return [ (choice.id, choice.name) for choice in 
                                    meta.session.query(act.Specialty).all() ]

def get_cotationfr_choice_list():
    """ returns [ ( "cotation_id", "SC12 price" ), ] """

    cotationfr_choices = meta.session.query(CotationLocale)\
        .order_by(CotationLocale.key_id)\
        .order_by(CotationLocale.adult_multiplicator)\
        .all()
    cotats = []
    for cotat_choice in cotationfr_choices:
        ngap = meta.session.query(cotation.NgapKeyFr)\
            .filter(cotation.NgapKeyFr.id == cotat_choice.key_id)\
            .one()
        cotats.append( (cotat_choice, ngap ) )

    return [ (cotat.id, ngap.key + str(cotat.adult_multiplicator) + " " + 
              str(cotat.get_price(cotat.adult_multiplicator, 
                                  cotat.exceeding_adult_normal))
             ) for cotat, ngap in cotats 
           ]


####
# Specialties
####

@app.route('/specialty/')
@app.route('/specialties/')
def list_specialty(ordering=[]):
    query = meta.session.query(act.Specialty)
    if not ordering:
        ordering = [act.Specialty.id]
    for order in ordering:
        query = query.order_by(order)
    specialties = query.all()
    return render_template('list_specialty.html', specialties=specialties)

@app.route('/specialty/add/', methods=['GET', 'POST'])
def add_specialty():
    form = SpecialtyForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in get_specialty_field_list() }
        new_specialty = act.Specialty(**args)
        meta.session.add(new_specialty)
        meta.session.commit()
        return redirect(url_for('list_specialty'))
    return render_template('add_specialty.html', form=form)

@app.route('/act/update_specialty/id=<int:specialty_id>/', 
            methods=['GET', 'POST'])
def update_specialty(specialty_id):
    try:
        specialty = meta.session.query(act.Specialty).filter\
              (act.Specialty.id == specialty_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        return redirect(url_for('list_specialty'))

    form = SpecialtyForm(request.form)

    if request.method == 'POST' and form.validate():
        specialty.name = form.name.data
        specialty.color = form.color.data
        meta.session.commit()
        return redirect(url_for('list_specialty'))
    

    return render_template('update_specialty.html', form=form, 
                            specialty=specialty)


#####
# Acts
#####

@app.route('/acttype?keywords=<keywords>&ordering=<ordering>')
def list_acttype(keywords="", ordering=""):
    """ The target is too display dentist's gesture, describing it, its values.
    Looking in ActType table, we may decide to print only 
        acts from one specialty
        then filter by keyword
        ordering the printing
    
    The result will be a list of tuples :
     ( gesture, specialty, cotat, ngap )
    """
    keywords = keywords.encode("utf_8").split()
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
    if not acttype:
        return redirect(url_for('list_acttype'))
    try:
        specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == acttype.specialty_id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        specialty=""
    cotat = meta.session.query(CotationLocale)\
                .filter(CotationLocale.id == acttype.cotationfr_id).one()
    ngap = meta.session.query(cotation.NgapKeyFr)\
                .filter(cotation.NgapKeyFr.id == cotat.key_id).one()


    acttype_form = ActTypeForm(request.form)
    acttype_form.specialty_id.choices = get_specialty_choice_list()
    acttype_form.cotationfr_id.choices = get_cotationfr_choice_list()
    
    #TODO
    
    if request.method == 'POST' and acttype_form.validate():
        for f in get_acttype_field_list():
            setattr(acttype, f, getattr(acttype_form, f).data)
            #getattr(acttype, f) = getattr(acttype_form, f).data
        meta.session.commit()
        return redirect(url_for('list_acttype', 
                                keywords=acttype_form.name.data, 
                                ordering=" "))

    # For the GET method
    for f in get_acttype_field_list():
        getattr(acttype_form, f).data = getattr(acttype, f)

    specialty_form = SpecialtyForm(request.form)
    cotat_form = views_cotation.CotationFrForm(request.form)
    return render_template('/update_act.html', 
                            acttype_form=acttype_form, 
                            specialty_form=specialty_form,
                            cotat_form=cotat_form,
                            acttype=acttype
                            )
