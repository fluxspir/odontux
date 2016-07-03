# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/25
# v0.5
# Licence BSD
#

import pdb
import sqlalchemy
from sqlalchemy import cast, Date
from flask import session
from gettext import gettext as _

import os
import ConfigParser

import datetime

import sqlalchemy

from odontux.models import (
                            meta, 
                            administration, 
                            schedule,
                            act,
                            teeth,
                            md,
                            users,
                            assets
                           )

def get_odontux_folder():
    parser = ConfigParser.ConfigParser()
    home = os.path.expanduser("~")
    parser.read(os.path.join(home, ".odontuxrc"))
    odontux_folder = parser.get("environment", "odontux_folder")
    if not os.path.exists(odontux_folder):
        os.makedirs(odontux_folder)
    return odontux_folder

def get_odontux_document_folder():
    parser = ConfigParser.ConfigParser()
    home = os.path.expanduser("~")
    parser.read(os.path.join(home, ".odontuxrc"))
    odontux_folder = get_odontux_folder()
    document_folder_name = parser.get("environment", "document_folder")
    document_folder = os.path.join(odontux_folder, document_folder_name)
    if not os.path.exists(document_folder):
        os.makedirs(document_folder)
    return document_folder

def get_dental_office_logo():
    parser = ConfigParser.ConfigParser()
    home = os.path.expanduser("~")
    parser.read(os.path.join(home, ".odontuxrc"))
    odontux_folder = get_odontux_folder()
    odontux_logo = parser.get("environment", "odontux_logo")
    return os.path.join(odontux_folder, odontux_logo)

def get_patient(patient_id):
    try:
        patient = meta.session.query(administration.Patient)\
            .filter(administration.Patient.id == patient_id)\
            .one()
        return patient
    except sqlalchemy.orm.exc.NoResultFound:
        return False

def get_patient_appointment(patient_id=0, appointment_id=0):
    if appointment_id:
        appointment = (
            meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id == appointment_id
                ).one_or_none()
        )
    else:
        if not patient_id:
            return None, None
        appointment = (
            meta.session.query(schedule.Appointment).join(schedule.Agenda)
                .filter(
                    schedule.Appointment.patient_id == patient_id, 
                    (cast(schedule.Agenda.starttime,Date) <= 
                                                    datetime.date.today() ) )
                .order_by(schedule.Agenda.starttime.desc())
                .first()
        )
    return appointment.patient, appointment

def get_patient_acts(patient_id, appointment_id=None, ordering=[]):
    """ The purpose of this function is to filter, then order and finally 
    return acts made to a specific patient, specifying exactly what act was
    made with its name, and not only its ID.
    Returns a list of tuples (gesture, tooth, appointment, act_info, specialty)
    """
    # Our principal query will be on the "AppointmentGestureReference" table:
    query = meta.session.query(act.AppointmentGestureReference)

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
            act.AppointmentGestureReference.appointment_id.in_(RVlist))

    if ordering:
        for o in ordering:
            query = query.order_by(o)

    acts = []
    for gesture in query.all():
        # First, identify if the act was made on a tooth, and gives info about
        # that tooth
        # We need to know in which appointment this act occurs, for the date
        appointment = meta.session.query(schedule.Appointment)\
            .filter(schedule.Appointment.id == gesture.appointment_id).one()

        # Then, we need some human readable infos about the act, instead of 
        # an obscur ID
        act_info = meta.session.query(act.Gesture)\
            .filter(act.Gesture.id == gesture.gesture_id).one()

        # And eventually, get the specialty for knowing in which area the 
        # patient is treated for.
        try:
            specialty = meta.session.query(act.Specialty)\
                .filter(act.Specialty.id == act_info.specialty_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            specialty = ""
        

        # Fill in the acts_list with a tuple
        acts.append( ( gesture, appointment, act_info, specialty) )

    return acts


def is_body_already_in_database(data, body_type="patient"):
    """ 
    Function not working with the commands add_patient / add_md
    because it gets the
        " form.xxx.data "
    and commands come with  " options.xxx " without the final "data" attribute

    we need a trick to change it.
    """
    if body_type == "patient":
        patient = meta.session.query(administration.Patient)\
            .filter(administration.Patient.lastname == data.lastname.data)\
            .filter(administration.Patient.firstname == 
                    data.firstname.data)\
            .filter(administration.Patient.dob == data.dob.data)\
            .one_or_none()
        return patient

    elif body_type == "md":
        body = ( meta.session.query(md.MedecineDoctor)
                .filter(md.MedecineDoctor.lastname == data.lastname.data,
                md.MedecineDoctor.firstname == data.firstname.data)
                .one_or_none()
        )
        return body
   
    elif body_type == "provider":
        body = ( meta.session.query(assets.AssetProvider).filter(
                assets.AssetProvider.name == data.name.data)
                .one_or_none()
        )
        return body
    else:
        return None
