# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/25
# v0.5
# Licence BSD
#

import sqlalchemy
from flask import session
from gettext import gettext as _

from odontux.models import (
                            meta, 
                            administration, 
                            schedule,
                            act,
                            teeth,
                           )

import pdb

def in_patient_file():
    try:
        if session['patient_id']:
            return True
    except KeyError:
        return False
    return False

def quit_patient_file():
    try:
        if session['patient_id']:
            session.pop('patient_id', None)
    except KeyError:
        pass

def quit_appointment():
    try:
        if session['appointment_id']:
            session.pop('appointment_id', None)
    except KeyError:
        pass

def get_patient(patient_id):
    try:
        patient = meta.session.query(administration.Patient)\
            .filter(administration.Patient.id == patient_id)\
            .one()
    except sqlalchemy.orm.exc.NoResultFound:
        return False
    return patient

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
        patient_id = session['patient_id']
    except:
        print(_("Must be in patient file ; please feel in the session "
                "variable"))
        return False

    # Then, verify we're in an appointment, too :
    try:
        appointment_id = session['appointment_id']
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

def get_patient_acts(patient_id, appointment_id=None, ordering=[]):
    """ The purpose of this function is to filter, then order and finally 
    return acts made to a specific patient, specifying exactly what act was
    made with its name, and not only its ID.
    Returns a list of tuples (gesture, tooth, appointment, act_info, specialty)
    """
    # Our principal query will be on the "AppointmentActReference" table:
    query = meta.session.query(act.AppointmentActReference)

    # Get all appointments where the patient came, as it is while an 
    # appointment that acts are made on patient.
    appointments = meta.session.query(schedule.Appointment)\
        .filter(schedule.Appointment.patient_id == patient_id)
    if appointment_id:
        appointments = appointments.filter(
                schedule.Appointment.id == appointment_id)
    appointments = appointments.all()

    RVlist = [ RV.id for RV in appointments]
    query = query.filter(
            act.AppointmentActReference.appointment_id.in_(RVlist))

    if ordering:
        for o in ordering:
            query = query.order_by(o)

    acts = []
    for gesture in query.all():
        # First, identify if the act was made on a tooth, and gives info about
        # that tooth
        if gesture.tooth_id:
            tooth = meta.session.query(teeth.Tooth)\
                .filter(teeth.Tooth.id == gesture.tooth_id).one()
        else:
            tooth = None

        # We need to know in which appointment this act occurs, for the date
        appointment = meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.id == gesture.appointment_id).one()

        # Then, we need some human readable infos about the act, instead of 
        # an obscur ID
        act_info = meta.session.query(act.ActType)\
            .filter(act.ActType.id == gesture.act_id).one()

        # And eventually, get the specialty for knowing in which area the 
        # patient is treated for.
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == act_info.specialty_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            specialty = ""
        

        # Fill in the acts_list with a tuple
        acts.append( ( gesture, tooth, appointment, act_info, specialty) )

    return acts

