# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/10/28
# v0.5
# licence BSD
#

from base import BaseCommand
from models import meta, users, administration
import constants

from sqlalchemy import or_

import os
import sys
import datetime

now = datetime.datetime.now()
today = datetime.date.today()

class ListDentalOfficeCommand(BaseCommand):
    """ """
    command_name = "list_dentaloffice"
    def __init__(self):
        self.query = meta.session.query(users.DentalOffice)
    def parse_args(self, args):
        parser = self.get_parser()
        parser.add_option("--id", action="store_true", default=False,
                        help="print only dental office id",
                        dest="dentaloffice_id")
        (options, args) = parser.parse_args(args)
        return options, args
    def run(self, args):
        (options, args) = self.parse_args(args)

        query = self.query
        for keyword in args:
            if keyword == self.command_name:
                continue
            keyword = "%{}%".format(keyword)
            query = query.filter(or_(
                users.DentalOffice.office_name.ilike(keyword),
                users.DentalOffice.owner_lastname.ilike(keyword),
                users.DentalOffice.owner_firstname.ilike(keyword)
                ))
        query = query.all()
        if options.dentaloffice_id:
            for d in query:
                print(d.id)
        else:
            for d in query:
                print("{} {} {} {}".format(d.id, d.office_name.encode("utf_8"),
                                       d.owner_lastname.encode("utf_8"), 
                                       d.owner_firstname.encode("utf_8")))

class ListUserCommand(BaseCommand):
    """ """

    command_name = "list_user"

    def __init__(self):
        self.query = meta.session.query(users.OdontuxUser)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--id", action="store_true", default=False,
                        help="print only user id", 
                        dest="user_id")

        parser.add_option("-r", "--role", action="store", type="string",
               help="Role might be :",
               dest="role")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)

        if not options.role:
            query = self.query
        else:
            for r_id, r_name in constants.ROLES_LIST:
                if options.role == r_name:
                    query = self.query.filter(
                        users.OdontuxUser.role == r_id)
                    break

        for keyword in args:
            if keyword == self.command_name:
                continue
            keyword = "%{}%".format(keyword)
            query = query.filter(or_(
                users.OdontuxUser.lastname.ilike(keyword),
                users.OdontuxUser.firstname.ilike(keyword)
                ))

        query = query.all()
        if options.user_id:
            for u in query:
                print("{}".format(u.id))
#                print(u.id)
        else:
            for u in query:
                print("{} {} {} {}".format(u.id, u.lastname, u.firstname, 
                                           constants.ROLES[u.role]))

