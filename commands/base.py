# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

from model import meta, administration

import ConfigParser
from optparse import OptionParser

import os

try:
    import gnucash
    from gnucash import Session as GCSession
    from gnucash.gnucash_business import Customer
except ImportError:
    pass

class BaseCommand():
    
    def get_parser(self):
        return OptionParser(usage="%prog {}".format(self.command_name))

class GnuCash():
    """ """
    def __init__(self, patient_id):
        parser = ConfigParser.ConfigParser()
        home = os.path.expanduser("~")
        parser.read(os.path.join(home, ".odontuxrc"))
        professionnalaccounting_url = parser.get("gnucashdb", "url")
        assets = parser.get("gnucashdb", "assets")
        receivables = parser.get("gnucashdb", "receivables")
        incomes = parser.get("gnucashdb", "incomes")
        dentalincomes = parser.get("gnucashdb", "dentalincomes")

        # Precise on which patient we'll work on
        self.patient_id = patient_id
        self.patient = meta.session.query(administration.Patient)\
                        .filter(administration.Patient.id == patient_id).one()

        # Set the gnucash patient_id
        self.gcpatient_id = "pat_" + str(self.patient_id)

        # Set up the Book for accounting
        self.gcsession = GCSession(professionnalaccounting_url, True)
        self.book = self.gcsession.get_book()

        # Set up the root on accounting book
        self.root = self.book.get_root_account()
        self.assets = self.root.lookup_by_name(assets)
        self.receivables = self.assets.lookup_by_name(receivables)
        self.incomes = self.root.lookup_by_name(incomes)
        self.dentalincomes = self.incomes.lookup_by_name(dentalincomes)

        # set the currency we'll use
        currency = parser.get("gnucashdb", "currency")
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
