# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/11/30
# v0.5
# Licence BSD
#

import pdb


from models import meta, administration, users, compta, schedule
import constants

from gettext import gettext as _

import ConfigParser

from decimal import Decimal
import os
import datetime


import gnucash
from gnucash import Session as GCSession, GUID
from gnucash import GncNumeric
from gnucash import gnucash_core_c as gnc_core_c
from gnucash.gnucash_business import Customer, Address, Invoice, Entry

class GnuCash():
    """ 

    In "/home/user/.odontuxrc" lies the odontux configuration, that tells
    about gnucash.
    
    In order that several dentists may use odontux together, the 
    "profissionnalaccounting_url", which specify the gnucash account place is 
    store in the user (ROLE_DENTIST) session :
    "models.users.OdontuxUser.profissionnalaccounting_url".
    
    The inside of gnucash needs at least :
        * assets  ( all of the dentist assets )
            * receivables  ( what the patient owes to the dentist )
            * dentalfund  ( what the patient paid to the dentist, but ain't 
                            usable right away ; needs to pass by the bank )
        * incomes  ( all of the dentist incomes )
            * dentalincomes  ( incomes coming from dental practice activity )

    While coding the assistant/secretary salary, the buying of dental supplies
    and all, we'll add "outcomes", liabilities...

    See commands/compta.py for :
        * assets
            * dentalfund
            * check
            * cash
            * card
            * transfer
            * paypal
    """
    def __init__(self, patient_id, dentist_id):
        self.parser = ConfigParser.ConfigParser()
        home = os.path.expanduser("~")
        self.parser.read(os.path.join(home, ".odontuxrc"))
        profissionnalaccounting_url = ( meta.session.query(users.OdontuxUser)
            .filter(users.OdontuxUser.id == dentist_id).one().gnucash_url
            .encode("utf_8") )
        if profissionnalaccounting_url.split(".")[-1] == "xml":
            self.gnucashtype = "xml"
        elif "postgresql" in profissionnalaccounting_url.split("://"):
            self.gnucashtype = "postgresql"
        else:
            self.gnucashtype = "xml"
        assets = self.parser.get("gnucashdb", "assets")
        receivables = self.parser.get("gnucashdb", "receivables")
        dentalfund = self.parser.get("gnucashdb", "dentalfund")
        incomes = self.parser.get("gnucashdb", "incomes")
        dentalincomes = self.parser.get("gnucashdb", "dentalincomes")

        # Precise on which patient we'll work on
        self.patient_id = patient_id
        self.patient = meta.session.query(administration.Patient).filter(
                                administration.Patient.id == patient_id).one()

        # Set the gnucash patient_id
        self.gcpatient_id = "pat_" + str(self.patient_id)
        # Set up the Book for accounting
        self.gcsession = GCSession(profissionnalaccounting_url, True)
        self.book = self.gcsession.get_book()

        # Set up the root on accounting book
        self.root = self.book.get_root_account()
        # Assets
        self.assets = self.root.lookup_by_name(assets)
        # What the patient owes to dental office
        self.receivables = self.assets.lookup_by_name(receivables)
        # What the patient paid to dental office, but not usable
        # because it needs to pass by the bank.
        # the detail of dental fund is build in commands/compta.py
        # while getting the paymenttype.
        self.dentalfund = self.assets.lookup_by_name(dentalfund)

        # Incomes
        self.incomes = self.root.lookup_by_name(incomes)
        self.dentalincomes = self.incomes.lookup_by_name(dentalincomes)

        # set the currency we'll use
        currency = self.parser.get("gnucashdb", "currency")
        commod_tab = self.book.get_table()
        self.currency = commod_tab.lookup("CURRENCY", currency)

    def gnc_numeric_from_decimal(self, decimal_value):
        sign, digits, exponent = decimal_value.as_tuple()

        # convert decimal digits to a fractional numerator
        # equivlent to
        # numerator = int(''.join(digits))
        # but without the wated conversion to string and back,
        # this is probably the same algorithm int() uses
        numerator = 0
        TEN = int(Decimal(0).radix()) # this is always 10
        numerator_place_value = 1
        # add each digit to the final value multiplied by the place value
        # from least significant to most sigificant
        for i in xrange(len(digits)-1,-1,-1):
            numerator += digits[i] * numerator_place_value
            numerator_place_value *= TEN

        if decimal_value.is_signed():
            numerator = -numerator

        # if the exponent is negative, we use it to set the denominator
        if exponent < 0 :
            denominator = TEN ** (-exponent)
        # if the exponent isn't negative, we bump up the numerator
        # and set the denominator to 1
        else:
            numerator *= TEN ** exponent
            denominator = 1

        return GncNumeric(numerator, denominator)

