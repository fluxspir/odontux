# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from models import meta, schedule
from base import BaseTool

import sqlalchemy
import os
import sys


class GetAppointmentTool(BaseTool):
    """
    Prints the last appointment id for the patient
    Needed for the switch_patient function in bashodontuxrc, to set the 
    appointment_id env variable to last appointment.
    """

    tool_name = "get_appointment"

    def __init__(self):
        self.query = meta.session.query(schedule.Appointment)

    def run(self, args):
        if not os.getenv("patient_id"):
            sys.exit("enter patient file please")
        else:
            patient_id = os.getenv("patient_id")

        appointment = self.query.filter(schedule.Appointment.patient_id ==
                                        patient_id).all()
        try:
            appointment_id = appointment[-1].id
        except IndexError:
            appointment_id = "OUT"
        print(appointment_id)


class GetAppointmentPatientTool(BaseTool):
    """
    Prints patient_id who assist on appointment in args
    Needed for the "next_appointment" function in bashodontuxrc
    """

    tool_name = "get_appointmentpatient"
    
    def __init__(self):
        self.query = meta.session.query(schedule.Appointment)

    def run(self, appointment_id):
        try:
            appointment = self.query.filter(schedule.Appointment.id ==
                                            int(appointment_id[0])).one()
        except sqlalchemy.orm.exc.NoResultFound:
            sys.exit(_("Bad appointment id given in argument"))

        print(appointment.patient_id)