class OdontuxUserParser(BaseCommand):
    """ """
    def parse_args(self, args, update=False):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="ID of the user we're gonna uptate",
                            dest="user_id")
                            
        parser.add_option("-u", "--username", action="store", type="string",
                        help="username of the person allowed using software",
                        dest="username")

        parser.add_option("-p", "--password", action="store", type="string",
                        help="Password",
                        dest="password")

        parser.add_option("-r", "--role", action="store", type="string",
                        help="Job of user in the dental office",
                        dest="role")

        parser.add_option("-t", "--title", action="store", type="string",
                        help="Dentist's title",
                         dest="title")

        parser.add_option("-l", "--lastname", action="store", type="string",
                        help="Lastname of the user, mandatory",
                        dest="lastname")

        parser.add_option("-f", "--firstname", action="store", type="string",
                        help="User's firstname",
                        dest="firstname")

        parser.add_option("--qualifications", action="store", type="string",
                        help="Qualification of the patient",
                        dest="qualifications")

        parser.add_option("--registration", action="store", type="string",
                        help="For the role dentist : registration",
                        dest="registration")

        parser.add_option("--correspondence_name", action="store", 
                        type="string", dest="correspondence_name",\
                        help="Correspondance name for patient")

        parser.add_option("-s", "--sex", action="store", type="string",
                        help="1/M for Male, 0/F for Female",
                        dest="sex")

        parser.add_option("-b", "--birthday", action="store", type="string",
                        help="Patient's date of birth",
                        dest="dob")

        parser.add_option("--inactive", action="store_true", dest="inactive",\
                        help="if status of patient is inactive")

        parser.add_option("-c", "--comments", action="store", type="string",
                        help="any comments about this user.",
                        dest="comments")

        parser.add_option("-a", "--avatar_id", action="store", type="string",
                        help="to add an avatar, NOT IMPLEMENTED YET",
                        dest="avatar_id")

        parser.add_option("--display_order", action="store", type="string",
                        help="NOT IMPLEMENTED, openmolar retrocompatibility",
                        dest="display_order")

        parser.add_option("--modified_by", action="store", type="string",
                        help="NOT IMPLEMENTED, openmolar retrocompatibility",
                        dest="modified_by")

        parser.add_option("--time_stamp", action="store", type="string",
                        help="user's file creation, default=now",
                        dest="time_stamp")

        parser.add_option("--phonenum", action="store", type="string",
                        help="user's phone number",
                        dest="phone_num")

        parser.add_option("--phonename", action="store", type="string",
                        help="user's phone number",
                        dest="phone_name")

        parser.add_option("--mail", action="store", type="string",
                        help="user's email",
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
        
        parser.add_option("--gnucash_url", action="store", type="string",
                        help="url for gnucash",
                        dest="gnucash_url")

        (options,args) = parser.parse_args(args)

        return options, args


class AddOdontuxUserCommand(BaseCommand, OdontuxUserParser):
    """ """

    command_name = "add_user"

    def __init__(self):
        self.values = {}

    def run(self, args):
        (options, args) = self.parse_args(args)

        if not options.lastname:
            sys.exit("a lastname is mandatory to add a new user to database")

        self.values["username"] = options.username.decode("utf_8").lower()
        self.values["password"] = options.password.decode("utf_8")
        self.values["role"] = options.role.decode("utf_8")
        self.values["title"] = options.title.decode("utf_8").title()
        self.values["lastname"] = options.lastname.decode("utf_8").upper()
        self.values["firstname"] = options.firstname.decode("utf_8").title()
        if options.qualifications:
            self.values["qualifications"] =\
            options.qualifications.decode("utf_8").title()
        if options.registration:
            self.values["registration"] = options.registration.decode("utf_8")
        if options.correspondence_name:
            self.values["correspondence_name"] = \
            options.correspondence_name.decode("utf_8").upper()
        if options.sex is "1" or options.sex is "M" or options.sex is "m":
            self.values["sex"] = "m"
        else:
            self.values["sex"] = "f"
        if options.dob:
            self.values["dob"] = options.dob
        if options.inactive:
            self.values["status"] = False
        if options.comments:
            self.values["comments"] = options.comments.decode("utf_8")
        if options.avatar_id:
            self.values["avatar_id"] = options.avatar_id
        if options.display_order:
            self.values["display_order"] = options.display_order
        if options.modified_by:
            self.values["modified_by"] = options.modified_by.decode("utf_8")
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp
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

        if int(options.role) == constants.ROLE_DENTIST:
            self.values['gnucash_url'] = options.gnucash_url.decode("utf_8")

        new_user = users.OdontuxUser(**self.values)
        meta.session.add(new_user)
        new_user.addresses.append(administration.Address(
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
                options.phone_name = "defaut"
            new_user.phones.append(administration.Phone(
                            name = options.phone_name.decode("utf_8"),
                            number = options.phone_num.decode("utf_8")
                            ))
        if options.email:
            new_user.mails.append(administration.Mail(
                            email = options.email
                            ))

        meta.session.commit()

class UpdateUserCommand(BaseCommand, OdontuxUserParser):
    """ To change password or others stuff that are not address/phone related
    """

    command_name = "update_user"

    def __init__(self):
        self.query = meta.session.query(users.OdontuxUser)

    def run(self, args):
        (options, args) = self.parse_args(args, True)
        if not options.user_id:
            print(_("the user's id must be provide to update odontux user"))
            sys.exit(1)
        user = self.query.filter(users.OdontuxUser.id ==
                                 options.user_id).one()

        if options.username:
            user.username = options.username.decode("utf_8").lower()
        if options.password:
            user.password = options.password.decode("utf_8")
        if options.role:
            user.role = options.role.decode("utf_8")
        if options.title:
            user.role = options.title.decode("utf_8").title()
        if options.lastname:
            user.lastname = options.lastname.decode("utf_8").upper()
        if options.firstname:
            user.firstname = options.firstname.decode("utf_8").title()
        if options.qualifications:
            user.qualifications = options.qualifications.decode("utf_8")
        if options.registration:
            user.registration = options.registration.decode("utf_8")
        if options.correspondence_name:
            user.correspondence_name = \
            options.correspondence_name.decode("utf_8")
        if options.inactive:
            user.status = False
        if options.sex:
            user.sex = options.sex
        if options.dob:
            user.dob = options.dob
        if options.comments:
            user.comments = options.comments.decode("utf_8")
        if options.avatar_id:
            user.avatar_id = options.avatar_id
        if options.display_order:
            user.display_order = options.display_order
        if options.time_stamp:
            user.time_stamp = options.time_stamp
        else:
            user.time_stamp = today

        if user.role == constants.ROLE_DENTIST:
            if options.gnucash_url:
                user.gnucash_url = options.gnucash_url

        meta.session.commit()      

class UserMovingInCommand(BaseCommand):
    """
    When the user moves (used mainly for dentists who make replacements...
    """

    command_name = "user_movingin"

    def __init__(self):
        pass

    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("--user_id", action="store", type="string",
                        help="Id of user we want to change/update address",
                        dest="odontuxuser_id")
        
        parser.add_option("--address_id", action="store", type="string",
                        help="id of address to update",
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
        
        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)

        if options.odontuxuser_id:
            odontuxuser = meta.session.query(users.OdontuxUser)\
                          .filter(users.OdontuxUser.id ==
                          options.odontuxuser_id).one()
        else:
            username = os.getenv("USER")
            odontuxuser = meta.session.query(users.OdontuxUser)\
                             .filter(users.OdontuxUser.username ==
                             username).one()

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

        if options.address_id:
            options.address_id = int(options.address_id)
            for addr in odontuxuser.addresses:
                if addr.id == options.address_id:
                    if options.street:
                        addr.street = options.street
                    if options.building:
                        addr.building = options.building
                    if options.postal_code:
                        addr.postal_code = options.postal_code
                    if options.city:
                        addr.city = options.city
                    if options.county:
                        addr.county = options.county
                    if options.country:
                        addr.country = options.country
                    meta.session.commit()
        else:
            odontuxuser.addresses.append(administration.Address(
                                            street = options.street,
                                            building = options.building,
                                            city = options.city,
                                            postal_code = options.postal_code,
                                            county = options.county,
                                            country = options.country,
                                            update_date = options.update_date
                                            ))
            meta.session.commit()


class DentalOfficeParser(BaseCommand):  
    """ """

    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("-e", "--enterprise", action="store", type="string",
                        help="Name of the enterprise",
                        dest="office_name")

        parser.add_option("-l", "--lastname", action="store", type="string",
                        help="Lastname of the dentist to add, mandatory",
                        dest="lastname")

        parser.add_option("-f", "--firstname", action="store", type="string",
                        help="Firstname of dentist.",
                        dest="firstname")

        parser.add_option("--phonename", action="store", type="string",
                        help="Phone of the dentist.",
                        dest="phone_name")

        parser.add_option("--phonenum", action="store", type="string",
                        help="Phone of the dentist.",
                        dest="phone_num")

        parser.add_option("-m", "--mail", action="store", type="string",
                        help="Email address of the dentist.",
                        dest="email")

        parser.add_option("--url", action="store", type="string",
                        help="URL of the dental office",
                        dest="url")

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

class AddDentalOfficeCommand(BaseCommand, DentalOfficeParser):
    """ """
    
    command_name = "add_dentaloffice"

    def __init__(self):
        self.values = {}

    def run(self, args):
        
        (options, args) = self.parse_args(args)

        if not options.lastname:
            sys.exit("a lastname must be provide to add a new medecine doctor")

        self.values["owner_lastname"] =\
        options.lastname.decode("utf_8").upper()
        if options.office_name:
            self.values["office_name"] =\
            options.office_name.decode("utf_8").title()
        if options.firstname:
            self.values["owner_firstname"] =\
            options.firstname.decode("utf_8").title()
        if options.url:
            self.values['url'] = options.url.decode("utf_8")
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

        new_dental_office = users.DentalOffice(**self.values)
        meta.session.add(new_dental_office)
        new_dental_office.addresses.append(administration.Address(
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
                options.phone_name = "defaut"
            new_dental_office.phones.append(administration.Phone(
                            name = options.phone_name.decode("utf_8"),
                            number = options.phone_num.decode("utf_8")
                            ))
        if options.email:
            new_dental_office.mails.append(administration.Mail(
                            email = options.email
                            ))

        meta.session.commit()
        
