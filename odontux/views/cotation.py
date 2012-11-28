# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/15
# v0.5
# Licence BSD
#

from flask import session, render_template, request, redirect, url_for
from gettext import gettext as _
from wtforms import ( Form, TextField, HiddenField, SelectField, IntegerField,
                    validators )
import sqlalchemy
from sqlalchemy import or_, and_

from odontux import constants
from odontux.odonweb import app
from odontux.models import meta, cotation, act

cotationlocale = "Cotation" + constants.LOCALE.title()
CotationLocale = getattr(cotation, cotationlocale)

class NgapKeyFrForm(Form):
    name = TextField(_('name'), [validators.Required(
                      message=_("Please give a name"))])
    key = TextField(_('key'), [validators.Required(
                     message=_("Specify a key-code")),
                        validators.Length(min=1, max=5,
                     message=_("key must be between 1 and 5 letters"))])
    unit_price = TextField(_('unit_price'), [validators.Required(
                            message=_("please write a unit_price"))])

class CmuKeyFrForm(Form):
    key = TextField(_('key'), [validators.Required(
                        message=_("Please enter a key")),
                        validators.Length(min=1, max=5,
                        message=_("key between 1 and 5 letters"))])
    name = TextField(_('name'), [validators.Required(
                        message=_("Please name the use of key"))])

class MajorationFrForm(Form):
    name = TextField(_('name'), [validators.Required(
                        message=_("Please specify the majoration reason"))])
    price = TextField(_('price'), [validators.Required(
                        message=_("Give the price of the majoration"))])

class CotationFrForm(Form):
    # choices list
    ngap_list = []
    cmu_list = []
    for ngap in meta.session.query(cotation.NgapKeyFr).all():
        ngap_list.append( (ngap.id, ngap.key + "-" + ngap.name) )
    for cmu in meta.session.query(cotation.CmuKeyFr).all():
        cmu_list.append( (cmu.id, cmu.key + "-" + cmu.name) )
    # Form
    cotationfr_id = HiddenField(_('ID'))
    key_id = SelectField(_('key_id'), [validators.Required(
                            message=_("Must provide a ngap key"))],
                            choices=ngap_list)
    key_cmu_id = SelectField(_('key_cmu_id'), [validators.Optional()],
                            choices=cmu_list)
    adult_multiplicator = TextField(_('adult_multiplicator'))
    kid_multiplicator = TextField(_('kid_multiplicator'))
    adult_cmu_num = TextField(_('adult_cmu_num'))
    kid_cmu_num = TextField(_('kid_cmu_num'))
    exceeding_adult_normal = TextField(_('exceeding_adult_normal'))
    exceeding_kid_normal = TextField(_('exceeding_kid_normal'))
    exceeding_adult_cmu = TextField(_('exceeding_adult_cmu'))
    exceeding_kid_cmu = TextField(_('exceeding_kid_cmu'))


ngapkeyfr_fields = [ "name", "key", "unit_price" ]
cmukeyfr_fields = [ "key", "name" ]
majorationfr_fields = [ "name", "price" ]
cotationfr_fields = ["key_id", "key_cmu_id", "adult_multiplicator", 
                     "kid_multiplicator", "adult_cmu_num", "kid_cmu_num",
                     "exceeding_adult_normal", "exceeding_kid_normal",
                     "exceeding_adult_cmu", "exceeding_kid_cmu" ]

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

    cotations = meta.session.query(CotationLocale).all()

    cotat_list = []
    for cotat in cotations:
        # Get all the gesture (acttype) that user is looking for :
        all_gestures = acttypes.filter(act.ActType.cotationfr_id == 
                                                           cotat.id).all()
        gestures = []
        if all_gestures:
            for gesture in all_gestures:
                # We want to know this gesture is in what kind of specialty
                # creating a tuple (gesture, specialty)
                try:
                    specialty = meta.session.query(act.Specialty)\
                        .filter(act.Specialty.id == gesture.specialty_id)\
                        .one()
                except sqlalchemy.orm.exc.NoResultFound:
                    specialty = ""
                gestures.append( (gesture, specialty) )

            ngap = meta.session.query(cotation.NgapKeyFr)\
                .filter(cotation.NgapKeyFr.id == cotat.key_id).one()
            try:
                cmu = meta.session.query(cotation.CmuKeyFr)\
                    .filter(cotation.CmuKeyFr.id == cotat.key_cmu_id).one()
            except sqlalchemy.orm.exc.NoResultFound:
                cmu = ""
            cotat_list.append( (gestures, cotat, ngap, cmu) )

    return render_template('list_cotations.html', cotat_list=cotat_list)


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


