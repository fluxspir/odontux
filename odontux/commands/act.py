# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from models import meta, act, administration, schedule, cotation, teeth
from base import BaseCommand
import constants

from sqlalchemy import or_
from gettext import gettext as _
from decimal import Decimal
import sqlalchemy
import datetime
import os
import sys

import gnucash_handler

today = datetime.date.today()


locale = "fr"
socialsecuritylocale = "SocialSecurity" + locale.title()
SocialSecurityLocale = getattr(administration, socialsecuritylocale)


class ActTypeParser(BaseCommand):
    """ """
    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("-s", "--specialty", action="store", type="string",
                        help="id of the specialty for this kind of act",
                        dest="specialty_id")

        parser.add_option("-n", "--name", action="store", type="string",
                        help="name describing exactly the act",
                        dest="name")

        parser.add_option("-a", "--alias", action="store", type="string",
                        help="alias for the act",
                        dest="alias")

        parser.add_option("-c", "--code", action="store", type="string",
                        help="code user may tell to simplify",
                        dest="code")

        parser.add_option("-k", "--cotation", action="store", type="string",
                        help="id of the cotation for this act",
                        dest="cotationfr_id")

        parser.add_option("--color", action="store", type="string",
                        help="color for this act",
                        dest="color")


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
    """ An ActType is an act made by the dentist
    This act has a scientific / administrative name (or description)
    The act also has an alias : a sort name use in everyday life
    The act has a code, without whitespaces, to enter it quicker
    The "cotation" is the code the social security will give it, and the 
    cotation may change whether the act is on adult, child...
    The color is for gui purpose.
    
    """

    command_name = "add_acttype"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)
        
        self.values["name"] = options.name
        if options.specialty_id:
            self.values["specialty_id"] = options.specialty_id
        if options.alias:
            self.values["alias"] = options.alias.decode("utf_8")
        else:
            self.values["alias"] = options.name.decode("utf_8")
        if options.code:
            self.values["code"] = options.code.decode("utf_8")
        if options.cotationfr_id:
            self.values["cotationfr_id"] =\
            options.cotationfr_id.decode("utf_8")
        if options.color:
            self.values["color"] = options.color.decode("utf_8")

        new_acttype = act.ActType(**self.values)
        meta.session.add(new_acttype)
        meta.session.commit()


