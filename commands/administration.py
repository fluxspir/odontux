# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# licence BSD
#

from model import meta, administration, cotation, md, teeth
from base import BaseCommand, GnuCash

import ConfigParser
import os
from sqlalchemy import or_
from gettext import gettext as _
import sys

try:
    import gnucash
    from gnucash import Session as GCSession
    from gnucash.gnucash_business import Customer, Address
    GNUCASH_ACCOUNT = True
except ImportError:
    GNUCASH_ACCOUNT = False


locale = "fr"
socialsecuritylocale = "SocialSecurity" + locale.title()
SocialSecurityLocale = getattr(administration, socialsecuritylocale)


class GnuCashCustomer(GnuCash):
    """
    This class is meant to manage "Customers" informations in gnucash.
    """

    def _test_id_already_in_database(self):
        return self.book.CustomerLookupByID(self.gcpatient_id)

    def _set_name(self):
        """return customer instance, and his name"""
        # patient_name :  M. LASTNAME Firstname
        name = self.patient.title + " " + self.patient.lastname + " " \
               + self.patient.firstname
        new_customer = Customer(self.book, self.gcpatient_id, self.currency, 
                                name.encode("utf_8"))
        self.gcsession.save()
        return new_customer, name

    def _update_name(self):
        """return customer instance, and his name"""
        name = self.patient.title + " " + self.patient.lastname + " " \
               + self.patient.firstname
        customer = self.book.CustomerLookupByID(self.gcpatient_id)
        customer.SetName(name.encode("utf_8"))
        self.gcsession.save()
        return customer, name

    def _set_address(self, customer, patientname):
        """ needs a customer_instance 
        This address, in gnucash, is asked for billing purpose
        We'll keep the patient's name as the customer ;
        the billing's name will be wether patient's name if he's alone
        in the family, and the " Family patient.lastname " if there
        is several patients / payers in this family
        """
        # Get the payers' names
        payername = ""
        payerlist = []
        for payer in self.patient.family.payers:
            # The patient is noted as a payer
            if payer.patient_id == self.patient_id:
                # The patient pays for himself
                payername = patientname
                break
            else:
                payerlist.append(payer.patient_id)

        if not payername:
            # Case the patient ain't recorded as a payer
            if not payerlist:
                # Curious case where nobody recorded as a payer for this family
                # The patient will finally be the payer for gnucash.Customer
                payername = patientname
            else:
                for patient_id in payerlist:
                    payer = meta.session.query(administration.Patient)\
                            .filter(administration.Patient.id == patient_id)
                    payer = payer.one()
                    payer = payer.title + " " + payer.lastname + " " +\
                            payer.firstname
                    payername.join(", ", payer)

        address = customer.GetAddr()
        address.SetName(payername.encode("utf_8"))
        if self.patient.family.addresses[-1].street:
            address.SetAddr1(self.patient.family.addresses[-1]
                             .street.encode("utf_8"))
        if self.patient.family.addresses[-1].building:
            address.SetAddr2(self.patient.family.addresses[-1]
                             .building.encode("utf_8"))
        postal_code = ""
        city = ""
        if self.patient.family.addresses[-1].postal_code:
            postal_code = self.patient.family.addresses[-1]\
                          .postal_code.encode("utf_8")
        if self.patient.family.addresses[-1].city:
            city = self.patient.family.addresses[-1].city.encode("utf_8")
        address.SetAddr3(postal_code  + " " + city)
        county = ""
        country = ""
        if self.patient.family.addresses[-1].county:
            county = self.patient.family.addresses[-1].county.encode("utf_8")
        if self.patient.family.addresses[-1].country:
            country = self.patient.family.addresses[-1].country.encode("utf_8")
        address.SetAddr4(county + " " + country)

        self.gcsession.save()
        self.gcsession.end()

    def add_customer(self):
        if self._test_id_already_in_database():
            self.update_customer()
            return True
        (new_customer, name) = self._set_name()
        self._set_address(new_customer, name)
        return True

    def update_customer(self):
        if not self._test_id_already_in_database():
            self.self.add_customer()
            return True
        (customer, name) = self._update_name()
        self._set_address(customer, name)
        return True

