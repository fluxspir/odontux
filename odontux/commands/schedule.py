# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from models import meta, schedule, administration
from base import BaseCommand

from gettext import gettext as _
from sqlalchemy import or_
import os
import sys

class AppointmentParser(BaseCommand):
    """ """

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="id of the patient, mandatory")
        parser.add_option("-u", "--user", action="store",\
                        type="string", dest="dentist_id",\
                        help="id of the dentist who handle the appointment.")
        parser.add_option("--emergency", "--urgence", action="store_true",\
                        dest="emergency",\
                        help="specify the patient was taken in emergency")
        parser.add_option("-r", "--reason", action="store",\
                        type="string", dest="reason",\
                        help="Few words ; will be written on schedule")
        parser.add_option("-d", "--diagnostic", action="store",\
                        type="string", dest="diagnostic",\
                        help="diagnostic of the complaint")
        parser.add_option("-t", "--treatment", action="store",\
                        type="string", dest="treatment",\
                        help="Few words, resume.")
        parser.add_option("-p", "-f", "--future", "--prognostic", 
                        action="store", type="string", dest="prognostic",\
                        help="prognostic of the treatment")
        parser.add_option("-a", "--advise", action="store",\
                        type="string", dest="advise",\
                        help="advise done to patient to help")
        parser.add_option("-n", "--next", action="store",\
                        type="string", dest="next_appointment",\
                        help="What's planned to do in next appointment.")
        parser.add_option("-s", "--starttime", action="store",\
                        type="string", dest="starttime",\
                        help="date/hour of beginning of appointment")
        parser.add_option("-e", "--endtime", action="store",\
                        type="string", dest="endtime",\
                        help="date/hour of ending of appointment.")

        (options,args) = parser.parse_args(args)
        return options, args


class AddAppointmentCommand(BaseCommand, AppointmentParser):
    """ """

    command_name = "add_appointment"

    def __init__(self):
        self.appointment_values = {}
        self.agenda_values = {}

    def run(self, args):
        (options,args) = self.parse_args(args)
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.appointment_values["patient_id"] = patient_id
        self.appointment_values["dentist_id"] = options.dentist_id
        if options.emergency:
            self.appointment_values["emergency"] = options.emergency
        if options.reason:
            self.appointment_values["reason"] = options.reason.decode("utf_8")
        if options.diagnostic:
            self.appointment_values["diagnostic"] =\
            options.diagnostic.decode("utf_8")
        if options.treatment:
            self.appointment_values["treatment"] =\
            options.treatment.decode("utf_8")
        if options.prognostic:
            self.appointment_values["prognostic"] =\
            options.prognostic.decode("utf_8")
        if options.advise:
            self.appointment_values["advise"] = options.advise.decode("utf_8")
        if options.next_appointment:
            self.appointment_values["next_appointment"] =\
            options.next_appointment.decode("utf_8")
        if options.starttime:
            self.agenda_values["starttime"] = options.starttime
        if options.endtime:
            self.agenda_values["endtime"] = options.endtime


        new_appointment = schedule.Appointment(**self.appointment_values)
        meta.session.add(new_appointment)
        meta.session.commit()

        self.agenda_values["appointment_id"] = new_appointment.id
        new_schedule = schedule.Agenda(**self.agenda_values)
        meta.session.add(new_schedule)
        meta.session.commit()

        print(new_appointment.id)


class AddAppointmentMemoCommand(BaseCommand):
    """ """
    
    command_name = "add_appointmentmemo"

    def __init__(self):
        self.values = {}

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--patient", action="store",
                        type="string", dest="patient_id",
                        help="id of the patient, mandatory")
        parser.add_option("-u", "--user", action="store",
                        type="string", dest="dentist_id",
                        help="The user who wrote the memo")
        parser.add_option("--appointment", action="store",
                        type="string", dest="appointment_id",
                        help="id of the appointment, mandatory")
        parser.add_option("-m", "--memo", action="store",
                        type="string", dest="memo",
                        help="Memo/note about patient.")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options,args) = self.parse_args(args)
        
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        self.values["patient_id"] = patient_id
        self.values["dentist_id"] = options.dentist_id
        if options.appointment_id:
            self.values["appointment_id"] = options.appointment_id
        else:
            self.values["appointment_id"] = os.getenv("appointment_id")
        if options.memo:
            self.values["memo"] = options.memo.decode("utf_8")

        new_memo = schedule.AppointmentMemo(**self.values)
        meta.session.add(new_memo)

        meta.session.commit()


