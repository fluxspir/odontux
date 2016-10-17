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

@app.route('/update_appointment_cotation_ref_base')
def update_appointment_cotation_ref_base(you_know_what_you_are_doing=False):
    """ Used for migration from appointment_gesture_reference to
                                appointment_cotation_reference
    """
    if not you_know_what_you_are_doing:
        return abort(403)

    agr = meta.session.query(act.AppointmentGestureReference).all()
    from odontux.models import statements
    bagr = (meta.session.query(
                        statements.BillAppointmentGestureReference).all()
    )
    for r in agr:
        cot = ( meta.session.query(act.Cotation)
                    .filter(act.Cotation.gesture_id == r.gesture_id,
                            act.Cotation.healthcare_plan_id == r.healthcare_plan_id
                    )
                    .one()
        )
        values = {
            'id': r.id,
            'appointment_id': r.appointment_id,
            'cotation_id': cot.id,
            'anatomic_location': r.anatomic_location,
            'price': r.price,
            'invoice_id': r.invoice_id,
            'is_paid': r.is_paid,
        }
        new_acr = act.AppointmentCotationReference(**values)
        meta.session.add(new_acr)
        meta.session.commit()

    for r in bagr:
        values = {
            'id': r.id,
            'bill_id': r.bill_id,
            'appointment_cotation_id': r.appointment_gesture_id,
        }
        new_bacr = statements.BillAppointmentCotationReference(**values)
        meta.session.add(new_bacr)
        meta.session.commit()

    return redirect(url_for('index'))



