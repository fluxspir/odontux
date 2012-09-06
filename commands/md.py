# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD
#

from base import BaseCommand
from model import md, meta
from sqlalchemy import or_
import sys

class MedecineDoctorParser(BaseCommand):
    """ """
    def parse_args(self, args, update=False):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="the md id",
                            dest="md_id")

        parser.add_option("-l", "--lastname", action="store", type="string",
                          help="Lastname of the generalist doctor to add,"
                                                                " mandatory",
                          dest="lastname")

        parser.add_option("-f", "--firstname", action="store", type="string",
                          help="Firstname of generalist doctor.",
                          dest="firstname")

        parser.add_option("-c", "--city", action="store", type="string",
                          help="City where the generalist doctor works.",
                          dest="city")

        parser.add_option("-a", "--address", action="store", type="string",
                          help="Address of the generalist doctor office.",
                          dest="address")

        parser.add_option("-p", "--phone", action="store", type="string",
                          dest="phone", help="Phone of the generalist doctor.")

        parser.add_option("-m", "--mail", action="store", type="string",
                          help="Email address of the generalist doctor.",
                          dest="mail")

        (options,args) = parser.parse_args(args)

        return options, args


class AddMedecineDoctorCommand(BaseCommand, MedecineDoctorParser):
    """ """

    command_name = "add_md"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        if not options.lastname:
            sys.exit("a lastname must be provide to add "
                     "a new medecine doctor, please")

        self.values["lastname"] = options.lastname.decode("utf_8").upper()
        if options.firstname:
            self.values["firstname"] = options.firstname.decode("utf8").title()
        if options.city:
            self.values["city"] = options.city.decode("utf_8").title()
        if options.address:
            self.values["address"] = options.address.decode("utf_8").title()
        if options.phone:
            self.values["phone"] = options.phone.decode("utf_8")
        if options.mail:
            self.values["mail"] = options.mail.decode("utf_8").lower()

        new_generalist = MedecineDoctor(**self.values)

        meta.session.add(new_generalist)

        meta.session.commit()


class ListMedecineDoctorCommand(BaseCommand):
    """ """

    command_name = "list_md"

    def __init__(self):
        self.query = meta.session.query(MedecineDoctor)

    def parse_args(self, args):
        parser = self.get_parser()
    
        parser.add_option("-i", "--id", action="store_true", dest="md_id",
                        help="use this option if you want to get only the id")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)
        query = self.query
        if args:
            for keyword in args:
                keyword = '%{}%'.format(keyword)
                query = query.filter(or_(
                                MedecineDoctor.lastname.ilike(keyword),
                                MedecineDoctor.firstname.ilike(keyword),
                                MedecineDoctor.city.ilike(keyword)))

        if options.md_id:
            query = query.one()
            print(u"{}".format(query.id))
        else:
            for doc in query:
                print(u"{}. {} {},\t{}".format(doc.id, doc.lastname,
                                           doc.firstname, doc.city))


class UpdateMedecineDoctorCommand(BaseCommand, MedecineDoctorParser):
    """ """

    command_name = "update_md"

    def __init__(self):
        self.query = meta.session.query(MedecineDoctor)

    def run(self, args):
        (options, args) = self.parse_args(args, True)

        if not options.md_id:
            sys.exit("the id of md must be provide to update md")

        doc = self.query.filter(MedecineDoctor.id ==
                                options.md_id).one()

        if options.lastname:
            doc.lastname = options.lastname.decode("utf_8").upper()
        if options.firstname:
            doc.firstname = options.firstname.decode("utf8").title()
        if options.city:
            doc.city = options.city.decode("utf_8").title()
        if options.address:
            doc.address = options.address.decode("utf_8").title()
        if options.phone:
            doc.phone = options.phone.decode("utf_8")
        if options.mail:
            doc.mail = options.mail.decode("utf_8").lower()

        meta.session.commit()



