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
        print(professionnalaccounting_url)

        # Precise on which patient we'll work on
        self.patient_id = patient_id
        self.patient = meta.session.query(administration.Patient)\
                        .filter(administration.Patient.id == patient_id).one()

        # Set the gnucash patient_id
        self.gcpatient_id = "patient_" + str(self.patient_id)

        # Set up the Book for accounting
        self.gcsession = GCSession(professionnalaccounting_url, True)
        self.book = self.gcsession.get_book()

        # set the currency we'll use
        currency = parser.get("gnucashdb", "currency")
        commod_tab = self.book.get_table()
        self.currency = commod_tab.lookup("CURRENCY", currency)