class AddAdministrativeActCommand(BaseCommand, AppointmentActReferenceParser):
    """ The Administrative Act
    
    An administrative act is recorded as it was made while an Appointment 
    (linking it this way to a patient, a dentist, a dental office, and a 
    datetime).
    Each act will get his own administrativeact instance, that will stock :
        * the act
        * the appointment
        * the social_security code for this act
        *the actual price of this act
    If GnuCash is enabled, it will also make the Invoice.
    
    """

    command_name = "add_administrativeact"

    def __init__(self):
        self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        # define precisely when the act was done
        if options.appointment_id:
            appointment_id = options.appointment_id
        else:
            appointment_id = os.getenv("appointment_id")

        # add possible majoration for night, holidays(...)
        if options.majoration_id:
            majoration = meta.session.query(cotation.MajorationFr)\
                .filter(cotation.MajorationFr.id == 
                        options.majoration_id).one()
            majoration = majoration.price
        else:
            majoration = 0

        if not options.act_id:
            sys.exit(_("Please enter the act id with option -a"))

        # get type_id, the one who correspond to what dentist done.
        actual_act = meta.session.query(act.ActType)\
                .filter(act.ActType.id == options.act_id).one()
        # get the data to "create" the price for the act done.
        execution = meta.session.query(cotation.CotationFr)\
                .filter(cotation.CotationFr.id == 
                        actual_act.cotationfr_id).one()
        # tell in which appointment, to whom, the act was made.
        appointment = meta.session.query(schedule.Appointment)\
                .filter(schedule.Appointment.id == appointment_id).one()
        patient_id = appointment.patient.id
        patient = meta.session.query(administration.Patient)\
                .filter(administration.Patient.id == patient_id).one()
        # When the patient is under 13, the cotation for the act may change.
        # as well as the price ; 
        # We'll adapt the price later for CMU's, if needed.
        if patient.age() < constants.KID_AGE:
            multiplicator = execution.kid_multiplicator
            exceeding = execution.exceeding_kid_normal
        else:
            multiplicator = execution.adult_multiplicator
            exceeding = execution.exceeding_adult_normal

        # For some acts, people getting CMU have another prices.
        patient_right = meta.session.query(SocialSecurityLocale)\
                        .filter(SocialSecurityLocale.id ==
                                patient.socialsecurity_id).one()

        key = meta.session.query(cotation.NgapKeyFr)\
                .filter(cotation.NgapKeyFr.id == execution.key_id).one()

        # In the appointment-acttype table, we'll store :
        # The appointment
        self.values["appointment_id"] = appointment_id
        # The optional tooth where the act was made
        if options.tooth_id:
            self.values["tooth_id"] = options.tooth_id
        # The act that was made
        self.values["act_id"] = options.act_id

        # The code for this act
        if patient_right.cmu:
            if execution.key_cmu_id:
                cmu_key = meta.session.query(cotation.CmuKeyFr)\
                           .filter(cotation.CmuKeyFr.id ==
                                   execution.key_cmu_id).one().key
                self.values["code"] = cmu_key + str(execution.adult_cmu_num)
                exceeding = execution.exceeding_adult_cmu
                if patient.age() < constants.KID_AGE:
                    exceeding = execution.exceeding_kid_cmu
            else:
                self.values["code"] = key.key + str(multiplicator)
        else:
            self.values["code"] = key.key + str(multiplicator)

        # The price of this act
        self.values["price"] = execution.get_price(multiplicator, 
                               exceeding, majoration)

        new_act = act.AppointmentActReference(**self.values)
        meta.session.add(new_act)
        meta.session.commit()

        invoice = gnucash_handler.GnuCashInvoice(patient_id, appointment_id)
        invoice_id = invoice.add_act(self.values["code"], 
                                         self.values["price"])
        new_act.invoice_id = invoice_id
        meta.session.commit()
        print(new_act.id)

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
            print(_(u"{}.\t{}\t {} || {}"\
                .format(acte.id, acte.code, acte.alias, acte.name)\
                .encode("utf_8")))


class ListPatientActCommand(BaseCommand, AppointmentActReferenceParser):
    """ """

    command_name = "list_patientact"

    def __init__(self):
        self.query = meta.session.query(act.AppointmentActReference)
        self.appointment = meta.session.query(schedule.Appointment)
        self.act = meta.session.query(act.ActType)
        self.tooth = meta.session.query(teeth.Tooth)
        self.toothevent = meta.session.query(teeth.ToothEvent)
        self.crownevent = meta.session.query(teeth.CrownEvent)
        self.rootevent = meta.session.query(teeth.RootEvent)

    def run(self, args):
        """ """
        patient_id = os.getenv("patient_id")

        appointments = self.appointment\
                       .filter(schedule.Appointment.patient_id == patient_id)
        for appointment in appointments:
            acts = self.query.filter(act.AppointmentActReference.appointment_id
                  == appointment.id)
            for a in acts:
                try:
                    tooth = self.tooth.filter(teeth.Tooth.id == 
                                              a.tooth_id).one()
                except sqlalchemy.orm.exc.NoResultFound:
                    tooth = ""

                event = self.act.filter(act.ActType.id == a.act_id).one()

                if tooth:
                    print(_(u"{}.\t{}\t|| {}\t: {}\t\t{}"\
                        .format(a.id, tooth.name, a.code, a.price,
                        event.alias)))
                else:
                    print(_(u"{}.\t{}\t|| {}\t: {}\t\t{}"\
                        .format(a.id, _(" "), a.code, a.price, event.alias)))
