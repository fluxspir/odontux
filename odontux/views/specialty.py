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

from wtforms import Form, TextField, validators
from odontux.views.forms import ColorField

class SpecialtyForm(Form):
    name = TextField('name', [validators.Required(), 
                     validators.Length(min=1, max=20, 
                     message=_("Must be less than 20 characters"))])
    color = ColorField('color')



@app.route('/specialty/')
@app.route('/specialties/')
def list_specialty():
    query = meta.session.query(act.Specialty).all()
    return render_template('specialty.html', specialties=query)


@app.route('/specialty/add/', methods=['GET', 'POST'])
@app.route('/specialties/add/', methods=['GET', 'POST'])
@app.route('/add/specialty/', methods=['GET', 'POST'])
@app.route('/add/specialties/', methods=['GET', 'POST'])
def add_specialty():
    form = SpecialtyForm(request.form)
    if request.method == 'POST' and form.validate():
        values = {}
        values['name'] = form.name.data
        values['color'] = form.color.data
        new_specialty = act.Specialty(**values)
        meta.session.add(new_specialty)
        meta.session.commit()
        return redirect(url_for('list_specialty'))
    return render_template('/add_specialty.html', form=form)


@app.route('/act/update_specialty/id=<int:specialty_id>/', 
            methods=['GET', 'POST'])
def update_specialty(specialty_id):
    specialty = meta.session.query(act.Specialty).filter\
              (act.Specialty.id == specialty_id).one()
    if not specialty:
        return redirect(url_for('list_specialty'))
    form = SpecialtyForm(request.form)

    if request.method == 'POST' and form.validate():
        if form.name.data != acttype.name:
            acttype.name = form.name.data
        if form.color.data != acttype.color:
            acttype.color = form.color.data
        return redirect(url_for('list_specialty'))
    return render_template('/update_spectialty.html', form=form, 
                            specialty=specialty)
