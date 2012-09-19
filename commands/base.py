# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#

import ConfigParser
from optparse import OptionParser

class BaseCommand():
    
    def get_parser(self):
        return OptionParser(usage="%prog {}".format(self.command_name))

class GnuCash():
    """ """
    def __init__(self, id):
        parser = ConfigParser.ConfigParser()
        home = os.path.expanduser("~")
        parser.read(os.path.join(home, ".odontuxrc"))
        professionnalaccounting_url = parser.get("gnucashdb", "url")

        # Precise on which patient we'll work on
        self.id = id
        self.patient = meta.session.query(administration.Patient)\
                        .filter(administration.Patient.id == id).one()

        # Set up the Book for accounting
        self.gcsession = Session(professionnalaccounting_url, True)
        self.book = self.gcsession.get_book()

        # set the currency we'll use
        currency = parser.get("gnucashdb", "currency")
        commod_tab = book.get_table()
        self.currency = commod_tab.lookup("CURRENCY", currency)


