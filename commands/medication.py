# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from model import meta, medication
from base import BaseCommand

from gettext import gettext as _
from sqlalchemy import or_

import os
import sys
import code


class DrugPrescribedParser(BaseCommand):
    """ """
    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("-a", "--alias", action="store",\
                        type="string", dest="alias",\
                        help="alias for the drug prescribed.")
        parser.add_option("-m", "--molecule", action="store",\
                        type="string", dest="molecule",\
                        help="The drug or molecule name.")
        parser.add_option("--packaging", action="store",\
                        type="string", dest="packaging",\
                        help="how the drug looks and number in the box.")
        parser.add_option("-p", "--posologia", action="store",\
                        type="string", dest="posologia",\
                        help="Quantity and period of day the drug is taken.")
        parser.add_option("-d", "--dayssupply", action="store",\
                        type="string", dest="dayssupply",\
                        help="how long the drug is taken")
        parser.add_option("-c", "--comments", action="store",\
                        type="string", dest="comments",\
                        help="comments on how to take the drug")

        (options,args) = parser.parse_args(args)
        return options, args


class PrescriptionParser(BaseCommand):
    """ """
    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("-u", "--user", action="store", type="string",
                        help="dentist who's making the prescription",
                        dest="dentist_id")

        parser.add_option("--patient", action="store", type="string",
                        help="patient for whom the prescription is",
                        dest="patient_id")

        parser.add_option("--appointment", action="store", type="string",
                        help="the appointment where the prescription was made",
                        dest="appointment_id")

        parser.add_option("--date", "--timestamp", action="store",
                        type="string", dest="time_stamp",
                        help="when the prescription was made")

        (options,args) = parser.parse_args(args)
        return options, args


class AddDrugPrescribedCommand(BaseCommand, DrugPrescribedParser):
    """ """
    
    command_name = "add_drug"
    
    def __init__(self):
        self.values = {}

    def run(self, args):

        (options,args) = self.parse_args(args)

        if not options.alias:
            sys.exit("the alias is needed to add a drug, please")

        self.values["alias"] = options.alias.decode("utf_8")
        self.values["molecule"] = options.molecule.decode("utf_8")
        if options.packaging:
            self.values["packaging"] = options.packaging.decode("utf_8")
        if options.posologia:
            self.values["posologia"] = options.posologia.decode("utf_8")
        if options.dayssupply:
            self.values["dayssupply"] = options.dayssupply.decode("utf_8")
        if options.comments:
            self.values["comments"] = options.comments.decode("utf_8")

        new_drug = medication.DrugPrescribed(**self.values)
        meta.session.add(new_drug)

        meta.session.commit()

class MakePrescriptionCommand(BaseCommand, PrescriptionParser):
    """ """

    command_name = "make_prescription"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options,args) = self.parse_args(args)

        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")
        self.values["dentist_id"] = options.dentist_id
        self.values["patient_id"] = patient_id
        if options.appointment_id:
            self.values["appointment_id"] = options.appointment_id
        else:
            self.values["appointment_id"] = os.getenv("appointment_id")
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp

        new_prescription = medication.Prescription(**self.values)
        meta.session.add(new_prescription)
        meta.session.commit()

        def askuser(message):
            userinteract = code.InteractiveConsole()
            response = userinteract.raw_input(message)
            return response

        n = 0
        while n == 0:
            message = _("keyword for type of drug you want to prescribed\t")
            keyword = askuser(message)
            keyword = '%{}%'.format(keyword)

            query = (
                meta.session.query(medication.DrugPrescribed)
                    .filter(
                        or_(
                            medication.DrugPrescribed.alias.ilike(keyword),
                            medication.DrugPrescribed.molecule.ilike(keyword)
                        )
                    )
            )

            for drug in query:
                print(_(u"{}. {} {} {} {} {} {}".format(drug.id, drug.alias,
                        drug.molecule, drug.packaging, drug.posologia, 
                        drug.dayssupply, drug.comments)))

            response = askuser(_("Choose a drug to add in the list\t"))
            self.values = {}
            self.values["drug_id"] = response
            self.values["prescription_id"] = new_prescription.id
            newdrugref = medication.PrescribedDrugReference(**self.values)
            meta.session.add(newdrugref)
            response = askuser(_("add another drug ? (Y/n)\t"))
            if response == _("n") or response == _("N"):
                n = 1

        meta.session.commit()


class ListDrugCommand(BaseCommand):
    """
    ./list_drug.py keyword1 keyword2
    will search for drug which alias or molecule contains keyword
    """

    command_name = "list_drug"

    def __init__(self):
        self.query = meta.session.query(medication.DrugPrescribed)

    def run(self, args):
        if not args:
            query = self.query
        else:
            for keyword in args:
                keyword = '%{}%'.format(keyword)
                query = self.query.filter(or_(
                            medication.DrugPrescribed.alias.ilike(keyword),\
                            medication.DrugPrescribed.molecule.ilike(keyword)))

        for drug in query:
            print(_(u"{}. {}, {} {} {} {} {}"\
                .format(drug.id, drug.alias, drug.molecule, drug.packaging,\
                drug.posologia, drug.dayssupply, drug.comments)))