class ListAppointmentCommand(BaseCommand):
    """ """

    command_name = "list_appointment"

    def __init__(self):
        self.query = meta.session.query(schedule.Appointment)

    def parse_args(self, args):
        parser = self.get_parser()
        parser.add_option("--patient", action="store", type="string",
                        help="the patient id.",
                        dest="patient_id")

        parser.add_option("-y", "--year", action="store_true", dest="year",
                        help="appointment this year particulary")

        parser.add_option("-m", "--month", action="store_true", dest="month",
                        help="appointment this month")

        parser.add_option("-q", "--quiet", action="store_true",
                        help="tells reason, diagnostic, treatment...",
                        dest="quiet")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")
        query = self.query.filter(schedule.Appointment.patient_id == 
                                  patient_id)

        patient = meta.session.query(administration.Patient).filter(
                  administration.Patient.id == patient_id).one()

        if options.year:
            pass
#            query = query.filter(schedule.Agenda.starttime == options.year)
        if options.month:
            pass
#            query = query.filter(schedule.Agenda.starttime == options.month)

        if not args:
            query = query.all()
        else:
            for keyword in args:
                keyword = '%{}%'.format(keyword)
                query = query.filter(or_(
                        schedule.Appointment.reason.ilike(keyword),
                        schedule.Appointment.diagnostic.ilike(keyword),
                        schedule.Appointment.treatment.ilike(keyword),
                        schedule.Appointment.prognostic.ilike(keyword),
                        schedule.Appointment.advise.ilike(keyword),
                        schedule.Appointment.next_appointment.ilike(keyword)
                                        )
                        ).all()

        
        print(_(u"Seen {} {}".format(patient.lastname, patient.firstname)))
        
        for appointment in query:
            print(_(u"{}\t{}\t{} {} {} {}"\
                    .format(appointment.id, "||", _("from"), 
                            appointment.agenda.starttime, _("to"),
                            appointment.agenda.endtime)))
            if not options.quiet:
                if appointment.emergency:
                    print(_(u"{}".format(_("EMERGENCY"))))
                if appointment.reason:
                    print(_(u"\t{}\t\t{}".format(_("Reason"), 
                    appointment.reason)))
                if appointment.diagnostic:
                    print(_(u"\t{}\t{}".format(
                    _("Diagnostic"), appointment.diagnostic)))
                if appointment.treatment:
                    print(_(u"\t{}\t{}".format(
                    _("Treatment"), appointment.treatment)))
                if appointment.prognostic:
                    print(_(u"\t{}\t{}".format(
                    _("Prognostic"), appointment.prognostic)))
                if appointment.advise:
                    print(_(u"\t{}\t\t{}".format(
                    _("Advise"), appointment.advise)))
                if appointment.next_appointment:
                    print(_(u"\t{}\t{}".format(
                    _("Next date"), 
                    appointment.next_appointment)))
            print("")

class ListAppointmentMemoCommand(BaseCommand):
    """ """

    command_name = "list_appointmentmemo"

    def __init__(self):
        self.query = meta.session.query(schedule.AppointmentMemo)

    def parse_args(self,args):
        parser = self.get_parser()
        parser.add_option("--patient", action="store",\
                        type="string", dest="patient_id",\
                        help="id of the patient")

        (options,args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options,args) = self.parse_args(args)
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        query = self.query.filter(administration.Patient.id == 
                                  patient_id).all()

        for q in query:
            print(q)


class UpdateAppointmentCommand(BaseCommand, AppointmentParser):
    """ """

    command_name = "update_appointment"

    def __init__(self):
        self.query = meta.session.query(schedule.Appointment)
        
    def run(self, args):    
        (options, args) = self.parse_args(args)
        try:    
            patient_id = int(os.getenv("patient_id"))
        except ValueError:
            sys.exit("Enter in the patient file please, to update his\
                      appointment")
        try:
            appointment_id = int(os.getenv("appointment_id"))
        except ValueError:
            sys.exit("Enter in an appointment to update this appointment")

        appointment = self.query.filter(schedule.Appointment.id ==
                                        appointment_id).one()

        if options.emergency:
            appointment.emergency = True
        if options.reason:
            appointment.reason = options.reason.decode("utf_8")
        if options.diagnostic:
            appointment.diagnostic = options.diagnostic.decode("utf_8")
        if options.treatment:
            appointment.treatment = options.treatment.decode("utf_8")
        if options.prognostic:
            appointment.prognostic = options.prognostic.decode("utf_8")
        if options.advise:
            appointment.advice = options.advise.decode("utf_8")
        if options.next_appointment:
            appointment.next_appointment =\
            options.next_appointment.decode("utf_8")
        if options.starttime:
            appointment.agenda.starttime = options.starttime.decode("utf_8")
        if options.endtime:
            appointment.agenda.endtime = options.endtime.decode("utf_8")

        meta.session.commit()