class GnuCashCustomer(GnuCash):
    """
    This class is meant to manage "Customers" informations in gnucash.
    Each patient is a gnucash_Customer.
    So, when we add a new patient to odontux_database, we have to add this 
    patient to the gnucash database.
    Please remember that when the patient changes of dentist, we have to add 
    a new Customer in gnucash, as each dentist possesses his own 
    gnucash_session.
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
        if self.gnucashtype == "xml":
            self.gcsession.save()
        return new_customer, name

    def _update_name(self):
        """return customer instance, and his name"""
        name = self.patient.title + " " + self.patient.lastname + " " \
               + self.patient.firstname
        customer = self.book.CustomerLookupByID(self.gcpatient_id)
        customer.SetName(name.encode("utf_8"))
        if self.gnucashtype == "xml":
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
        if self.patient.family.addresses:
            if self.patient.family.addresses[-1].street:
                address.SetAddr1(self.patient.family.addresses[-1]
                                .street.encode("utf_8"))
            if self.patient.family.addresses[-1].building:
                address.SetAddr2(self.patient.family.addresses[-1]
                                .building.encode("utf_8"))
            zip_code = ""
            city = ""
            if self.patient.family.addresses[-1].zip_code:
                zip_code = self.patient.family.addresses[-1]\
                            .zip_code.encode("utf_8")
            if self.patient.family.addresses[-1].city:
                city = self.patient.family.addresses[-1].city.encode("utf_8")
            address.SetAddr3(zip_code  + " " + city)
            county = ""
            country = ""
            if self.patient.family.addresses[-1].county:
                county = self.patient.family.addresses[-1].county.encode("utf_8")
            if self.patient.family.addresses[-1].country:
                country = self.patient.family.addresses[-1].country.encode("utf_8")
            address.SetAddr4(county + " " + country)
            #if self.gnucashtype == "xml":
            #    self.gcsession.save()

    def add_customer(self):
        try:
            if self._test_id_already_in_database():
                self.update_customer()
                return True
            (new_customer, name) = self._set_name()
            self._set_address(new_customer, name)
            self.gcsession.end()
            return True
        except:
            self.gcsession.end()
            raise
            return False
    def update_customer(self):
        try:
            if not self._test_id_already_in_database():
                self.add_customer()
                return True
            (customer, name) = self._update_name()
            self._set_address(customer, name)
            self.gcsession.end()
            return True
        except:
            self.gcsession.end()
            raise
            return False

class GnuCashInvoice(GnuCash):
    """ 
    The GnuCashInvoice deals with gnucash to enter act and price in an Invoice.
    As it hasn't been cashed, but that the act "is sold", it will be stocked
    in an "Receivable Account".
    An individual invoice will contain every act made on a unique patient
    during an unique appointment.
    """
    def __init__(self, patient_id, appointment_id, dentist_id, invoice_id=""):
        # Initialize the self.vars from Parent : GnuCash
        #   * self.gcsession
        #   * self.book
        #   * self.root, self.assets, self.receivables, self.incomes, 
        #   self.dentalincomes
        #   * self.gcpatient and self.patient
        #   * self.currency
        patient = meta.session.query(administration.Patient).filter(
                                administration.Patient.id == patient_id).one()
        # If it's a dentist who is entering an act in database, we assume he
        # did the gesture. Otherwise, if nurse, secretary (...) enters the act
        # in database, we assume the patient's official dentist made it.
        if not dentist_id:
            dentist_id = patient.dentist_id
        GnuCash.__init__(self, patient.id, dentist_id)
        # get the patient (customer) instance from gnucash database
        self.owner = self.book.CustomerLookupByID(self.gcpatient_id)
        # invoice_id is build as
        # Date + appointment_id
        self.date = (
            meta.session.query(schedule.Appointment)
                .filter(schedule.Appointment.id ==appointment_id)
                .one().agenda.endtime.date()
            )

        if not invoice_id:
            self.invoice_id = "inv_" + self.date.isoformat() + "_" +\
                                                            str(appointment_id)
        else:
            self.invoice_id = invoice_id

    def _create_invoice_instance(self):
        return Invoice(self.book, self.invoice_id, self.currency, 
                       self.owner, self.date)
        
    def add_act(self, code, price, act_id):
        # Get an instance for the invoice
        try:
            if self.book.InvoiceLookupByID(self.invoice_id):
                invoice = self.book.InvoiceLookupByID(self.invoice_id)
                invoice.Unpost(True)
                invoice.BeginEdit()
            else:
                invoice = self._create_invoice_instance()
                invoice.BeginEdit()

            description = str(act_id) + "_" + code
            invoice_value = self.gnc_numeric_from_decimal(Decimal(price))
            invoice_entry = Entry(self.book, invoice)
            invoice_entry.BeginEdit()
            invoice_entry.SetDescription(description.encode("utf_8"))
            invoice_entry.SetQuantity( GncNumeric(1) )
            invoice_entry.SetInvAccount(self.dentalincomes)
            invoice_entry.SetInvPrice(invoice_value)
            invoice_entry.CommitEdit()
            invoice.CommitEdit()
            invoice.PostToAccount(self.receivables, self.date, self.date,
                                    description.encode("utf_8"), True, False)
            self.gcsession.save()
            self.gcsession.end()
            return self.invoice_id
            
        except:
            self.gcsession.end()
            raise
            return False

    def remove_act(self, code, act_id):
        try:
            if self.book.InvoiceLookupByID(self.invoice_id):
                invoice = self.book.InvoiceLookupByID(self.invoice_id)
            else:
                raise Exception(_("invoice_id doesn't fit"))

            description = str(act_id) + "_" + code
            number_of_entries = len(invoice.GetEntries())
            
            for entry in invoice.GetEntries():
                if entry.GetDescription() == description:
                    if number_of_entries > 1 :
                        invoice.Unpost(True)
                        invoice.BeginEdit()
                        gnc_core_c.gncEntryBeginEdit(entry)
#                        gnc_core_c.gncInvoiceRemoveEntry(invoice, entry)
                        invoice.RemoveEntry(entry)
                        invoice.CommitEdit()
                        invoice.PostToAccount(self.receivables, self.date, 
                                            self.date, 
                                            description.encode("utf_8"),
                                            True, False)
                        self.gcsession.save()
                        self.gcsession.end()
                        return True
                    if number_of_entries == 1:
                        invoice.Unpost(True)
                        invoice.Destroy()
                        self.gcsession.save()
                        self.gcsession.end()
                        return True
            return False

        except:
            self.gcsession.end()
            raise
            return False

class GnuCashPayment(GnuCash):
    """ GnuCashPayment tries to 
    """
    def _get_payer(self, gcpayer_id):
        return self.book.CustomerLookupByID(gcpayer_id)

    def _get_paymenttype(self, mean_id):
        mean = meta.session.query(compta.PaymentType)\
               .filter(compta.PaymentType.id == mean_id).one()
        
        paymenttype = self.parser.get("gnucashdb", mean.name)
        return self.dentalfund.lookup_by_name(paymenttype)
            
    def add_payment(self, mean_id, amount, date):
        try:
            payer = self._get_payer(self.gcpatient_id)
            dest_account = self._get_paymenttype(mean_id)
            amount = self.gnc_numeric_from_decimal(amount)

#            invoices_list = []
#            for invoice_id in invoices_id:
#                invoices_list.append(self.book.InvoiceLookupByID(invoice_id))
                
#            payer.ApplyPayment(invoice=None, None, account=self.receivables, 
#                           dest_account, 
#                            amount, exch=GncNumeric(1), date, memo="", num="",
#                            autopay=False)
            payer.ApplyPayment(None, None, self.receivables, dest_account, 
                            amount, GncNumeric(1), date, "", "", False)
            
            if self.gnucashtype == "xml":
                self.gcsession.save()
            self.gcsession.end()
            return True
        except:
            self.gcsession.end()
            raise
