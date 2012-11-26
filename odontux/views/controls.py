# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/25
# v0.5
# Licence BSD
#

import sqlalchemy
from flask import session
from gettext import gettext as _

from odontux.models import meta, administration, schedule

def quit_patient_file():
    try:
        if session['patient']:
            session.pop('patient', None)
    except KeyError:
        pass

def quit_appointment():
    try:
        if session['appointment']:
            session.pop('appointment', None)
    except KeyError:
        pass

def is_patient_self_appointment():
    """ 
    Test if the patient is the one who has the appointment.
    Returns True if there isn't any problem.
    False otherwise.

    This function should be use very frequently ; and anytime it would
    returns False, all odontux odonweb... might stop really quickly, because
    everything could get very nasty quickly...
    """
    # At first, look if we're in a patient file :
    try:
        patient_id = session['patient'].id
    except:
        print(_("Must be in patient file ; please feel in the session "
                "variable"))
        return False

    # Then, verify we're in an appointment, too :
    try:
        appointment_id = session['appointment'].id
    except:
        print(_("Must be in an appointment for that kind of action"))
        return False

    # Verify now if in the database, this patient is connected to this 
    # appointment
    try:
        meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.patient_id == patient_id)\
            .filter(schedule.Appointment.id == appointment_id)\
            .one()
        return True
    except sqlalchemy.exc.DataError:
        print(_(""))
        return False
    except sqlalchemy.orm.exc.NoResultFound:
        print(_("Patient wasn't this appointment owner ; error !"))
        return False
