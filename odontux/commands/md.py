# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/25
# v0.4
# Licence BSD
#

from base import BaseCommand
from models import md, meta, administration

import sqlalchemy
from sqlalchemy import or_, and_
from gettext import gettext as _
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

        parser.add_option("--phonename", action="store", type="string",
                           help="Phone of the generalist doctor.",
                           dest="phone_name")

        parser.add_option("--phonenum", action="store", type="string",
                           help="Phone of the generalist doctor.",
                           dest="phone_num")

        parser.add_option("-m", "--mail", action="store", type="string",
                          help="Email address of the generalist doctor.",
                          dest="email")

        parser.add_option("--address_id", action="store", type="string",
                        help="address id in DB from the person",
                        dest="address_id")

        parser.add_option("--street", action="store", type="string",
                        help="street and number",
                        dest="street")
    
        parser.add_option("--building", action="store", type="string",
                        help="building, stair... any complement for address",
                        dest="building")

        parser.add_option("--city", action="store", type="string",
                        help="name of the city",
                        dest="city")

        parser.add_option("--postal_code", action="store", type="string",
                        help="postal code of the city",
                        dest="postal_code")

        parser.add_option("--county", action="store", type="string",
                        help="county's name",
                        dest="county")

        parser.add_option("--country", action="store", type="string",
                        help="country",
                        dest="country")

        parser.add_option("--update_date", action="store", type="string",
                        help="date since when the person lives here",
                        dest="update_date")


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
            print(_("a lastname must be provide to add "
                     "a new medecine doctor, please"))
            sys.exit(1)

        self.values["lastname"] = options.lastname.decode("utf_8").upper()
        if options.firstname:
            self.values["firstname"] = options.firstname.decode("utf8").title()
        if options.street:
            options.street = options.street.decode("utf_8")
        if options.building:
            options.building = options.building.decode("utf_8")
        if options.postal_code:
            options.postal_code = options.postal_code.decode("utf_8")
        if options.city:
            options.city = options.city.decode("utf_8").title()
        if options.county:
            options.county = options.county.decode("utf_8").title()
        if options.country:
            options.country = options.country.decode("utf_8").title()
        if options.email:
            options.email = options.email.decode("utf_8").lower()

        try:
            old_md = meta.session.query(md.MedecineDoctor).filter(and_(
                    md.MedecineDoctor.lastname == options.lastname,
                    md.MedecineDoctor.firstname == options.firstname
                    )).one()
        except sqlalchemy.orm.exc.NoResultFound:
            old_md = ""

        if not old_md:
            new_medecine_doctor = md.MedecineDoctor(**self.values)
            meta.session.add(new_medecine_doctor)
            
            new_medecine_doctor.addresses.append(administration.Address(
                            street = options.street,
                            building = options.building,
                            city = options.city,
                            postal_code = options.postal_code,
                            county = options.county,
                            country = options.country,
                            update_date = options.update_date
                            ))
            if options.phone_num:
                if not options.phone_name:
                    options.phone_name = _("defaut")
                new_medecine_doctor.phones.append(administration.Phone(
                                name = options.phone_name.decode("utf_8"),
                                number = options.phone_num.decode("utf_8")
                                ))
            if options.email:
                new_medecine_doctor.mails.append(administration.Mail(
                                email = options.email
                                ))

            meta.session.commit()

class ListMedecineDoctorCommand(BaseCommand):
    """ """

    command_name = "list_md"

    def __init__(self):
        self.query = meta.session.query(md.MedecineDoctor)

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
                                md.MedecineDoctor.lastname.ilike(keyword),
                                md.MedecineDoctor.firstname.ilike(keyword)
                                )
                       )

        if options.md_id:
            try:
                query = query.one()
            #TODO change this horrible except hack :(
            except sqlalchemy.orm.exc.MultipleResultsFound:
                query = query.first()
            print(u"{}".format(query.id))
        else:
            for doc in query:
                print(u"{}. {} {},\t{}".format(doc.id, doc.lastname,
                                           doc.firstname, _("Todo : city")))


class UpdateMedecineDoctorCommand(BaseCommand, MedecineDoctorParser):
    """ """

    command_name = "update_md"

    def __init__(self):
        self.query = meta.session.query(md.MedecineDoctor)

    def run(self, args):
        (options, args) = self.parse_args(args, True)

        if not options.md_id:
            sys.exit("the id of md must be provide to update md")

        doc = self.query.filter(md.MedecineDoctor.id ==
                                options.md_id).one()

        if options.lastname:
            doc.lastname = options.lastname.decode("utf_8").upper()
        if options.firstname:
            doc.firstname = options.firstname.decode("utf8").title()
        if options.street:
            doc.addresses[-1].street = options.street.decode("utf_8").title()
        if options.building:
            doc.addresses[-1].building = options.building.decode("utf_8").title()
        if options.city:
            doc.addresses[-1].city = options.city.decode("utf_8").title()
        if options.postal_code:
            doc.addresses[-1].postal_code = options.postal_code.decode("utf_8").title()
        if options.county:
            doc.addresses[-1].county = options.county.decode("utf_8").title()
        if options.country:
            doc.addresses[-1].country = options.country.decode("utf_8").title()
        if options.phone:
            doc.phone = options.phone.decode("utf_8")
        if options.mail:
            doc.mail = options.mail.decode("utf_8").lower()

        meta.session.commit()