class PatientParser(BaseCommand):
    """ """
    def parse_args(self, args, update=False):
        parser = self.get_parser()

        if update:
            parser.add_option("--id", action="store", type="string",
                            help="patient id of the file we want to update",
                            dest="patient_id")

        parser.add_option("-t", "--title", action="store", type="string",
                        help="Patient's title",
                        dest="title")

        parser.add_option("-l", "--lastname", action="store", type="string",
                        help="Lastname of the patient, mandatory",
                        dest="lastname")

        parser.add_option("-f", "--firstname", action="store", type="string",
                        help="Patient's firstname",
                        dest="firstname")

        parser.add_option("--qualification", action="store", type="string",
                        help="Qualification of the patient",
                        dest="qualification")

        parser.add_option("--preferred_name", action="store", type="string",
                        help="Patient's preferred name",
                        dest="preferred_name")

        parser.add_option("--correspondence_name", action="store", 
                        type="string", dest="correspondence_name",
                        help="Correspondance name for patient")

        parser.add_option("-s", "--sex", action="store", type="string",
                        help="1/M for Male, 0/F for Female",
                        dest="sex")

        parser.add_option("-b", "--birthday", action="store", type="string",
                        help="User's date of birth",
                        dest="dob")

        parser.add_option("-j", "--job", action="store", type="string",
                        help="patient's job",
                        dest="job")

        parser.add_option("--inactive", action="store_true", default=False,
                        help="if status of patient is inactive",
                        dest="inactive")

        parser.add_option("-o", "--office", "--dentaloffice", action="store",
                        type="string", dest="office_id",
                        help="add, and get id, with add/list_dental_office")

        parser.add_option("-u", "--user", action="store", type="string",
                        help="Dentist'id who takes care of this patient",
                        dest="dentist_id")

        parser.add_option("-d", "--doctor", action="store", type="string",
                        help="add, and get id, with add/list_MD.py",
                        dest="gen_doc_id")

        parser.add_option("--date", "--time_stamp", action="store",
                        type="string", dest="time_stamp",
                        help="patient's file creation, default=now")

        parser.add_option("--phonename", action="store", type="string",
                        help="Name of the phone (cellular...)",
                        dest="phone_name")

        parser.add_option("--phonenum", action="store", type="string",
                        help="Phone of the generalist doctor.",
                        dest="phone_num")

        parser.add_option("--mail", action="store", type="string",
                        help="Email address of the generalist doctor.",
                        dest="email")

        parser.add_option("--nopayer", action="store_false", default=True,
                        help="Is the patient payer for family",
                        dest="payer")

        parser.add_option("--family_id", action="store", type="string",
                        help="family id in DB from the person",
                        dest="family_id")

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

        parser.add_option("--socialsecuritynum", action="store", type="string",
                        help="social security number",
                        dest="socialsecuritynum")

        parser.add_option("--cmu", action="store_true", default=False,
                        help="the patient has cmu",
                        dest="cmu")

        parser.add_option("--insurance", action="store", type="string",
                        help="name of the patient's insurance",
                        dest="insurance")

        (options,args) = parser.parse_args(args)
        return options, args

