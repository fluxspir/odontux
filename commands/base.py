# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/26
# v0.4
# Licence BSD
#


from optparse import OptionParser

class BaseCommand():
    
    def get_parser(self):
        return OptionParser(usage="%prog {}".format(self.command_name))
