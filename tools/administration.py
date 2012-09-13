# -*- coding: utf-8 -*-
# Franck Labadille
# 2012/08/27
# v0.4
# Licence BSD
#

from model import meta, administration
from base import BaseCommand

from gettext import gettext as _
from sqlalchemy import or_, and_
import os
import sys



class ListFamilyTool(BaseCommand):
    """ """
    tool_name = "list_family"

    def __init__(self):
        self.query = meta.session.query(administration.Family)
    
    def parse_args(self, args):
        parser = self.get_parser()

        parser.add_option("--id", action="store_true", default=False,
                        help="to get the family id",
                        dest="family_id")

        (options, args) = parser.parse_args(args)
        return options, args

    def run(self, args):
        (options, args) = self.parse_args(args)

## REPLACE BY   list_patient -i
#
#class GetPatientIdTool(BaseCommand):
#    """ """
#
#    tool_name = "get_patientid"
#
#    def __init__(self):
#        self.query = meta.session.query(administration.Patient)
#
#    def run(self, args):
#        query = self.query
#        for keyword in args:
#            keyword = "%{}%".format(keyword)
#            query = query.filter(or_(
#                    administration.Patient.lastname.ilike(keyword),
#                    administration.Patient.firstname.ilike(keyword),
#                    administration.Patient.preferred_name.ilike(keyword),
#                    administration.Patient.correspondence_name.ilike(keyword))
#                    )
#        query = query.one()            
#        print(query.id)