class AddPatientCommand(BaseCommand, PatientParser):
    """ """
    
    command_name = "add_patient"

    def __init__(self):
        self.values = {}

    def run(self, args):

        (options, args) = self.parse_args(args)

        if not options.lastname:
            sys.exit("a lastname must be provide to add a new patient to\
                                                                    database")

        # Insering patient's name
        self.values["lastname"] = options.lastname.decode("utf_8").upper()
        if options.title:
            self.values["title"] = options.title.decode("utf_8").title()
        if options.firstname:
            self.values["firstname"] = options.firstname\
                                       .decode("utf_8").title()
        if options.qualification:
            self.values["qualification"] = options.qualification\
                                           .decode("utf_8").title()
        if options.preferred_name:
            self.values["preferred_name"] = options.preferred_name\
                                            .decode("utf_8").upper()
        if options.correspondence_name:
            self.values["correspondence_name"] = options.correspondence_name\
                                                 .decode("utf_8").upper()

        # patient's caracteristics
        if options.sex is "1" or options.sex is "M" or options.sex is "m":
            self.values["sex"] = True
        else:
            self.values["sex"] = False
        if options.dob:
            self.values["dob"] = options.dob
        if options.job:
            self.values["job"] = options.job.decode("utf_8")

        # The patient is a patient that may be seen
        if options.inactive:
            self.values["inactive"] = True

        # The dentist, the office... where the patient is actually treated.
        if options.office_id:
            self.values["office_id"] = options.office_id
        self.values["dentist_id"] = options.dentist_id
        if options.gen_doc_id:
            self.values["gen_doc_id"] = options.gen_doc_id

        # Last time the patient data were updated
        if options.time_stamp:
            self.values["time_stamp"] = options.time_stamp
            self.values["creation_date"] = options.time_stamp

        # The family the patient's belong to
        if options.family_id:
            self.values["family_id"] = options.family_id

        # A family have already an address ; if not in family, create a family 
        # with its own address.
        else:
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

        # Adding the new patient.
        new_patient = administration.Patient(**self.values)
        meta.session.add(new_patient)
        meta.session.commit()

        # Dealing with the patient's family :
        # If doesn't belong to already know family, create a family and its
        # address.
        if not options.family_id:
            family = administration.Family()
            meta.session.add(family)
            meta.session.commit()
            new_patient.family_id = family.id
            meta.session.commit()

            new_patient.family.addresses.append(administration.Address(
                        street = options.street,
                        building = options.building,
                        city = options.city,
                        postal_code = options.postal_code,
                        county = options.county,
                        country = options.country,
                        update_date = options.update_date
                        ))
            meta.session.commit()

        # Now, we have to tell if the patient may pay for himself and his 
        # family.
        if options.payer:
            payer_values = {}
            payer_values["patient_id"] = new_patient.id
            payer = administration.Payer(**payer_values)
            meta.session.add(payer)
            new_patient.family.payers.append(payer)
            meta.session.commit()

        # Patient's phone number
        if options.phone_num:
            if not options.phone_name:
                options.phone_name = "default"
            new_patient.phones.append(administration.Phone(
                            name = options.phone_name.decode("utf_8"),
                            number = options.phone_num.decode("utf_8")
                            ))

        # Patient's email
        if options.email:
            new_patient.mails.append(administration.Mail(
                            email = options.email
                            ))

        # Patient's social security :
        SSN_values = {}
        if options.socialsecuritynum:
            try:
                SSN_id =\
                meta.session.query(SocialSecurityLocale)\
                    .filter(SocialSecurityLocale.number ==
                            options.socialsecuritynum).one().id
                new_patient.socialsecurity_id = SSN_id

            except sqlalchemy.orm.exc.NoResultFound:
                SSN_values["number"] = options.socialsecuritynum
                if options.cmu:
                    SSN_values["cmu"] = options.cmu
                if options.insurance:
                    SSN_values["insurance"] = options.insurance.decode("utf_8")
                socialsecurity = SocialSecurityLocale(**SSN_values)
                meta.session.add(socialsecurity)
                meta.session.commit()
                new_patient.socialsecurity_id = socialsecurity.id
            
        else:
            SSN_values["number"] = None
            if options.cmu:
                SSN_values["cmu"] = options.cmu
            if options.insurance:
                SSN_values["insurance"] = options.insurance.decode("utf_8")
            socialsecurity = SocialSecurityLocale(**SSN_values)
            meta.session.add(socialsecurity)
            meta.session.commit()
            new_patient.socialsecurity_id = socialsecurity.id

        meta.session.commit()

        if GNUCASH_ACCOUNT:
            comptability = GnuCashCustomer(new_patient.id)
            new_customer = comptability.add_customer()
       
#        print(new_patient.id)
        sys.exit(new_patient.id)

class PatientMovingInCommand(BaseCommand):
    """
    When the user moves (used mainly for dentists who make replacements...)
    """

    command_name = "patient_movingin"

    def __init__(self):
        pass

    def parse_args(self, args):

        parser = self.get_parser()

        parser.add_option("--patient_id", action="store", type="string",
                        help="Id of user we want to change/update address",
                        dest="patient_id")
        
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

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)

        sys.exit(_("""Need to upgrade this method with the family ; the 
        movin_in will depend wether all the family is moving, or the
        patient is starting a new family, quitting his parents"""))

    
        if options.patient_id:
            patient_id = options.patient_id
        else:
            patient_id = os.getenv("patient_id")

        patient = meta.session.query(administration.Patient)\
                     .filter(administration.Patient.id ==
                     patient_id).one()

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
            for addr in patient.addresses:
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
            patient.addresses.append(administration.Address(
                                            street = options.street,
                                            building = options.building,
                                            city = options.city,
                                            postal_code = options.postal_code,
                                            county = options.county,
                                            country = options.country,
                                            update_date = options.update_date
                                            ))
        meta.session.commit()

        if GNUCASH_ACCOUNT:
            comptability = GnuCashCustomer(patient.id)
            customer = comptability.update_customer()


