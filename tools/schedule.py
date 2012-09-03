# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from model import meta, schedule
from base import BaseCommand

import os
import sys


class GetAppointmentTool(BaseCommand):
    """ """

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
