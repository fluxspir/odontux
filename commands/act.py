# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from model import meta, act, administration, schedule, cotation
from base import BaseCommand

from sqlalchemy import or_
from gettext import gettext as _
import os
import sys


class ActTypeParser(BaseCommand):
    """ """
    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store",\
                        type="string", dest="specialty_id",\
                        help="id of the specialty for this kind of act")
        parser.add_option("-n", "--name", action="store",\
                        type="string", dest="name",\
                        help="name describing exactly the act")
        parser.add_option("-a", "--alias", action="store",\
                        type="string", dest="alias",\
                        help="alias for the act")
        parser.add_option("-k", "--cotation", action="store",\
                        type="string", dest="cotationfr_id",\
                        help="id of the cotation for this act")
        parser.add_option("-c", "--color", action="store",\
                        type="string", dest="color",\
                        help="color for this act")

        (options, args) = parser.parse_args(args)

        return options, args


class AppointmentActReferenceParser(BaseCommand):
    """ """
    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("--appointment", action="store", type="string",
                        help="Appointment while happened the act.",
                        dest="appointment_id")

        parser.add_option("-a", "--act", action="store", type="string",
                        help="Cotation of the act done",
                        dest="act_id")

        parser.add_option("-m", "--majoration", action="store", type="string",
                        help="majoration we have to add to the total price",
                        dest="majoration_id")

        parser.add_option("-t", "--tooth", action="store", type="string",
                        help="tooth we are working on",
                        dest="tooth_id")

        (options, args) = parser.parse_args(args)
        return options, args


class AddActTypeCommand(BaseCommand, ActTypeParser):
    """ """

    command_name = "add_acttype"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        self.values["specialty_id"] = options.specialty_id
        self.values["name"] = options.name
        if options.alias:
            self.values["alias"] = options.alias.decode("utf_8")
        else:
            self.values["alias"] = options.name.decode("utf_8")
        if options.cotationfr_id:
            self.values["cotationfr_id"] = options.cotationfr_id.decode("utf_8")
        if options.color:
            self.values["color"] = options.color.decode("utf_8")

        new_acttype = act.ActType(**self.values)
        meta.session.add(new_acttype)
        meta.session.commit()


class AddAdministrativeActCommand(BaseCommand, AppointmentActReferenceParser):
    """ """

    command_name = "add_administrativeact"

    def __init__(self):
            self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        if options.appointment_id:
            appointment_id = options.appointment_id
        else:
            appointment_id = os.getenv("appointment_id")

        if options.majoration_id:
            majoration = meta.session.query(cotation.MajorationFr)\
                .filter(cotation.MajorationFr.id == 
                        options.majoration_id).one()
            majoration = majoration.price
        else:
            majoration = 0

        if not options.act_id:
            sys.exit(_("Please enter the act id with option -a"))
        actual_act = meta.session.query(act.ActType)\
                .filter(act.ActType.id == options.act_id).one()
        execution = meta.session.query(cotation.CotationFr)\
                .filter(cotation.CotationFr.id == 
                        actual_act.cotationfr_id).one()

        appointment = meta.session.query(schedule.Appointment)\
                .filter(schedule.Appointment.id == appointment_id).one()
        patient_id = appointment.patient.id
        patient = meta.session.query(administration.Patient)\
                .filter(administration.Patient.id == patient_id).one()
        if patient.age() < 13:
            multiplicator = execution.kid_multiplicator
            exceeding = execution.exceeding_kid_normal
        else:
            multiplicator = execution.adult_multiplicator
            exceeding = execution.exceeding_adult_normal

        key = meta.session.query(cotation.NgapKeyFr)\
                .filter(cotation.NgapKeyFr.id == execution.key_id).one()

        self.values["appointment_id"] = appointment_id
        if options.tooth_id:
            self.values["tooth_id"] = options.tooth_id
        self.values["act_id"] = options.act_id
        self.values["code"] = key.key + str(multiplicator)
        self.values["price"] = execution.get_price(multiplicator, exceeding, 
                                                   majoration)

        new_act = act.AppointmentActReference(**self.values)
        meta.session.add(new_act)
        meta.session.commit()


class ListActTypeCommand(BaseCommand):
    """ """

    command_name = "list_acttype"

    def __init__(self):
        self.query = meta.session.query(act.ActType)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store",\
                        type="string", dest="specialty_id",\
                        help="Specialty of the act we're looking for")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        if options.specialty_id:
            query = self.query.filter(act.ActType.specialty_id == 
                                      options.specialty_id)
        else:
            query = self.query

        if not args:
            query = query.all()
        else:
            for keyword in args:
                keyword = "%{}%".format(keyword)
                query = query.filter(or_(
                            act.ActType.name.ilike(keyword),
                            act.ActType.alias.ilike(keyword)
                            )
                        )
                            
        for acte in query:
            print(_(u"{}. {} || {}"\
                .format(acte.id, acte.alias, acte.name).encode("utf_8")))
