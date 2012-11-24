# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/30
# v0.5
# Licence BSD
#

from flask import render_template, request
import sqlalchemy
from sqlalchemy import or_
from odontux.models import meta, act, administration, md, users, medication
from odontux.odonweb import app
from gettext import gettext as _
from odontux import constants

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
                )).order_by(administration.Patient.lastname)
        return render_template('list_patients.html', patients=query.all(),
                                role_admin=constants.ROLE_ADMIN)
    
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

    if request.form["database"] == "doctor":
        query = meta.session.query(md.MedecineDoctor)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                md.MedecineDoctor.lastname.ilike(keyword),
                md.MedecineDoctor.firstname.ilike(keyword),
                ))
        return render_template('list_md.html', doctors=query.all())

    if request.form["database"] == "drug":
        query = meta.session.query(medication.DrugPrescribed)
        for keyword in keywords:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                medication.DrugPrescribed.alias.ilike(keyword),
                medication.DrugPrescribed.molecule.ilike(keyword)
                ))
        return render_template('list_drugs.html', drugs=query.all())

@app.route('/search/user')
def find_user():
    pass
