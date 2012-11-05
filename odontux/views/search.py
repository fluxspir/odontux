# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# Licence BSD
#

from flask import render_template, request
import sqlalchemy
from sqlalchemy import or_
from odontux.models import meta, act, administration, users
from odontux.odonweb import app
from gettext import gettext as _

@app.route('/search/', methods=['GET', 'POST'])
def find():
    """ """
    keywords = request.form["keywords"].encode("utf_8").split()

    if request.form["database"] == "patient":
        query = meta.session.query(administration.Patient)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                administration.Patient.lastname.ilike(keyword),
                administration.Patient.firstname.ilike(keyword),
                administration.Patient.preferred_name.ilike(keyword),
                administration.Patient.correspondence_name.ilike(keyword)
                ))
        return render_template('search_patient.html', patients=query.all())
    
    if request.form["database"] == "act":
        query = meta.session.query(act.ActType)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                act.ActType.alias.ilike(keyword),
                act.ActType.name.ilike(keyword),
                act.ActType.code.ilike(keyword)
                ))
        return render_template('list_act.html', gestures=query.all())

    if request.form["database"] == "odontuxuser":
        query = meta.session.query(users.OdontuxUser)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                users.OdontuxUser.username.ilike(keyword),
                users.OdontuxUser.firstname.ilike(keyword),
                users.OdontuxUser.lastname.ilike(keyword),
                users.OdontuxUser.role.ilike(keyword)
                ))
        return render_template('list_users.html', users=query.all())

@app.route('/search/user')
def find_user():
    pass
