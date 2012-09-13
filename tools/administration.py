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



class GetFamilyIdTool(BaseCommand):
    """ 
    prints the id of the family for a patient.
    """
    tool_name = "get_familyid"

    def __init__(self):
        self.query = meta.session.query(administration.Patient)
    
    def run(self, args):
        query = self.query
        for keyword in args:
            keyword = "%{}%".format(keyword)
            query = meta.session.query(administration.Patient).filter(or_(
                    administration.Patient.lastname.ilike(keyword),
                    administration.Patient.firstname.ilike(keyword),
                    administration.Patient.preferred_name.ilike(keyword),
                    administration.Patient.correspondence_name.ilike(keyword))
                    )
        
#        try:
        family_id = query.one().family_id
        print(family_id)
#        except ???:
#        for patient in query.all():
#           print .....


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
