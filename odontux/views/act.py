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

from wtforms import Form, BooleanField, TextField, PasswordField, validators

class ActTypeForm(Form):
    specialty_id = TextField('specialty_id')
    cotationfr_id = TextField('cotationfr_id')
    code = TextField('code', default=self.acttype.code)
    alias = TextField('alias')
    name = TextField('name')

@app.route('/act/')
def list_acttype():
    query = meta.session.query(act.ActType).all()
    return render_template('gesture.html', gestures=query)

@app.route('/act/update_acttype=<int:acttype_id>/', methods=['GET', 'POST'])
def update_acttype(acttype_id):
    acttype = meta.session.query(act.ActType).filter\
              (act.ActType.id == acttype_id).one()
    form = ActTypeForm(request.form, acttype)

    if not acttype:
        return redirect(url_for('/act'))
    if request.method == 'POST' and form.validate():
        acttype.specialty_id = form.specialty_id.data
        acttype.cotationfr_id = form.cotationfr_id.data
        acttype.code = form.code.data
        acttype.alias = form.alias.data
        acttype.name = form.name.data
        acttype.color = form.color.data
        meta.session.commit()
        return redirect(url_for('index'))
    return render_template('/update_act.html', form=form)
