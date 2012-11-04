# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

from flask import session, render_template, request, redirect, url_for
import sqlalchemy
from odontux.models import meta, act
from odontux.secret import SECRET_KEY
from odontux.odonweb import app
from gettext import gettext as _

from odontux.views.log import index

from wtforms import Form, BooleanField, TextField, TextAreaField, validators
from odontux.views.forms import ColorField


class ActTypeForm(Form):
    specialty_id = TextField('specialty_id')
    cotationfr_id = TextField('cotationfr_id')
    code = TextField('code')
    alias = TextAreaField('alias')
    name = TextAreaField('name')
    color = ColorField('color')

@app.route('/act/')
def list_acttype():
    query = meta.session.query(act.ActType).all()
    return render_template('list_act.html', gestures=query)

@app.route('/act/add/', methods=['GET', 'POST'])
@app.route('/add/act/', methods=['GET', 'POST'])
def add_acttype():
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
    form = ActTypeForm(request.form)

    if request.method == 'POST' and form.validate():
        if form.specialty_id.data != acttype.specialty_id \
        and not form.specialty_id.data == "None": 
            acttype.specialty_id = form.specialty_id.data
        if form.cotationfr_id.data != acttype.cotationfr_id:
            acttype.cotationfr_id = form.cotationfr_id.data
        if form.code.data != acttype.code:
            acttype.code = form.code.data
        if form.alias.data != acttype.alias:
            acttype.alias = form.alias.data
        if form.name.data != acttype.name:
            acttype.name = form.name.data
        if form.color.data != acttype.color:
            acttype.color = form.color.data
#        meta.session.commit()
        return redirect(url_for('list_acttype'))
    return render_template('/update_act.html', form=form, acttype=acttype)