class ListPatientCommand(BaseCommand, PatientParser):
    """
    ./list_patient.py keyword1 keyword2
    will search for patient which lastname or firstname contains keyword
    """

    command_name = "list_patient"

    def __init__(self):
        self.query = meta.session.query(administration.Patient)
        self.querydoc = meta.session.query(md.MedecineDoctor)

    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--id", action="store_true", dest="patient_id",
                        help="Used this options to get only the patient id")
        
        parser.add_option("--inactive", action="store_true", default=False,
                        help="Use this option to look into inactive patients",
                        dest="inactive")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):

        (options, args) = self.parse_args(args)
        
        query = self.query
        
        for keyword in args:
            keyword = '%{}%'.format(keyword)
            query = query.filter(or_(
                    administration.Patient.lastname.ilike(keyword),
                    administration.Patient.firstname.ilike(keyword),
                    administration.Patient.preferred_name.ilike(keyword),
                    administration.Patient.correspondence_name.ilike(keyword)
                    ))
        
        if not options.inactive:
            query = query.filter(administration.Patient.inactive == False)

        # print result

        if options.patient_id:
            patient = query.one()
            print(_(u"{}".format(patient.id)))

        else:
            for patient in query:
                doc = self.querydoc.filter(md.MedecineDoctor.id ==
                                           patient.gen_doc_id).first()
                if patient.sex:
                    sex=_("M")
                else:
                    sex=_("F")

                print(_(u"{}. {} {} {}, {}\t{} ({} {})\t{} : {} {} {}\t{} {}"
                        .format(patient.id, patient.title, patient.lastname,
                        patient.firstname, sex, patient.dob, patient.age(),
                        _("years old"), _("Medecine Doctor"), _("Dr"),
                        doc.lastname, doc.firstname, _("inactive"), 
                        patient.inactive)))


class UpdatePatientCommand(BaseCommand, PatientParser):
    """ """
    
    command_name = "update_patient"

    def __init__(self):
        self.query = meta.session.query(administration.Patient)

    def run(self, args):

        (options, args) = self.parse_args(args, True)

        if not options.patient_id:
            sys.exit("the patient's id must be provide to update the database")

        patient = self.query.filter(administration.Patient.id == 
                                    options.patient_id).one()
        if options.lastname:
            patient.lastname = options.lastname.decode("utf_8").upper()
        if options.title:
            patient.title = options.title.decode("utf_8").title()
        if options.firstname:
            patient.firstname = options.firstname\
                                       .decode("utf_8").title()
        if options.qualification:
            patient.qualification = options.qualification\
                                           .decode("utf_8").title()
        if options.preferred_name:
            patient.preferred_name = options.preferred_name\
                                            .decode("utf_8").upper()
        if options.correspondence_name:
            patient.correspondence_name = options.correspondence_name\
                                                 .decode("utf_8").upper()
        if options.sex is "1" or options.sex is "M" or options.sex is "m":
            patient.sex = True
        else:
            patient.sex = False
        if options.dob:
            patient.dob = options.dob
        if options.job:
            patient.job = options.job.decode("utf_8")
        if options.phone_num:
            patient.phone_num = options.phone_num.decode("utf_8")
        if options.email:
            patient.email = options.email.decode("utf_8")
        if options.inactive:
            patient.inactive = True
        if options.office_id:
            patient.office_id = options.office_id
        if options.dentist_id:
            patient.dentist_id = options.dentist_id
        if options.gen_doc_id:
            patient.gen_doc_id = options.gen_doc_id
        if options.time_stamp:
            patient.time_stamp = options.time_stamp

        meta.session.commit()

        if GNUCASH_ACCOUNT:
            comptability = GnuCashCustomer(patient.id)
            customer = comptability.update_customer()


class AddPatientPhoneCommand(BaseCommand):
    pass

class UpdatePatientPhoneCommand(BaseCommand):
    pass
