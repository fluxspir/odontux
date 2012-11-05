# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# Licence BSD
#

from flask import render_template, request
import sqlalchemy
from sqlalchemy import or_
from odontux.models import meta, administration, users
from odontux.odonweb import app
from gettext import gettext as _

@app.route('/search/', methods=['GET', 'POST'])
def find():
    """ """
    if request.form["database"] == "patient":
        query = meta.session.query(administration.Patient)

    keywords = request.form["keywords"].split("\s")
    k_list = [ k_list.append(key[n:]) for n in range(len(key))]
    for keyword in k_list:
        keyword = '%{}%'.format(keyword)
        query = query.filter(or_(
            administration.Patient.lastname.ilike(keyword),
            administration.Patient.firstname.ilike(keyword),
            administration.Patient.preferred_name.ilike(keyword),
            administration.Patient.correspondence_name.ilike(keyword)
            ))
    return render_template('search_patient.html', patients=query.all())
        

@app.route('/search/user')
def find_user():
    pass
