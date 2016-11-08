# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/31
# v0.5
# licence BSD
#

import pdb
from flask import ( session, render_template, request, redirect, url_for, 
                    jsonify, abort )
import sqlalchemy
from sqlalchemy import or_, and_, desc
from gettext import gettext as _

from odontux.odonweb import app
from odontux import constants, checks, gnucash_handler
from odontux.models import ( meta, act, schedule, administration, traceability,
                            assets, teeth, compta)
from odontux.views import cotation as views_cotation
from odontux.views import cost

from odontux.views.log import index

from decimal import Decimal
import datetime

#@app.route('/appointment_from_device_to_asset')
#def mv_appointment_id_from_device_to_asset(you_know_what_you_are_doing=False):
#    if not you_know_what_you_are_doing:
#        return abort(403)
#   
#    devices = ( meta.session.query(assets.Device)
#                .filter(assets.Device.old_appointment_id.isnot(None) )
#                .all()
#    )
#
#    for device in devices:
#        device.appointment_id = device.old_appointment_id
#        meta.session.commit()
#
#    return redirect(url_for('index'))
#
#@app.route('/pass_ste_dev_cat_to_asset_cat')
#def pass_ste_dev_cat_to_asset_cat(you_know_what_you_are_doing=False):
#    if not you_know_what_you_are_doing:
#        return abort(403)
#    
#    asset_categories = meta.session.query(assets.AssetCategory).all()
#    dev_cats = meta.session.query(assets.DeviceCategory).all()
#    for dev_cat in dev_cats:
#        dev_cat.is_sterilizable = dev_cat.sterilizable
#        dev_cat.sterilization_validity = dev_cat.validity
#        meta.session.commit()
#    asset_cat = meta.session.query(assets.AssetCategory).all()
#    for a_c in asset_cat:
#        if not a_c.is_sterilizable:
#            a_c.sterilization_validity = None
#            meta.session.commit()
#    return redirect(url_for('index'))
#
#@app.route('/update_last_price_asset_category')
#def update_last_price_asset_category(you_know_what_you_are_doing=False):
#    if not you_know_what_you_are_doing:
#        return abort(403)
#    
#    asset_categories = meta.session.query(assets.AssetCategory).all()
#    for a_c in asset_categories:
#        for asset in sorted(a_c.assets, key=lambda a_c: a_c.acquisition_date,
#                                                                reverse=True) :
#            a_c.last_price = asset.acquisition_price
#            meta.session.commit()
#            break
#    return redirect(url_for('index'))
#
#@app.route('/update_materio_vigilance_sterilization')
#def update_materio_vigilance_sterilization(you_know_whate_you_are_doing=False):
#    if not you_know_what_you_are_doing:
#        return abort(403)
#
#    sterilization_cycles = ( 
#        meta.session.query(traceability.SterilizationCycle).all()
#    )
#    for cycle in sterilization_cycles:  
#        autoclave_cycle_clinic_gestures = meta.session.query(act.ClinicGesture)
#        if cycle.cycle_type.is_test_cycle:
#            autoclave_cycle_clinic_gestures = (
#                autoclave_cycle_clinic_gestures
#                    .filter(or_(
#                        act.ClinicGesture.is_autoclave_test.is_(True),
#                        act.ClinicGesture.is_autoclave_cycle.is_(True)
#                        )
#                    )
#                    .all()
#            )
#        else:
#            autoclave_cycle_clinic_gestures = (
#                autoclave_cycle_clinic_gestures
#                    .filter(act.ClinicGesture.is_autoclave_cycle.is_(True))
#                    .all()
#
#                )
#        for cg in autoclave_cycle_clinic_gestures:
#            for mat_cg_ref in cg.materials:
#                material_used = cost.get_material_used(mat_cg_ref.id, 
#                                                        sterilization_cycle=cycle)
#                values = {
#                    'material_id': material_used.id,
#                    'sterilization_cycle_id': cycle.id,
#                    'quantity_used': mat_cg_ref.mean_quantity,
#                }
#                new_materio_vigilance = traceability.MaterioVigilance(**values)
#                meta.session.add(new_materio_vigilance)
#                meta.session.commit()
#
#                material_used.actual_quantity = ( 
#                    material_used.actual_quantity - mat_cg_ref.mean_quantity )
#                meta.session.commit()
#    return redirect(url_for('index'))
#
#@app.route('/update_materio_vigilance_base')
#def update_materio_vigilance_base(you_know_what_you_are_doing=False):
#    """ """
#    if not you_know_what_you_are_doing:
#        return abort(403)
#
#    old_materio_vigilance = meta.session.query(traceability.MaterioVigilanceB).all()
#    
#    for r in old_materio_vigilance:
#        values = {
#            'id' = old_materio_vigilance.id
#
#        }
######
#######
#####
#
#@app.route('/update_appointment_cotation_ref_base')
#def update_appointment_cotation_ref_base(you_know_what_you_are_doing=False):
#    """ Used for migration from appointment_gesture_reference to
#                                appointment_cotation_reference
#    """
#    if not you_know_what_you_are_doing:
#        return abort(403)
#
#    agr = meta.session.query(act.AppointmentGestureReference).all()
#    from odontux.models import statements
#    bagr = (meta.session.query(
#                        statements.BillAppointmentGestureReference).all()
#    )
#    for r in agr:
#        cot = ( meta.session.query(act.Cotation)
#                    .filter(act.Cotation.gesture_id == r.gesture_id,
#                            act.Cotation.healthcare_plan_id == r.healthcare_plan_id
#                    )
#                    .one()
#        )
#        values = {
#            'id': r.id,
#            'appointment_id': r.appointment_id,
#            'cotation_id': cot.id,
#            'anatomic_location': r.anatomic_location,
#            'price': r.price,
#            'invoice_id': r.invoice_id,
#            'is_paid': r.is_paid,
#        }
#        new_acr = act.AppointmentCotationReference(**values)
#        meta.session.add(new_acr)
#        meta.session.commit()
#
#    for r in bagr:
#        values = {
#            'id': r.id,
#            'bill_id': r.bill_id,
#            'appointment_cotation_id': r.appointment_gesture_id,
#        }
#        new_bacr = statements.BillAppointmentCotationReference(**values)
#        meta.session.add(new_bacr)
#        meta.session.commit()
#
#    return redirect(url_for('index'))
#
#
#
