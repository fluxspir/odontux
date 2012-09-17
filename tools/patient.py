# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#


from model import meta, administration, schedule
from base import BaseTool

import sqlalchemy
import os
import sys


class GetPatientPromptTool(BaseTool):
    """ """

    tool_name = "get_patientprompt"

    def __init__(self):
        self.query = meta.session.query(administration.Patient)
    
    def run(self, args):
        patient_id = args[0]
        patient = self.query.filter(administration.Patient.id ==
                                    patient_id).one()
        patient_name = patient.lastname + " " + patient.firstname
        print(u"{}".format(patient_name).encode("utf_8"))


class TestPatientAppointmentTool(BaseTool):
    """ """

    tool_name = "test_patientappointment"

    def __init__(self):
        pass

    def run(self, args):
        try:
            patient_id = os.getenv("patient_id")
        except ValueError:
            sys.exit("need to be in a patient file")
        try:
            appointment_id = os.getenv("appointment_id")
        except ValueError:
            sys.exit("need to have an appointment")

        try:
            query = meta.session.query(schedule.Appointment)\
                    .filter(schedule.Appointment.patient_id == patient_id)\
                    .filter(schedule.Appointment.id == appointment_id).one()

            sys.exit(0)
        except sqlalchemy.exc.DataError:
            sys.exit(1)
        except sqlalchemy.orm.exc.NoResultFound:
            sys.exit(2)
