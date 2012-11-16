# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/15
# v0.5
# Licence BSD
#

from flask import session, render_template, request
from gettext import gettext as _
from wtforms import Form, TextField, validators

from odontux import constants
from odontux.odonweb import app
from odontux.models import meta, cotation

class NgapKeyFrForm(Form):
    name = TextField('name', [validators.Required(
                      message=_("Please give a name"))])
    key = TextField('key', [validators.Required(
                     message=_("Specify a key-code")),
                        validators.Length(min=1, max=5,
                     message=_("key must be between 1 and 5 letters"))])
    unit_price = TextField('unit_price', [validators.Required(
                            message=_("please write a unit_price"))])

class CmuKeyFrForm(Form):
    key = TextField('key', [validators.Required(
                        message=_("Please enter a key")),
                        validators.Length(min=1, max=5,
                        message=_("key between 1 and 5 letters"))])
    name = TextField('name', [validators.Required(
                        message=_("Please name the use of key"))])

class MajorationFrForm(Form):
    name = TextField('name', [validators.Required(
                        message=_("Please specify the majoration reason"))])
    price = TextField('price', [validators.Required(
                        message=_("Give the price of the majoration"))])

@app.route('/cotation/show_ngap/')
def show_ngap():
    query_ngap = meta.session.query(cotation.NgapKeyFr)\
            .order_by(cotation.NgapKeyFr.id).all()
    ngap_form = NgapKeyFrForm(request.form)
    query_cmu = meta.session.query(cotation.CmuKeyFr)\
            .order_by(cotation.CmuKeyFr.id).all()
    cmu_form = CmuKeyFrForm(request.form)
    query_majoration = meta.session.query(cotation.MajorationFr)\
            .order_by(cotation.MajorationFr.id).all()
    majoration_form = MajorationFrForm(request.form)
    return render_template('/show_ngap.html', query_ngap=query_ngap,
                            query_cmu=query_cmu, 
                            query_majoration=query_majoration,
                            ngap_form=ngap_form,
                            cmu_form=cmu_form,
                            majoration_form=majoration_form,
                            role_dentist=constants.ROLE_DENTIST)

@app.route('/cotation/update_ngap/id=<int:ngap_id>')
def update_ngap(ngap_id):
    pass
@app.route('/cotation/add_ngap')
def add_ngap():
    pass
@app.route('/cotation/update_cmu/id=<int:cmu_id>')
def update_cmu(cmu_id):
    pass
@app.route('/cotation/add_cmu')
def add_cmu():
    pass
@app.route('/cotation/update_majoration/id=<int:majoration_id>')
def update_majoration(majoration_id):
    pass
@app.route('/cotation/add_majoration')
def add_majoration():
    pass