@app.route('/cotation/update_ngap/id=<int:ngap_id>', methods=['POST'])
def update_ngap(ngap_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))

    ngap = meta.session.query(cotation.NgapKeyFr)\
            .filter(cotation.NgapKeyFr.id == ngap_id).one()
    form = NgapKeyFrForm(request.form)

    if request.method == 'POST' and form.validate():
        for f in ngapkeyfr_fields:
            setattr(ngap, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/add_ngap', methods=['POST'])
def add_ngap():
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    form = NgapKeyFrForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in ngapkeyfr_fields}
        new_ngapkeyfr = cotation.NgapKeyFr(**args)
        meta.session.add(new_ngapkeyfr)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/delete_ngap/id=<int:ngap_id>', methods=['POST'])
def delete_ngap(ngap_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    if request.method == 'POST':
        try:
            ngap = meta.session.query(cotation.NgapKeyFr)\
                    .filter(cotation.NgapKeyFr.id == ngap_id).one()
            meta.session.delete(ngap)
            meta.session.commit()
            return redirect(url_for('show_ngap'))
        except:
            raise Exception(_("Ngap deleting problem"))

@app.route('/cotation/update_cmu/id=<int:cmu_id>', methods=['POST'])
def update_cmu(cmu_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))

    cmu = meta.session.query(cotation.CmuKeyFr)\
            .filter(cotation.CmuKeyFr.id == cmu_id).one()
    form = CmuKeyFrForm(request.form)

    if request.method == 'POST' and form.validate():
        for f in cmukeyfr_fields:
            setattr(cmu, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/add_cmu', methods=['POST'])
def add_cmu():
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    form = CmuKeyFrForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in cmukeyfr_fields}
        new_cmukeyfr = cotation.CmuKeyFr(**args)
        meta.session.add(new_cmukeyfr)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/delete_cmu/id=<int:cmu_id>', methods=['POST'])
def delete_cmu(cmu_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    if request.method == 'POST':
        try:
            cmu = meta.session.query(cotation.CmuKeyFr)\
                    .filter(cotation.CmuKeyFr.id == cmu_id).one()
            meta.session.delete(cmu)
            meta.session.commit()
            return redirect(url_for('show_ngap'))
        except:
            raise Exception(_("CMU deleting problem"))

@app.route('/cotation/update_majoration/id=<int:majoration_id>', 
            methods=['POST'])
def update_majoration(majoration_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))

    majoration = meta.session.query(cotation.MajorationFr)\
            .filter(cotation.MajorationFr.id == majoration_id).one()
    form = MajorationFrForm(request.form)

    if request.method == 'POST' and form.validate():
        for f in majorationfr_fields:
            setattr(majoration, f, getattr(form, f).data)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/add_majoration', methods=['POST'])
def add_majoration():
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    form = MajorationFrForm(request.form)
    if request.method == 'POST' and form.validate():
        args = {f: getattr(form, f).data for f in majorationfr_fields}
        new_majorationfr = cotation.MajorationFr(**args)
        meta.session.add(new_majorationfr)
        meta.session.commit()
        return redirect(url_for('show_ngap'))

@app.route('/cotation/delete_majoration/id=<int:majoration_id>', 
            methods=['POST'])
def delete_majoration(majoration_id):
    if not session['role'] == constants.ROLE_DENTIST:
        return redirect(url_for('show_ngap'))
    if request.method == 'POST':
        try:
            majoration = meta.session.query(cotation.MajorationFr)\
                    .filter(cotation.MajorationFr.id == majoration_id).one()
            meta.session.delete(majoration)
            meta.session.commit()
            return redirect(url_for('show_ngap'))
        except:
            raise Exception(_("Majoration deleting problem"))
